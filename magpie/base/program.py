import os
import shutil
import time
import pathlib
import random
import collections
import subprocess
import copy
import difflib
import select
import signal
import errno
import logging
import re

from .. import config as magpie_config
from ..params import AbstractParamsEngine
from .execresult import ExecResult

class AbstractProgram():
    def __init__(self, path):
        self.logger = None
        self.path = os.path.abspath(path.strip())
        self.basename = os.path.basename(self.path)
        self.target_files = []
        self.engines = {}
        self.contents = {}
        self.local_contents = {}
        self.locations = {}
        self.location_weights = {}
        self.possible_edits = []
        self.work_dir = None

        self.reset_timestamp()
        self.reset_logger()
        self.reset_workdir()
        # self.reset_contents()

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

    def reset_workdir(self):
        # creates or move current work_dir
        new_work_dir = os.path.join(os.path.abspath(magpie_config.work_dir), self.run_label)
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
        lock_file = '{}.lock'.format(new_work_dir)
        os.remove(lock_file)

    def reset_contents(self):
        self.contents = {}
        self.locations = {}
        for target_file in self.target_files:
            try:
                engine = self.engines[target_file]
            except KeyError:
                engine = self.get_engine(target_file)
                self.configure_engine(engine, target_file)
                self.engines[target_file] = engine
            self.contents[target_file] = engine.get_contents(os.path.join(self.path, target_file))
            self.locations[target_file] = engine.get_locations(self.contents[target_file])

    def __str__(self):
        return "{}({}):{}".format(self.__class__.__name__,
                                  self.path, ",".join(self.target_files))

    def get_engine(self, target_file):
        raise NotImplementedError

    def configure_engine(self, engine, target_file):
        pass

    def location_names(self, target_file, target_type):
        return self.get_engine(target_file).location_names(self.locations, target_file, target_type)

    def show_location(self, target_file, target_type, target_loc):
        return self.get_engine(target_file).show_location(self.contents, self.locations, target_file, target_type, target_loc)

    def random_file(self, engine=None):
        if engine:
            files = [f for f in self.target_files if isinstance(self.engines[f], engine)]
        else:
            files = self.target_files
        if files:
            return random.choice(files)
        raise RuntimeError('No compatible target file for engine {}'.format(engine.__name__))

    def random_target(self, target_file=None, target_type=None):
        if target_file is None:
            target_file = random.choice(self.target_files)
        return self.get_engine(target_file).random_target(self.locations, self.location_weights, target_file, target_type)

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

    def compute_local_cli(self, step):
        cli = ''
        for target in self.target_files:
            engine = self.engines[target]
            if isinstance(engine, AbstractParamsEngine):
                if step in engine.config['timing']:
                    cli = '{} {}'.format(cli, engine.resolve_cli(self.local_contents[target]))
        return cli

    def evaluate_local(self):
        raise NotImplementedError

    def exec_cmd(self, cmd, timeout=15, env=None, shell=False, max_output=1e6):
        # 1e6 bytes is 1Mb
        sprocess = None
        stdout = b''
        stderr = b''
        start = time.time()
        sprocess = None
        try:
            sprocess = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, preexec_fn=os.setsid, env=env, shell=shell)
        except FileNotFoundError:
            return ExecResult(cmd, 'CLI_ERROR', -1, b"", b"", 0)
        if max_output > 0:
            stdout_size = 0
            stderr_size = 0
            while sprocess.poll() is None:
                end = time.time()
                if end-start > timeout:
                    os.killpg(os.getpgid(sprocess.pid), signal.SIGKILL)
                    _, _ = sprocess.communicate()
                    return ExecResult(cmd, 'TIMEOUT', sprocess.returncode, stdout, stderr, end-start)
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
                    return ExecResult(cmd, 'LENGTHOUT', sprocess.returncode, stdout, stderr, end-start)
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
                return ExecResult(cmd, 'TIMEOUT', sprocess.returncode, stdout, stderr, end-start)
            end = time.time()
        return ExecResult(cmd, 'SUCCESS', sprocess.returncode, stdout, stderr, end-start)

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

    def self_diagnose(self, run):
        pass
