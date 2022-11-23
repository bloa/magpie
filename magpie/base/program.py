import os
import shutil
import time
import pathlib
import random
import collections
import subprocess
import shlex
import copy
import difflib
import select
import signal
import errno
import logging
import re

from .. import config as magpie_config
from .execresult import ExecResult
from .runresult import RunResult
from ..params import AbstractParamsEngine

class Program():
    def __init__(self, path):
        self.base_init(path)
        self.setup()
        self.reset_timestamp()
        self.reset_logger()
        self.reset_contents()

    def base_init(self, path):
        self.logger = None
        self.path = os.path.abspath(path.strip())
        self.basename = os.path.basename(self.path)
        self.target_files = []
        self.engines = {}
        self.contents = {}
        self.local_contents = {}
        self.locations = {}
        self.possible_edits = []
        self.work_dir = None
        self.compile_cmd = None
        self.compile_timeout = None
        self.compile_output = None
        self.test_cmd = None
        self.test_timeout = None
        self.test_output = None
        self.run_cmd = None
        self.run_timeout = None
        self.run_output = None
        self.last_cmd = '(not set)'
        self.last_stdout = '(not set)'
        self.last_stderr = '(not set)'

    def setup(self):
        pass

    def reset_timestamp(self):
        # ensures a unique timestamp unique
        self.timestamp = str(int(time.time()))
        try:
            os.makedirs(magpie_config.work_dir)
        except FileExistsError:
            pass
        while True:
            self.run_label = '{}_{}'.format(self.basename, self.timestamp)
            new_work_dir = os.path.join(os.path.abspath(magpie_config.work_dir), self.run_label)
            lock_file = '{}.lock'.format(new_work_dir)
            try:
                fd = os.open(lock_file, os.O_CREAT | os.O_EXCL)
                os.close(fd)
                try:
                    os.mkdir(new_work_dir)
                    os.rmdir(new_work_dir)
                    break
                except FileExistsError:
                    os.remove(lock_file)
            except FileExistsError:
                pass
            self.timestamp = str(int(self.timestamp)+1)

        # creates or move current work_dir
        if self.work_dir and os.path.exists(self.work_dir):
            self.work_dir = shutil.move(self.work_dir, new_work_dir)
            if magpie_config.local_original_copy:
                self.path = os.path.join(self.work_dir, magpie_config.local_original_name)
        else:
            self.work_dir = new_work_dir
            if magpie_config.local_original_copy:
                new_path = os.path.join(self.work_dir, magpie_config.local_original_name)
                if self.path != new_path:
                    self.path = shutil.copytree(self.path, new_path)
        os.remove(lock_file)

    def reset_logger(self):
        # just in case
        if self.logger:
            self.logger.handlers.clear()

        # create logger
        self.logger = logging.getLogger(self.run_label)
        self.logger.setLevel(logging.DEBUG)

        # add file logging
        try:
            pathlib.Path(magpie_config.log_dir).mkdir(parents=True)
        except FileExistsError:
            pass
        file_handler = logging.FileHandler(os.path.join(magpie_config.log_dir, "{}.log".format(self.run_label)), delay=True)
        file_handler.setFormatter(logging.Formatter('%(asctime)s\t[%(levelname)s]\t%(message)s'))
        file_handler.setLevel(logging.DEBUG)
        self.logger.addHandler(file_handler)

        # add stream handler
        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(logging.INFO)
        self.logger.addHandler(stream_handler)

    def reset_contents(self):
        self.contents = {}
        self.locations = {}
        for target_file in self.target_files:
            try:
                engine = self.engines[target_file]
            except KeyError:
                engine = self.get_engine(target_file)
                self.engines[target_file] = engine
            self.contents[target_file] = engine.get_contents(os.path.join(self.path, target_file))
            self.locations[target_file] = engine.get_locations(self.contents[target_file])

    def __str__(self):
        return "{}({}):{}".format(self.__class__.__name__,
                                  self.path, ",".join(self.target_files))

    def get_engine(self, target_file):
        raise RuntimeError('Unknown engine for "{}"'.format(target_file))

    def create_edit(self):
        if self.possible_edits:
            edit = random.choice(self.possible_edits).create(self)
            tries = magpie_config.edit_retries
            while tries > 0:
                if edit.target is not None:
                    return edit
                tries -= 1
                edit = random.choice(self.possible_edits).create(self)
        raise RuntimeError('unable to create edit')

    def random_file(self, engine=None):
        if engine:
            files = [f for f in self.target_files if issubclass(self.engines[f], engine)]
        else:
            files = self.target_files
        return random.choice(files)

    def random_target(self, target_file=None, target_type=None):
        if target_file is None:
            target_file = random.choice(self.target_files)
        return self.get_engine(target_file).random_target(self.locations, target_file, target_type)

    def apply_patch(self, patch):
        # process modified files
        new_contents = copy.deepcopy(self.contents)
        new_locations = copy.deepcopy(self.locations)
        for target_file in self.contents.keys():
            # filter edits
            edits = list(filter(lambda a: a.target[0] == target_file, patch.edits))
            for edit in edits:
                edit.apply(self, new_contents, new_locations)

        # return modified content
        return new_contents

    def write_contents(self, new_contents):
        # reset work directory
        work_path = os.path.join(self.work_dir, self.basename)
        self.sync_folder(work_path, self.path)

        # process modified files
        for target_file in new_contents.keys():
            self.engines[target_file].write_contents_file(new_contents, work_path, target_file)

        # memorise
        self.local_contents = copy.deepcopy(new_contents)

    def sync_folder(self, target, original):
        try:
            contents_target = os.listdir(target)
        except FileNotFoundError:
            shutil.copytree(original, target)
            return
        contents_original = os.listdir(original)
        for entry in contents_target:
            if os.path.isdir(os.path.join(target, entry)):
                if entry not in contents_original:
                    # new directory
                    shutil.rmtree(os.path.join(target, entry))
                # else: common directory
            elif entry not in contents_original:
                # new file
                os.remove(os.path.join(target, entry))
            elif os.path.getmtime(os.path.join(original, entry)) < os.path.getmtime(os.path.join(target, entry)):
                # modified file
                shutil.copyfile(os.path.join(original, entry), os.path.join(target, entry))
                shutil.copystat(os.path.join(original, entry), os.path.join(target, entry))
            # else: unmodified file
        for entry in contents_original:
            if os.path.isdir(entry):
                if entry in contents_target:
                    # recursion
                    self.sync_folder(os.path.join(target, entry), os.path.join(original, entry))
                else:
                    # deleted directory (?)
                    shutil.copytree(os.path.join(original, entry), os.path.join(target, entry))
            elif entry not in contents_target:
                # deleted file
                shutil.copyfile(os.path.join(original, entry), os.path.join(target, entry))
            # else: appears in both (already handled)

    # def evaluate_patch(self, patch):
    #     new_contents = self.apply_patch(patch)
    #     return self.evaluate_contents(new_contents)

    def evaluate_contents(self, new_contents):
        self.write_contents(new_contents)
        return self.evaluate_local()

    def evaluate_local(self):
        cwd = os.getcwd()
        run_result = RunResult('SETUP_ERROR')
        try:
            # go to work directory
            os.chdir(os.path.join(self.work_dir, self.basename))

            # compile if needed
            if self.compile_cmd:
                timeout = self.compile_timeout or magpie_config.default_timeout
                max_output = self.compile_output or magpie_config.default_output
                exec_result = self.exec_cmd(shlex.split(self.compile_cmd),
                                            timeout=timeout,
                                            max_output=max_output)
                run_result.status = exec_result.status
                if run_result.status == 'SUCCESS':
                    self.process_compile_exec(run_result, exec_result)
                if run_result.status != 'SUCCESS':
                    return run_result

            # update command lines if needed
            cli = ''
            for target in self.target_files:
                engine = self.engines[target]
                if issubclass(engine, AbstractParamsEngine):
                    cli = '{} {}'.format(cli, engine.resolve_cli(self.local_contents[target]))

            # test if needed
            if self.test_cmd:
                test_cmd = '{} {}'.format(self.test_cmd, cli).strip()
                timeout = self.test_timeout or magpie_config.default_timeout
                max_output = self.test_output or magpie_config.default_output
                exec_result = self.exec_cmd(shlex.split(test_cmd),
                                            timeout=timeout,
                                            max_output=max_output)
                run_result.status = exec_result.status
                if run_result.status == 'SUCCESS':
                    self.process_test_exec(run_result, exec_result)
                if run_result.status != 'SUCCESS':
                    return run_result

            # run if needed
            if self.run_cmd:
                run_cmd = '{} {}'.format(self.run_cmd, cli).strip()
                timeout = self.run_timeout or magpie_config.default_timeout
                max_output = self.run_output or magpie_config.default_output
                exec_result = self.exec_cmd(shlex.split(run_cmd),
                                            timeout=timeout,
                                            max_output=max_output)
                run_result.status = exec_result.status
                if run_result.status == 'SUCCESS':
                    self.process_run_exec(run_result, exec_result)
        finally:
            # make sure to go back to main directory
            os.chdir(cwd)
        return run_result

    def exec_cmd(self, cmd, timeout=15, env=None, shell=False, max_output=1e6):
        # 1e6 bytes is 1Mb
        sprocess = None
        stdout = b''
        stderr = b''
        start = time.time()
        try:
            self.last_cmd = str(cmd)
            sprocess = None
            try:
                sprocess = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, preexec_fn=os.setsid, env=env, shell=shell)
            except FileNotFoundError:
                return ExecResult('CLI_ERROR', -1, b"", b"", 0)
            if max_output:
                stdout_size = 0
                stderr_size = 0
                while sprocess.poll() is None:
                    end = time.time()
                    if end-start > timeout:
                        os.killpg(os.getpgid(sprocess.pid), signal.SIGKILL)
                        _, _ = sprocess.communicate()
                        return ExecResult('TIMEOUT', sprocess.returncode, stdout, stderr, end-start)
                    a = select.select([sprocess.stdout, sprocess.stderr], [], [], 1)[0]
                    if sprocess.stdout in a:
                        for _ in range(1024):
                            if not len(select.select([sprocess.stdout], [], [], 0)[0]):
                                break
                            stdout += sprocess.stdout.read(1)
                            stdout_size += 1
                    if sprocess.stderr in a:
                        for _ in range(1024):
                            if not len(select.select([sprocess.stderr], [], [], 0)[0]):
                                break
                            stderr += sprocess.stderr.read(1)
                            stderr_size += 1
                    if stdout_size+stderr_size >= max_output:
                        os.killpg(os.getpgid(sprocess.pid), signal.SIGKILL)
                        _, _ = sprocess.communicate()
                        return ExecResult('OUTPUT_LIMIT', sprocess.returncode, stdout, stderr, end-start)
                end = time.time()
                stdout += sprocess.stdout.read()
                stderr += sprocess.stderr.read()
            else:
                try:
                    stdout, stderr = sprocess.communicate(timeout=timeout)
                except subprocess.TimeoutExpired:
                    os.killpg(os.getpgid(sprocess.pid), signal.SIGKILL)
                    stdout, stderr = sprocess.communicate()
                    end = time.time()
                    return ExecResult('TIMEOUT', sprocess.returncode, stdout, stderr, end-start)
                end = time.time()
            return ExecResult('SUCCESS', sprocess.returncode, stdout, stderr, end-start)

        finally:
            self.last_stdout = stdout
            self.last_stderr = stderr

    def process_compile_exec(self, run_result, exec_result):
        if exec_result.return_code != 0:
            run_result.debug = exec_result
            run_result.status = 'COMPILE_ERROR'

    def process_test_exec(self, run_result, exec_result):
        if exec_result.return_code != 0:
            run_result.debug = exec_result
            run_result.status = 'TEST_ERROR'

    def process_run_exec(self, run_result, exec_result):
        stdout = exec_result.stdout.decode(magpie_config.output_encoding)
        m = re.search('MAGPIE_FITNESS: (.*)', stdout)
        if m:
            try:
                run_result.fitness = float(m.group(1))
            except ValueError:
                run_result.debug = exec_result
                run_result.status = 'PARSE_ERROR'
        else:
            run_result.debug = exec_result
            run_result.status = 'PARSE_ERROR'

    def clean_work_dir(self):
        try:
            shutil.rmtree(self.work_dir)
        except FileNotFoundError:
            pass
        try:
            os.rmdir(magpie_config.work_dir)
        except FileNotFoundError:
            pass
        except OSError as e:
            if e.errno != errno.ENOTEMPTY:
                raise

    def diff_patch(self, patch):
        new_contents = self.apply_patch(patch)
        return self.diff_contents(new_contents)

    def diff_local(self):
        return self.diff_contents(self.local_contents)

    def diff_contents(self, new_contents):
        """
        Compare the source codes of original program and the patch-applied program
        using *difflib* module(https://docs.python.org/3.6/library/difflib.html).
        """
        if magpie_config.diff_method == 'unified':
            diff_method = difflib.unified_diff
        elif magpie_config.diff_method == 'context':
            diff_method = difflib.context_diff
        else:
            raise ValueError('Unknown diff method: `{}`'.format(magpie_config.diff_method))
        diffs = ''
        for filename in self.target_files:
            new_filename = self.engines[filename].renamed_contents_file(filename)
            orig = self.engines[filename].dump(self.contents[filename])
            modi = self.engines[filename].dump(new_contents[filename])
            orig_list = list(map(lambda s: s+'\n', orig.splitlines()))
            modi_list = list(map(lambda s: s+'\n', modi.splitlines()))
            for diff in diff_method(orig_list, modi_list,
                                    fromfile="before: " + new_filename,
                                    tofile="after: " + new_filename):
                diffs += diff
        return diffs
