import contextlib
import errno
import logging
import os
import pathlib
import platform
import re
import select
import shlex
import shutil
import signal
import subprocess
import time

import magpie

from .abstract_execmanager import AbstractExecManager
from .basic_variant import BasicVariant
from .execresult import ExecResult
from .runresult import RunResult


class BasicExecManager(AbstractExecManager):
    def __init__(self, software):
        self.software = software
        self.unix_timestamp = 0
        self.work_dir = None
        self.env_counter = None
        self.env_patch = None
        self.run_label = None

    def setup(self):
        self.reset_timestamp()
        self.reset_workdir()
        self.reset_logger()
        self.reset_contents()

    def reset(self):
        pass

    def reset_timestamp(self):
        # ensures a unique timestamp
        self.unix_timestamp = int(time.time())
        with contextlib.suppress(FileExistsError):
            pathlib.Path(magpie.settings.work_dir).mkdir(parents=True)
        while True:
            local_time = time.strftime('%Y%m%d', time.localtime(self.unix_timestamp))
            self.run_label = f'{self.software.basename}_{local_time}_{self.unix_timestamp}'
            new_work_dir = self.base_work_path()
            lock_file = f'{new_work_dir}.lock'
            try:
                fd = os.open(lock_file, os.O_CREAT | os.O_EXCL)
                os.close(fd)
                try:
                    new_work_dir.mkdir()
                    new_work_dir.rmdir()
                    break
                except FileExistsError:
                    pathlib.Path(lock_file).unlink()
            except FileExistsError:
                pass
            self.unix_timestamp += 1

    def reset_workdir(self):
        # creates or move current work_dir
        new_work_dir = self.base_work_path()
        if self.work_dir and self.work_dir.exists():
            self.work_dir = pathlib.Path(shutil.move(self.work_dir, new_work_dir))
            if magpie.settings.local_original_copy:
                self.software.path = self.work_dir / magpie.settings.local_original_name
        else:
            self.work_dir = new_work_dir
            if magpie.settings.local_original_copy:
                new_path = self.work_dir / magpie.settings.local_original_name
                if self.software.path != new_path:
                    self.software.path = shutil.copytree(self.software.path, new_path)
        pathlib.Path(f'{new_work_dir}.lock').unlink()

    def reset_contents(self):
        if not self.software.init_performed:
            self.software.init_performed = True
            if self.software.init_cmd:
                with contextlib.chdir(self.software.path):
                    timeout = self.software.init_timeout or magpie.settings.default_timeout
                    lengthout = self.software.init_lengthout or magpie.settings.default_lengthout
                    exec_result = self.exec_cmd(shlex.split(self.software.init_cmd),
                                                timeout=timeout,
                                                lengthout=lengthout)
                    run_result = RunResult(None, exec_result.status)
                    if run_result.status == 'SUCCESS':
                        for fit in self.software.fitness_objectives.values():
                            fit.process_init_exec(run_result, exec_result)
                    if run_result.status != 'SUCCESS':
                        run_result.status = f'INIT_{run_result.status}'
                        run_result.last_exec = exec_result
                        self.diagnose_error(run_result)
                        msg = '(cmd_init) failed to init target software'
                        raise RuntimeError(msg)

        # expend wildcards in target file list
        if any('*' in f for f in self.software.target_files):
            tmp = [sorted(self.software.path.glob(f)) if '*' in f else [f] for f in self.software.target_files]
            self.software.target_files = [str(f.relative_to(self.software.path)) for fl in tmp for f in fl]
        if any('*' in f for f in self.software.ingredient_files):
            tmp = [sorted(self.software.path.glob(f)) if '*' in f else [f] for f in self.software.ingredient_files]
            self.software.ingredient_files = [str(f.relative_to(self.software.path)) for fl in tmp for f in fl]
        self.software.ingredient_files = [f for f in self.software.ingredient_files if f not in self.software.target_files]

        # reset noop variant
        self.software.noop_variant = BasicVariant(self.software)

    def reset_logger(self):
        # create logger
        logger = logging.getLogger(self.run_label)
        logger.handlers.clear()
        logger.setLevel(logging.DEBUG)

        # add stream handler
        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(logging.INFO)
        logger.addHandler(stream_handler)

        # to remove ANSI color tags in file logs
        def color_stripper(record):
            if isinstance(record.msg, str):
                record.msg = re.sub(r'\033\[[0-9;]*m', '', record.msg)
            if isinstance(record.args, tuple):
                record.args = tuple(
                    re.sub(r'\033\[[0-9;]*m', '', arg) if isinstance(arg, str) else arg
                    for arg in record.args)
            return True

        # add file logging
        with contextlib.suppress(FileExistsError):
            pathlib.Path(magpie.settings.log_dir).mkdir(parents=True)
        file_handler = logging.FileHandler(f'{self.base_log_path()}.log', delay=True)
        file_handler.setFormatter(logging.Formatter('%(asctime)s\t[%(levelname)s]\t%(message)s'))
        file_handler.setLevel(logging.DEBUG)
        file_handler.addFilter(color_stripper)
        logger.addHandler(file_handler)

        # save logger
        self.software.logger = logger

    def base_log_path(self):
        return pathlib.Path(magpie.settings.log_dir).resolve() / self.run_label

    def base_work_path(self):
        return pathlib.Path(magpie.settings.work_dir).resolve() / self.run_label

    def variant_work_path(self, variant):
        return self.base_work_path() / self.software.basename # always the same for now

    def write_variant(self, variant):
        # reset work directory
        work_path = self.work_dir / self.software.basename
        self.sync_folder(work_path, self.software.path)

        # process modified files
        with contextlib.chdir(work_path):
            for filename in self.software.target_files:
                variant.models[filename].write_to_file()

    def sync_folder(self, target, original):
        try:
            contents_target = os.listdir(target)
        except FileNotFoundError:
            shutil.copytree(original, target)
            return
        contents_original = os.listdir(original)
        for entry in contents_target:
            target_entry = target / entry
            if target_entry.is_dir():
                if entry not in contents_original:
                    # new directory
                    shutil.rmtree(target_entry)
                # else: common directory
            elif entry not in contents_original:
                # new file
                target_entry.unlink()
            else:
                original_entry = original / entry
                if original_entry.stat().st_mtime < target_entry.stat().st_mtime:
                    # modified file
                    shutil.copyfile(original_entry, target_entry)
                    shutil.copystat(original_entry, target_entry)
            # else: unmodified file
        for entry in contents_original:
            target_entry = target / entry
            original_entry = original / entry
            if original_entry.is_dir():
                if entry in contents_target:
                    # recursion
                    self.sync_folder(target_entry, original_entry)
                else:
                    # deleted directory (?)
                    shutil.copytree(original_entry, target_entry)
            elif entry not in contents_target:
                # deleted file
                shutil.copyfile(original_entry, target_entry)
            # else: appears in both (already handled)

    @contextlib.contextmanager
    def add_to_env(self, counter=None, patch=None):
        try:
            self.env_counter = str(counter or '')
            self.env_patch = str(patch or '')
            yield
        finally:
            self.env_counter = None
            self.env_patch = None

    def exec_cmd(self, cmd, timeout=15, env=None, shell=False, lengthout=1e6):
        # 1e6 bytes is 1Mb
        sprocess = None
        stdout = b''
        stderr = b''
        start = time.time()
        sprocess = None
        env = env or os.environ.copy()
        env['MAGPIE_ROOT'] = magpie.settings.magpie_root
        env['MAGPIE_LOG_DIR'] = magpie.settings.log_dir
        env['MAGPIE_WORK_DIR'] = magpie.settings.work_dir
        env['MAGPIE_BASENAME'] = self.software.basename
        env['MAGPIE_TIMESTAMP'] = str(self.unix_timestamp)
        env['MAGPIE_COUNTER'] = self.env_counter or ''
        env['MAGPIE_PATCH'] = self.env_patch or ''
        if magpie.settings.show_cmd_progress:
            display_str = '$ ' + ' '.join(cmd)
            display_length = magpie.settings.cmd_progress_maxlength
            tmp = display_str
            if len(tmp) > display_length:
                tmp = f'{display_str[:display_length-len(tmp)-5]}[...]'
            print(tmp, end='\r', flush=True)
        try:
            is_posix = os.name == 'posix'
            with subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=shell, env=env, start_new_session=is_posix) as sprocess:
                if lengthout > 0:
                    stdout_size = 0
                    stderr_size = 0
                    while sprocess.poll() is None:
                        end = time.time()
                        if end-start > timeout:
                            _kill_proc_with_children(sprocess)
                            return ExecResult(cmd, 'TIMEOUT', sprocess.returncode, stdout, stderr, end-start, stdout_size+stderr_size)
                        a = select.select([sprocess.stdout, sprocess.stderr], [], [], 1)[0]
                        if magpie.settings.show_cmd_progress:
                            display_time = f'({int(end-start)}s ago)'
                            tmp = f'{display_str} {display_time}'
                            if len(tmp) > display_length:
                                tmp = f'{display_str[:display_length-len(tmp)-5]}[...] {display_time}'
                            else:
                                tmp += (display_length-len(tmp))*' '
                            print(tmp, end='\r', flush=True)
                        if sprocess.stdout in a:
                            for _ in range(1024):
                                if not select.select([sprocess.stdout], [], [], 0)[0]:
                                    break
                                stdout += sprocess.stdout.read(1)
                                stdout_size += 1
                        if sprocess.stderr in a:
                            for _ in range(1024):
                                if not select.select([sprocess.stderr], [], [], 0)[0]:
                                    break
                                stderr += sprocess.stderr.read(1)
                                stderr_size += 1
                        if stdout_size+stderr_size >= lengthout:
                            _kill_proc_with_children(sprocess)
                            _, _ = sprocess.communicate()
                            return ExecResult(cmd, 'LENGTHOUT', sprocess.returncode, stdout, stderr, end-start, stdout_size+stderr_size)
                    end = time.time()
                    stdout += sprocess.stdout.read()
                    stderr += sprocess.stderr.read()
                else:
                    try:
                        stdout, stderr = sprocess.communicate(timeout=timeout)
                    except subprocess.TimeoutExpired:
                        _kill_proc_with_children(sprocess)
                        stdout, stderr = sprocess.communicate()
                        end = time.time()
                        return ExecResult(cmd, 'TIMEOUT', sprocess.returncode, stdout, stderr, end-start, len(stdout)+len(stderr))
                    end = time.time()
                return ExecResult(cmd, 'SUCCESS', sprocess.returncode, stdout, stderr, end-start, len(stdout)+len(stderr))
        except FileNotFoundError:
            return ExecResult(cmd, 'CLI_ERROR', -1, b'', b'', 0, 0)
        finally:
            if magpie.settings.show_cmd_progress:
                print(' '*display_length, end='\r', flush=True)

    def clean_work_dir(self):
        with contextlib.suppress(FileNotFoundError):
            shutil.rmtree(self.base_work_path())
        with contextlib.suppress(FileNotFoundError):
            try:
                pathlib.Path(magpie.settings.work_dir).rmdir()
            except OSError as e:
                if e.errno != errno.ENOTEMPTY:
                    raise

    def diagnose_error(self, run):
        logger = self.software.logger
        logger.info('!*'*40)
        logger.info('Unable to run and evaluate the target software.')
        logger.info('Self-diagnostic:')
        self.self_diagnostic(run)
        logger.info('!*'*40)
        if run.last_exec is not None:
            logger.info('CWD: %s', pathlib.Path(self.work_dir) / self.software.basename)
            logger.info('CMD: %s', run.last_exec.cmd)
            logger.info('STATUS: %s', run.last_exec.status)
            logger.info('RETURN_CODE: %s', run.last_exec.return_code)
            logger.info('RUNTIME: %s', run.last_exec.runtime)
            encoding = magpie.settings.output_encoding
            logger.info('STDOUT: (see log file)')
            try:
                s = run.last_exec.stdout.decode(encoding)
                logger.debug('STDOUT:\n%s', s)
            except UnicodeDecodeError:
                logger.debug('STDOUT: (failed to decode to: %s)\n%s', encoding, run.last_exec.stdout)
            logger.info('STDERR: (see log file)')
            try:
                s = run.last_exec.stderr.decode(encoding)
                logger.debug('STDERR:\n%s', s)
            except UnicodeDecodeError:
                logger.debug('STDERR: (failed to decode to: %s)\n%s', encoding, run.last_exec.stderr)
            logger.info('!*'*40)

    def self_diagnostic(self, run):
        logger = self.software.logger
        for step in ['init', 'setup', 'compile', 'test', 'run']:
            if run.status == f'{step.upper()}_CLI_ERROR':
                logger.info('Unable to run the "%s_cmd" command', step)
                logger.info('--> there might be a typo (try it manually)')
                logger.info('--> your command might not be found (check your PATH)')
                logger.info('--> it might not run from the correct directory (check CWD below)')
            if run.status == f'{step.upper()}_CODE_ERROR':
                logger.info('The "%s_cmd" command failed with a nonzero exit code', step)
                logger.info('--> try to run it manually')
            if run.status == f'{step.upper()}_PARSE_ERROR':
                logger.info('The "%s_cmd" STDOUT/STDERR was invalid', step)
                logger.info('--> try to run it manually')
            if run.status == f'{step.upper()}_TIMEOUT':
                logger.info('The "%s_cmd" command took too long to run', step)
                logger.info('--> consider increasing "%s_timeout"', step)
            if run.status == f'{step.upper()}_LENGTHOUT':
                logger.info('The "%s_cmd" command generated too much output', step)
                logger.info('--> consider increasing "%s_lengthout"', step)
        if run.status == 'BATCH_TIMEOUT':
            logger.info('Batch execution of "run_cmd" took too long to run')
            logger.info('--> consider increasing "batch_timeout"')
        if run.status == 'BATCH_LENGTHOUT':
            logger.info('Batch execution of "run_cmd" generated too much output')
            logger.info('--> consider increasing "batch_lengthout"')


if os.name == 'posix':
    def _kill_proc_with_children(proc):
        os.killpg(os.getpgid(proc.pid), signal.SIGKILL)
elif platform.system() == 'Windows':
    def _kill_proc_with_children(proc):
        subprocess.run(['taskkill', '/F', '/T', '/PID', str(proc.pid)], check=False)
else: # we probably shouldn't even support this
    def _kill_proc_with_children(proc):
        proc.kill() # hoping there aren't any child process
