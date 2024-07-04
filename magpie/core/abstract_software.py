import abc
import contextlib
import errno
import logging
import os
import pathlib
import platform
import re
import select
import shutil
import signal
import subprocess
import time

import magpie.settings

from .execresult import ExecResult
from .variant import Variant


class AbstractSoftware(abc.ABC):
    def __init__(self, path, reset=True):
        self.logger = None
        self.path = pathlib.Path(path.strip()).resolve()
        self.basename = self.path.name
        self.target_files = []
        self.noop_variant = None
        self.work_dir = None

        if reset:
            self.reset_timestamp()
            self.reset_logger()
            self.reset_workdir()
            self.reset_contents()

    def reset_timestamp(self):
        # ensures a unique timestamp unique
        self.timestamp = str(int(time.time()))
        with contextlib.suppress(FileExistsError):
            pathlib.Path(magpie.settings.work_dir).mkdir(parents=True)
        while True:
            self.run_label = f'{self.basename}_{self.timestamp}'
            new_work_dir = pathlib.Path(magpie.settings.work_dir).resolve() / self.run_label
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
            self.timestamp = str(int(self.timestamp)+1)

    def reset_logger(self):
        # just in case
        if self.logger:
            self.logger.handlers.clear()

        # create logger
        self.logger = logging.getLogger(self.run_label)
        self.logger.setLevel(logging.DEBUG)

        # add stream handler
        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(logging.INFO)
        self.logger.addHandler(stream_handler)

        # to remove ANSI color tags in file logs
        def color_stripper(record):
            if isinstance(record.msg, str):
                record.msg = re.sub(r'\033\[[0-9;]*m', '', record.msg)
            return True

        # add file logging
        with contextlib.suppress(FileExistsError):
            pathlib.Path(magpie.settings.log_dir).mkdir(parents=True)
        file_handler = logging.FileHandler((pathlib.Path(magpie.settings.log_dir) / f'{self.run_label}.log'), delay=True)
        file_handler.setFormatter(logging.Formatter('%(asctime)s\t[%(levelname)s]\t%(message)s'))
        file_handler.setLevel(logging.DEBUG)
        file_handler.addFilter(color_stripper)
        self.logger.addHandler(file_handler)


    def reset_workdir(self):
        # creates or move current work_dir
        new_work_dir = pathlib.Path(magpie.settings.work_dir).resolve() / self.run_label
        if self.work_dir and self.work_dir.exists():
            self.work_dir = pathlib.Path(shutil.move(self.work_dir, new_work_dir))
            if magpie.settings.local_original_copy:
                self.path = self.work_dir / magpie.settings.local_original_name
        else:
            self.work_dir = new_work_dir
            if magpie.settings.local_original_copy:
                new_path = self.work_dir / magpie.settings.local_original_name
                if self.path != new_path:
                    self.path = shutil.copytree(self.path, new_path)
        pathlib.Path(f'{new_work_dir}.lock').unlink()

    def reset_contents(self):
        # expend wildcards in target file list
        if any('*' in f for f in self.target_files):
            tmp = [sorted(self.path.glob(f)) if '*' in f else [f] for f in self.target_files]
            self.target_files = [str(f.relative_to(self.path)) for fl in tmp for f in fl]

        # reset noop variant
        self.noop_variant = Variant(self)

    @abc.abstractmethod
    def evaluate_variant(self, variant, cached_run=None):
        pass

    def write_variant(self, variant):
        # reset work directory
        work_path = self.work_dir / self.basename
        self.sync_folder(work_path, self.path)

        # process modified files
        with contextlib.chdir(work_path):
            for filename in self.target_files:
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
        env['MAGPIE_BASENAME'] = self.basename
        env['MAGPIE_TIMESTAMP'] = self.timestamp
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

    def clean_work_dir(self):
        with contextlib.suppress(FileNotFoundError):
            shutil.rmtree(self.work_dir)
        with contextlib.suppress(FileNotFoundError):
            try:
                pathlib.Path(magpie.settings.work_dir).rmdir()
            except OSError as e:
                if e.errno != errno.ENOTEMPTY:
                    raise

if os.name == 'posix':
    def _kill_proc_with_children(proc):
        os.killpg(os.getpgid(proc.pid), signal.SIGKILL)
elif platform.system() == 'Windows':
    def _kill_proc_with_children(proc):
        subprocess.run(['taskkill', '/F', '/T', '/PID', str(proc.pid)], check=False)
else: # we probably shouldn't even support this
    def _kill_proc_with_children(proc):
        proc.kill() # hoping there aren't any child process
