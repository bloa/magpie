import abc
import contextlib
import copy
import difflib
import errno
import logging
import os
import pathlib
import random
import select
import shutil
import signal
import subprocess
import time

import magpie
from .execresult import ExecResult
from .variant import Variant

class AbstractSoftware(abc.ABC):
    def __init__(self, path, reset=True):
        self.logger = None
        self.path = os.path.abspath(path.strip())
        self.basename = os.path.basename(self.path)
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
        try:
            os.makedirs(magpie.settings.work_dir)
        except FileExistsError:
            pass
        while True:
            self.run_label = '{}_{}'.format(self.basename, self.timestamp)
            new_work_dir = os.path.join(os.path.abspath(magpie.settings.work_dir), self.run_label)
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

    def reset_logger(self):
        # just in case
        if self.logger:
            self.logger.handlers.clear()

        # create logger
        self.logger = logging.getLogger(self.run_label)
        self.logger.setLevel(logging.DEBUG)

        # add file logging
        try:
            pathlib.Path(magpie.settings.log_dir).mkdir(parents=True)
        except FileExistsError:
            pass
        file_handler = logging.FileHandler(os.path.join(magpie.settings.log_dir, "{}.log".format(self.run_label)), delay=True)
        file_handler.setFormatter(logging.Formatter('%(asctime)s\t[%(levelname)s]\t%(message)s'))
        file_handler.setLevel(logging.DEBUG)
        self.logger.addHandler(file_handler)

        # add stream handler
        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(logging.INFO)
        self.logger.addHandler(stream_handler)

    def reset_workdir(self):
        # creates or move current work_dir
        new_work_dir = os.path.join(os.path.abspath(magpie.settings.work_dir), self.run_label)
        if self.work_dir and os.path.exists(self.work_dir):
            self.work_dir = shutil.move(self.work_dir, new_work_dir)
            if magpie.settings.local_original_copy:
                self.path = os.path.join(self.work_dir, magpie.settings.local_original_name)
        else:
            self.work_dir = new_work_dir
            if magpie.settings.local_original_copy:
                new_path = os.path.join(self.work_dir, magpie.settings.local_original_name)
                if self.path != new_path:
                    self.path = shutil.copytree(self.path, new_path)
        lock_file = '{}.lock'.format(new_work_dir)
        os.remove(lock_file)

    def reset_contents(self):
        # expend wildcards in target file list
        if any('*' in f for f in self.target_files):
            path = pathlib.Path(self.path)
            tmp = [sorted(path.glob(f)) if '*' in f else [f] for f in self.target_files]
            self.target_files = [str(f.relative_to(path)) for fl in tmp for f in fl]

        # reset noop variant
        self.noop_variant = Variant(self)

    @abc.abstractmethod
    def evaluate_variant(self, variant, cached_run=None):
        pass

    def write_variant(self, variant):
        # reset work directory
        work_path = os.path.join(self.work_dir, self.basename)
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
            if os.path.isdir(os.path.join(original, entry)):
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
            sprocess = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, preexec_fn=os.setsid, env=env, shell=shell)
        except FileNotFoundError:
            return ExecResult(cmd, 'CLI_ERROR', -1, b"", b"", 0, 0)
        if lengthout > 0:
            stdout_size = 0
            stderr_size = 0
            while sprocess.poll() is None:
                end = time.time()
                if end-start > timeout:
                    os.killpg(os.getpgid(sprocess.pid), signal.SIGKILL)
                    _, _ = sprocess.communicate()
                    return ExecResult(cmd, 'TIMEOUT', sprocess.returncode, stdout, stderr, end-start, stdout_size+stderr_size)
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
                if stdout_size+stderr_size >= lengthout:
                    os.killpg(os.getpgid(sprocess.pid), signal.SIGKILL)
                    _, _ = sprocess.communicate()
                    return ExecResult(cmd, 'LENGTHOUT', sprocess.returncode, stdout, stderr, end-start, stdout_size+stderr_size)
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
                return ExecResult(cmd, 'TIMEOUT', sprocess.returncode, stdout, stderr, end-start, len(stdout)+len(stderr))
            end = time.time()
        return ExecResult(cmd, 'SUCCESS', sprocess.returncode, stdout, stderr, end-start, len(stdout)+len(stderr))

    def clean_work_dir(self):
        try:
            shutil.rmtree(self.work_dir)
        except FileNotFoundError:
            pass
        try:
            os.rmdir(magpie.settings.work_dir)
        except FileNotFoundError:
            pass
        except OSError as e:
            if e.errno != errno.ENOTEMPTY:
                raise
