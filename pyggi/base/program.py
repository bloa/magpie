from abc import ABC, abstractmethod
import os
import shutil
import json
import time
import pathlib
import random
import enum
import collections
import subprocess
import shlex
import copy
import difflib
import select
import signal
import errno
import logging
from distutils.dir_util import copy_tree

from .. import config as pyggi_config
from .runresult import RunResult

class AbstractProgram(ABC):
    """
    Program encapsulates the original source code.
    Currently, PYGGI stores the source code as a list of code lines,
    as lines are the only supported unit of modifications.
    For modifications at other granularity levels,
    this class needs to process and store the source code accordingly
    (for example, by parsing and storing the AST).
    """
    def __init__(self, path, config={}):
        self.path = os.path.abspath(path.strip())
        self.basename = os.path.basename(self.path)
        self.work_dir = None
        self.target_files = []
        self.logger = None
        self.setup(config)
        self.reset()

    def reset(self):
        self.close_logger()
        self.timestamp = str(int(time.time()))

        # ensures the timestamp is unique
        while True:
            self.run_label = '{}_{}'.format(self.basename, self.timestamp)
            new_work_dir = os.path.join(os.path.abspath(pyggi_config.work_dir), self.run_label)
            lock_file = '{}.lock'.format(new_work_dir)
            try:
                os.open(lock_file, os.O_CREAT | os.O_EXCL).close()
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
            if pyggi_config.local_original_copy:
                self.path = os.path.join(self.work_dir, pyggi_config.local_original_name)
        else:
            self.work_dir = new_work_dir
            if pyggi_config.local_original_copy:
                new_path = os.path.join(self.work_dir, pyggi_config.local_original_name)
                if self.path != new_path:
                    self.path = shutil.copytree(self.path, new_path)
        os.remove(lock_file)

        self.work_path = os.path.join(self.work_dir, self.basename)
        self.setup_logger()
        self.reset_tmp_variant()
        self.load_contents()

    def __str__(self):
        return "{}({}):{}".format(self.__class__.__name__,
                                  self.path, ",".join(self.target_files))

    def setup(self, config={}):
        for key in [
                'test_command',
                'target_files',
        ]:
            try:
                self.__dict__[key] = config[key]
            except KeyError:
                pass

    def setup_logger(self):
        # create logger
        self.logger = logging.getLogger(self.run_label)
        self.logger.setLevel(logging.DEBUG)

        # add file logging
        try:
            pathlib.Path(pyggi_config.log_dir).mkdir(parents=True)
        except FileExistsError:
            pass
        file_handler = logging.FileHandler(os.path.join(pyggi_config.log_dir, "{}.log".format(self.run_label)), delay=True)
        file_handler.setFormatter(logging.Formatter('%(asctime)s\t[%(levelname)s]\t%(message)s'))
        file_handler.setLevel(logging.DEBUG)
        self.logger.addHandler(file_handler)

        # add stream handler
        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(logging.INFO)
        self.logger.addHandler(stream_handler)

    def close_logger(self):
        if self.logger is not None:
            self.logger.handlers.clear()


    @abstractmethod
    def get_engine(self, file_name):
        pass

    def load_engines(self):
        # Associate each file to its engine
        self.engines = dict()
        for file_name in self.target_files:
            self.engines[file_name] = self.get_engine(file_name)

    def load_contents(self):
        self.load_engines()
        self.contents = {}
        self.locations = {}
        self.locations_weights = {}
        for file_name in self.target_files:
            engine = self.engines[file_name]
            self.contents[file_name] = engine.get_contents(os.path.join(self.path, file_name))
            self.locations[file_name] = engine.get_locations(self.contents[file_name])

    def random_file(self, engine=None):
        if engine:
            files = [f for f in self.target_files if issubclass(self.engines[f], engine)]
        else:
            files = self.target_files
        return random.choice(files)

    def random_target(self, target_file=None, target_type=None):
        if target_file is None:
            target_file = random.choice(self.target_files)
        if target_type is None:
            target_type = random.choice(self.locations[target_file])
        try:
          if self.locations_weights[target_file][target_type]:
              # untested
              sum_proba = sum(self.locations_weights[target_file][target_type])
              if sum_proba > 0:
                  r = random.random()*sum_proba
                  for i,w in enumerate(self.locations_weights[target_file][target_type]):
                      if r <= r:
                          return (target_file, target_type, i)
                      r -= w
        except KeyError:
            pass
        return (target_file, target_type, random.randrange(len(self.locations[target_file][target_type])))

    def reset_tmp_variant(self):
        # TODO: be more like rsync
        self.remove_tmp_variant()
        shutil.copytree(self.path, self.work_path)

    def remove_tmp_variant(self):
        try:
            shutil.rmtree(self.work_path)
        except FileNotFoundError:
            pass

    def clean_work_dir(self):
        try:
            shutil.rmtree(self.work_dir)
        except FileNotFoundError:
            pass
        try:
            os.rmdir(pyggi_config.work_dir)
        except FileNotFoundError:
            pass
        except OSError as e:
            if e.errno != errno.ENOTEMPTY:
                raise

    def write_to_tmp_dir(self, new_contents):
        """
        Write new contents to the temporary directory of program

        :param new_contents: The new contents of the program.
          Refer to *apply* method of :py:class:`.patch.Patch`
        :type new_contents: dict(str, ?)
        :rtype: None
        """
        for target_file in new_contents:
            engine = self.engines[target_file]
            tmp_path = os.path.join(self.work_path, target_file)
            engine.write_to_tmp_dir(new_contents[target_file], tmp_path)

    def dump(self, contents, file_name):
        """
        Convert contents of file to the source code
        :param contents_of_file: The contents of the file which is the parsed form of source code
        :type contents_of_file: ?
        :return: The source code
        :rtype: str
        """
        return self.engines[file_name].dump(contents[file_name])

    def get_modified_contents(self, patch):
        new_locations = copy.deepcopy(self.locations)
        new_contents = copy.deepcopy(self.contents)
        for target_file in self.contents.keys():
            edits = list(filter(lambda a: a.target[0] == target_file, patch.edit_list))
            for edit in edits:
                edit.apply(self, new_contents, new_locations)
        return new_contents

    def apply(self, patch):
        """
        This method applies the patch to the target program.
        It does not directly modify the source code of the original program,
        but modifies the copied program within the temporary directory.

        :return: The contents of the patch-applied program, See *Hint*.
        :rtype: dict(str, list(str))

        .. hint::
            - key: The target file name(path) related to the program root path
            - value: The contents of the file
        """
        self.reset_tmp_variant()
        new_contents = self.get_modified_contents(patch)
        self.write_to_tmp_dir(new_contents)
        return new_contents

    def exec_cmd(self, cmd, timeout=15, env=None, shell=False, max_pipesize=1e4):
        # 1e6 bytes is 1Mb
        sprocess = None
        try:
            stdout = b''
            stderr = b''
            stdout_size = 0
            stderr_size = 0
            start = time.time()
            sprocess = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, preexec_fn=os.setsid, env=env, shell=shell)
            while sprocess.poll() is None:
                end = time.time()
                if end-start > timeout:
                    raise TimeoutError()
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
                if stdout_size+stderr_size >= max_pipesize:
                    raise IOError()
            end = time.time()
            stdout += sprocess.stdout.read()
            stderr += sprocess.stderr.read()
            return (sprocess.returncode, stdout, stderr, end-start)

        except (TimeoutError, IOError):
            end = time.time()
            if sprocess:
                os.killpg(os.getpgid(sprocess.pid), signal.SIGKILL)
                _, _ = sprocess.communicate()
                return (sprocess.returncode, stdout, stderr, end-start)
            else:
                raise

    def compute_fitness(self, result, return_code, stdout, stderr, elapsed_time):
        try:
            result.fitness = float(stdout.strip())
        except:
            result.status = 'PARSE_ERROR'

    def evaluate_patch(self, patch, timeout=15):
        # apply + run
        self.apply(patch)
        cwd = os.getcwd()
        try:
            os.chdir(self.work_path)
            return_code, stdout, stderr, elapsed_time = self.exec_cmd(shlex.split(self.test_command), timeout)
        finally:
            os.chdir(cwd)
        if return_code is None: # timeout
            return RunResult('TIMEOUT')
        else:
            result = RunResult('SUCCESS', None)
            self.compute_fitness(result, return_code, stdout.decode("ascii"), stderr.decode("ascii"), elapsed_time)
            return result

    def diff(self, patch) -> str:
        """
        Compare the source codes of original program and the patch-applied program
        using *difflib* module(https://docs.python.org/3.6/library/difflib.html).

        :return: The file comparison result
        :rtype: str
        """
        diffs = ''
        new_contents = self.get_modified_contents(patch)
        for file_name in self.target_files:
            orig = self.dump(self.contents, file_name)
            modi = self.dump(new_contents, file_name)
            orig_list = list(map(lambda s: s+'\n', orig.splitlines()))
            modi_list = list(map(lambda s: s+'\n', modi.splitlines()))
            for diff in difflib.context_diff(orig_list, modi_list,
                                             fromfile="before: " + file_name,
                                             tofile="after: " + file_name):
                diffs += diff
        return diffs
