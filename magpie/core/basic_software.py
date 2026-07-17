import contextlib
import errno
import logging
import os
import pathlib
import platform
import re
import select
import shutil
import shlex
import signal
import subprocess
import time

import magpie.settings
from magpie.parsing import MathTree

from .abstract_software import AbstractSoftware
from .basic_variant import BasicVariant
from .errors import ScenarioError
from .execresult import ExecResult
from .runresult import RunResult


class BasicSoftware(AbstractSoftware):
    def __init__(self, config):
        self.config = config
        self.logger = None
        self.path = pathlib.Path(config['software']['path'].strip()).resolve()
        self.basename = self.path.name
        self.target_files = []
        self.ingredient_files = []
        self.noop_variant = None
        self.work_dir = None
        self.env_counter = None
        self.env_patch = None

        self.target_files = config['software']['target_files'].split()
        self.ingredient_files = config['software']['ingredient_files'].split()

        # model rules
        self.model_rules = self._init_model_rules(config['software']['model_rules'])
        if not self.model_rules:
            msg = 'Invalid config file: empty "[software] model_rules"'
            raise ScenarioError(msg)

        # model config
        self.model_config = self._init_model_config(config['software']['model_config'])
        if not self.model_config:
            msg = 'Invalid config file: empty "[software] model_config"'
            raise ScenarioError(msg)

        # fitness type
        self.fitness_trees = self._init_model_fitness(config['software']['fitness'])
        if not self.fitness_trees:
            msg = 'Invalid config file: empty "[software] fitness"'
            raise ScenarioError(msg)
        self.fitness_objectives = {s: magpie.utils.fitness_from_string(s)(self) for tree in self.fitness_trees for s in tree.variables}

        # init
        self.init_performed = False
        self.init_cmd = magpie.utils.str_to_str_or_none(config['software']['init_cmd'])
        self.init_timeout = magpie.utils.str_to_float_or_none(config['software']['init_timeout'])
        self.init_lengthout = magpie.utils.str_to_int_or_none(config['software']['init_lengthout'])

        # setup
        self.setup_performed = False
        self.setup_cmd = magpie.utils.str_to_str_or_none(config['software']['setup_cmd'])
        self.setup_timeout = magpie.utils.str_to_float_or_none(config['software']['setup_timeout'])
        self.setup_lengthout = magpie.utils.str_to_int_or_none(config['software']['setup_lengthout'])

        # compile
        self.compile_cmd = magpie.utils.str_to_str_or_none(config['software']['compile_cmd'])
        self.compile_timeout = magpie.utils.str_to_float_or_none(config['software']['compile_timeout'])
        self.compile_lengthout = magpie.utils.str_to_int_or_none(config['software']['compile_lengthout'])

        # test
        self.test_cmd = magpie.utils.str_to_str_or_none(config['software']['test_cmd'])
        self.test_timeout = magpie.utils.str_to_float_or_none(config['software']['test_timeout'])
        self.test_lengthout = magpie.utils.str_to_int_or_none(config['software']['test_lengthout'])

        # run
        self.run_cmd = magpie.utils.str_to_str_or_none(config['software']['run_cmd'])
        self.run_timeout = magpie.utils.str_to_float_or_none(config['software']['run_timeout'])
        self.run_lengthout = magpie.utils.str_to_int_or_none(config['software']['run_lengthout'])

        # batch parameters
        self.batch = [''] # default initial batch: single empty instance
        self.batch_fitness_strategy = config['software']['batch_fitness_strategy']
        known_strategies = ['sum', 'average', 'median']
        if self.batch_fitness_strategy not in known_strategies:
            tmp = '/'.join(known_strategies)
            msg = f'Invalid config file: "[software] batch_fitness_strategy" key must be {tmp}'
            raise ScenarioError(msg)
        self.batch_bin_fitness_strategy = config['software']['batch_fitness_strategy']
        known_strategies = ['aggregate', 'sum', 'average', 'median', 'q10', 'q25', 'q75', 'q90']
        if self.batch_fitness_strategy not in known_strategies:
            tmp = '/'.join(known_strategies)
            msg = f'Invalid config file: "[software] batch_bin_fitness_strategy" key must be {tmp}'
            raise ScenarioError(msg)
        self.batch_timeout = magpie.utils.str_to_float_or_none(config['software']['batch_timeout'])
        self.batch_lengthout = magpie.utils.str_to_int_or_none(config['software']['batch_lengthout'])

        # reset everything
        self.reset_timestamp()
        self.reset_logger()
        self.reset_workdir()
        self.reset_contents()


    def reset_timestamp(self):
        # ensures a unique timestamp
        self.unix_timestamp = int(time.time())
        with contextlib.suppress(FileExistsError):
            pathlib.Path(magpie.settings.work_dir).mkdir(parents=True)
        while True:
            local_time = time.strftime('%Y%m%d', time.localtime(self.unix_timestamp))
            self.run_label = f'{self.basename}_{local_time}_{self.unix_timestamp}'
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
            self.unix_timestamp += 1

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
            if isinstance(record.args, tuple):
                record.args = tuple(
                    re.sub(r'\033\[[0-9;]*m', '', arg) if isinstance(arg, str) else arg
                    for arg in record.args)
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
        if not self.init_performed:
            self.init_performed = True
            if self.init_cmd:
                with contextlib.chdir(self.path):
                    timeout = self.init_timeout or magpie.settings.default_timeout
                    lengthout = self.init_lengthout or magpie.settings.default_lengthout
                    exec_result = self.exec_cmd(shlex.split(self.init_cmd),
                                                timeout=timeout,
                                                lengthout=lengthout)
                    run_result = RunResult(None, exec_result.status)
                    if run_result.status == 'SUCCESS':
                        for fit in self.fitness_objectives.values():
                            fit.process_init_exec(run_result, exec_result)
                    if run_result.status != 'SUCCESS':
                        run_result.status = f'INIT_{run_result.status}'
                        run_result.last_exec = exec_result
                        self.diagnose_error(run_result)
                        msg = '(cmd_init) failed to init target software'
                        raise RuntimeError(msg)

        # expend wildcards in target file list
        if any('*' in f for f in self.target_files):
            tmp = [sorted(self.path.glob(f)) if '*' in f else [f] for f in self.target_files]
            self.target_files = [str(f.relative_to(self.path)) for fl in tmp for f in fl]
        if any('*' in f for f in self.ingredient_files):
            tmp = [sorted(self.path.glob(f)) if '*' in f else [f] for f in self.ingredient_files]
            self.ingredient_files = [str(f.relative_to(self.path)) for fl in tmp for f in fl]
        self.ingredient_files = [f for f in self.ingredient_files if f not in self.target_files]

        # reset noop variant
        self.noop_variant = BasicVariant(self)

    @staticmethod
    def _init_model_rules(value):
        rules = []
        try:
            for rule in value.split('\n'):
                if rule: # discard potential initial empty line
                    k, v = rule.split(':')
                    v = v.strip()
                    if re.search(r'[^_A-z0-9]', v):
                        msg = f'Badly formated rule: "{rule}"'
                        raise ScenarioError(msg)
                    rules.append((k.strip(), v))
        except ValueError as e:
            msg = f'Badly formated rule: "{rule}"'
            raise ScenarioError(msg) from e
        return rules

    @staticmethod
    def _init_model_config(value):
        config = []
        try:
            for rule in value.split('\n'):
                if rule: # discard potential initial empty line
                    k, v = rule.split(':')
                    v = v.strip()
                    if re.search(r'[^_A-z0-9]', v[1:-1]) or v[0]+v[-1] != '[]':
                        msg = f'Badly formated rule: "{rule}"'
                        raise ScenarioError(msg)
                    config.append((k.strip(), v[1:-1]))
        except ValueError as e:
            msg = f'Badly formated rule: "{rule}"'
            raise ScenarioError(msg) from e
        return config

    @staticmethod
    def _init_model_fitness(expr):
        # multi-objective fitness
        if ';' in expr:
            tmp = [BasicSoftware._init_model_fitness(s) for s in expr.split(';')]
            return [tree for trees in tmp for tree in trees]
        if '\n' in expr:
            tmp = [BasicSoftware._init_model_fitness(s) for s in expr.split()]
            return [tree for trees in tmp for tree in trees]
        # replace variable names
        var_map = {}
        var_count = 1
        pattern = re.compile(r'\b[a-zA-Z_]\w*(?:<[^<>]*?>)?')
        def replacer(_match):
            nonlocal var_count
            original = _match.group(0)
            if original not in var_map:
                var_map[original] = f'var{var_count}'
                var_count += 1
            return var_map[original]
        new_expr = pattern.sub(replacer, expr)
        # parse expression
        try:
            tree = MathTree.from_string(new_expr)
        except SyntaxError as e:
            msg = 'Invalid config file: unable to parse "[software] fitness"'
            raise ScenarioError(msg) from e
        except TypeError as e:
            msg = 'Invalid config file: "[software] fitness" only supports numeric expressions'
            raise ScenarioError(msg) from e
        # put original variable names back
        for (old, new) in var_map.items():
            tree.rename(new, old)
        return [tree]

    def evaluate_variant(self, variant, cached_run=None):
        # check batch sync
        if cached_run is None:
            # new variant
            self.write_variant(variant)
        elif not cached_run.cache.keys():
            # cached (failed) --> early exit
            return cached_run
        elif {inst for b in self.batch for inst in b}.issubset(cached_run.cache.keys()):
            # cached (complete) --> early exit
            self.process_batch_final(cached_run)
            return cached_run
        else:
            # partially cached
            self.write_variant(variant)

        # evaluate
        work_path = self.work_dir / self.basename
        run_result = cached_run or RunResult(variant, 'UNKNOWN_ERROR')
        run_result.updated = True

        with contextlib.chdir(work_path):
            raw_fitness_values = {}

            # one-time setup
            if not self.setup_performed:
                self.setup_performed = True

                # make sure this is the unmodified software
                for filename in self.target_files:
                    model = variant.models[filename]
                    if model.dump() != model.cached_dump:
                        raise AssertionError

                # run "[software] setup_cmd" if provided
                if self.setup_cmd:
                    # setup
                    cli = self.compute_local_cli(variant, 'setup')
                    setup_cmd = self.setup_cmd.strip()
                    if '{PARAMS}' in self.setup_cmd:
                        setup_cmd = setup_cmd.replace('{PARAMS}', cli)
                    else:
                        setup_cmd = f'{setup_cmd} {cli}'
                    timeout = self.setup_timeout or magpie.settings.default_timeout
                    lengthout = self.setup_lengthout or magpie.settings.default_lengthout
                    exec_result = self.exec_cmd(shlex.split(setup_cmd),
                                                timeout=timeout,
                                                lengthout=lengthout)
                    run_result.status = exec_result.status
                    run_result.last_exec = exec_result
                    if run_result.status == 'SUCCESS':
                        for (name, fit) in self.fitness_objectives.items():
                            run_result.fitness = None
                            fit.process_setup_exec(run_result, exec_result)
                            if run_result.fitness is not None:
                                raw_fitness_values[name] = run_result.fitness
                    if run_result.status != 'SUCCESS':
                        run_result.status = f'SETUP_{run_result.status}'
                        run_result.fitness = None
                        return run_result

                # sync work directory
                self.sync_folder(self.path, work_path)

            # make sure ingredient files are unmodified
            for filename in self.ingredient_files:
                model = variant.models[filename]
                if model.dump() != model.cached_dump:
                    raise AssertionError

            # run "[software] compile_cmd" if provided
            if self.compile_cmd:
                cli = self.compute_local_cli(variant, 'compile')
                compile_cmd = self.compile_cmd.strip()
                if '{PARAMS}' in self.compile_cmd:
                    compile_cmd = compile_cmd.replace('{PARAMS}', cli)
                else:
                    compile_cmd = f'{compile_cmd} {cli}'
                timeout = self.compile_timeout or magpie.settings.default_timeout
                lengthout = self.compile_lengthout or magpie.settings.default_lengthout
                exec_result = self.exec_cmd(shlex.split(compile_cmd),
                                            timeout=timeout,
                                            lengthout=lengthout)
                run_result.status = exec_result.status
                run_result.last_exec = exec_result
                if run_result.status == 'SUCCESS':
                    for (name, fit) in self.fitness_objectives.items():
                        run_result.fitness = None
                        fit.process_compile_exec(run_result, exec_result)
                        if run_result.fitness is not None:
                            raw_fitness_values[name] = run_result.fitness
                if run_result.status != 'SUCCESS':
                    run_result.status = f'COMPILE_{run_result.status}'
                    run_result.fitness = None
                    return run_result

            # run "[software] test_cmd" if provided
            if self.test_cmd:
                cli = self.compute_local_cli(variant, 'test')
                test_cmd = self.test_cmd.strip()
                if '{PARAMS}' in self.test_cmd:
                    test_cmd = test_cmd.replace('{PARAMS}', cli)
                else:
                    test_cmd = f'{test_cmd} {cli}'
                timeout = self.test_timeout or magpie.settings.default_timeout
                lengthout = self.test_lengthout or magpie.settings.default_lengthout
                exec_result = self.exec_cmd(shlex.split(test_cmd),
                                            timeout=timeout,
                                            lengthout=lengthout)
                run_result.status = exec_result.status
                run_result.last_exec = exec_result
                if run_result.status == 'SUCCESS':
                    for (name, fit) in self.fitness_objectives.items():
                        run_result.fitness = None
                        fit.process_test_exec(run_result, exec_result)
                        if run_result.fitness is not None:
                            raw_fitness_values[name] = run_result.fitness
                if run_result.status != 'SUCCESS':
                    run_result.status = f'TEST_{run_result.status}'
                    run_result.fitness = None
                    return run_result

            default_raw_fitness_values = raw_fitness_values.copy()
            # run "[software] run_cmd" if provided
            if self.run_cmd:
                cli = self.compute_local_cli(variant, 'run')
                timeout = self.run_timeout or magpie.settings.default_timeout
                lengthout = self.run_lengthout or magpie.settings.default_lengthout
                batch_timeout = self.batch_timeout
                batch_lengthout = self.batch_lengthout
                insts = [inst for b in self.batch for inst in b]
                for inst in insts:
                    raw_fitness_values = default_raw_fitness_values.copy()
                    if inst in run_result.cache:
                        continue
                    run_cmd = self.run_cmd.strip()
                    if '{INST}' in self.run_cmd:
                        run_cmd = run_cmd.replace('{INST}', inst)
                    else:
                        run_cmd = f'{run_cmd} {inst}'
                    if '{PARAMS}' in self.run_cmd:
                        run_cmd = run_cmd.replace('{PARAMS}', cli)
                    else:
                        run_cmd = f'{run_cmd} {cli}'
                    exec_result = self.exec_cmd(shlex.split(run_cmd),
                                                timeout=timeout,
                                                lengthout=lengthout)
                    run_result.status = exec_result.status
                    run_result.last_exec = exec_result
                    if run_result.status == 'SUCCESS':
                        for (name, fit) in self.fitness_objectives.items():
                            run_result.fitness = None
                            fit.process_run_exec(run_result, exec_result)
                            if run_result.fitness is not None:
                                raw_fitness_values[name] = run_result.fitness
                    run_result.fitness = self.process_final_fitness(raw_fitness_values)
                    self.process_batch_single(run_result, inst)
                    if run_result.status != 'SUCCESS':
                        run_result.status = f'RUN_{run_result.status}'
                        break
                    if batch_timeout:
                        batch_timeout -= exec_result.runtime
                        if batch_timeout < 0:
                            run_result.status = 'BATCH_TIMEOUT'
                            break
                    if batch_lengthout:
                        batch_lengthout -= exec_result.output_length
                        if batch_lengthout < 0:
                            run_result.status = 'BATCH_LENGTHOUT'
                            break
                self.process_batch_final(run_result)
            else:
                run_result.fitness = self.process_final_fitness(raw_fitness_values)

        # final process
        return run_result

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

    def compute_local_cli(self, variant, step):
        cli = ''
        for target in self.target_files:
            model = variant.models[target]
            cli = model.update_cli(variant, cli, step)
        return cli

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
        env['MAGPIE_BASENAME'] = self.basename
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

    def process_final_fitness(self, raw_fitness_values):
        final_fitness = []
        for tree in self.fitness_trees:
            try:
                fit = tree.evaluate(raw_fitness_values)
            except KeyError:
                return None
            final_fitness.append(fit)
        return final_fitness

    def process_batch_single(self, run_result, inst):
        run_result.cache[inst] = (run_result.status, run_result.fitness)
        if inst != '':
            self.logger.debug('EXEC> %s %s %s', inst, run_result.status, run_result.fitness)

    def process_batch_final(self, run_result):
        fit_per_batch = []
        for b in self.batch:
            bin_fitness = []
            for inst in b:
                status, fitness = run_result.cache[inst]
                if status != 'SUCCESS':
                    # TODO: penalised fitness
                    run_result.fitness = None
                    return
                bin_fitness.append(fitness)
            multi = len(bin_fitness[0]) > 1
            if self.batch_bin_fitness_strategy == 'aggregate':
                fit_per_batch.extend(bin_fitness) # ???
            else:
                acc = []
                tmp = [list(a) for a in zip(*bin_fitness)] if multi else bin_fitness
                for a in tmp: # a_k = fitness values per instance for fitness k
                    if len(a) == 1: # single instance
                        v = a[0]
                        precision = len(str(float(v)))
                    else:
                        precision = max(len(str(float(x)).split('.')[1]) for x in a)
                        if self.batch_bin_fitness_strategy == 'sum':
                            v = sum(a)
                        elif self.batch_bin_fitness_strategy == 'average':
                            v = sum(a)/len(a)
                            precision += 1
                        elif self.batch_bin_fitness_strategy == 'median':
                            if len(a) % 2 == 0:
                                v = sorted(a)[len(a)//2]
                            else:
                                v = sum(sorted(a)[len(a)//2:len(a)//2+2])/2
                                precision += 1
                        elif self.batch_bin_fitness_strategy == 'q10':
                            if len(a) % 10 == 0:
                                v = sorted(a)[len(a)//10]
                            else:
                                v = sum(sorted(a)[len(a)//10:len(a)//10+2])/2
                                precision += 1
                        elif self.batch_bin_fitness_strategy == 'q25':
                            if len(a) % 4 == 0:
                                v = sorted(a)[len(a)//4]
                            else:
                                v = sum(sorted(a)[len(a)//10:len(a)//10+2])/2
                                precision += 1
                        elif self.batch_bin_fitness_strategy == 'q75':
                            if len(a) % 4 == 0:
                                v = sorted(a)[3*len(a)//4]
                            else:
                                v = sum(sorted(a)[3*len(a)//4:3*len(a)//4+2])/2
                                precision += 1
                        elif self.batch_bin_fitness_strategy == 'q90':
                            if len(a) % 10 == 0:
                                v = sorted(a)[len(a)//10]
                            else:
                                v = sum(sorted(a)[9*len(a)//10:9*len(a)//10+2])/2
                                precision += 1
                    acc.append(round(v, precision))
                fit_per_batch.append(acc)
        acc = []
        tmp = [list(a) for a in zip(*fit_per_batch)]
        for a in tmp: # a_k = fitness values per bin for fitness k
            if len(a) == 1: # single bin
                v = a[0]
                precision = len(str(float(v)))
            else:
                precision = max(len(str(float(x)).split('.')[1]) for x in a)
                if self.batch_fitness_strategy == 'sum':
                    v = sum(a)
                elif self.batch_fitness_strategy == 'average':
                    v = sum(a)/len(a)
                    precision += 1
                elif self.batch_fitness_strategy == 'median':
                    if len(a) % 2 == 0:
                        v = sorted(a)[len(a)//2]
                    else:
                        v = sum(sorted(a)[len(a)//2:len(a)//2+2])/2
                        precision += 1
            acc.append(round(v, precision))
        run_result.fitness = acc

    def clean_work_dir(self):
        with contextlib.suppress(FileNotFoundError):
            shutil.rmtree(self.work_dir)
        with contextlib.suppress(FileNotFoundError):
            try:
                pathlib.Path(magpie.settings.work_dir).rmdir()
            except OSError as e:
                if e.errno != errno.ENOTEMPTY:
                    raise

    def diagnose_error(self, run):
        self.logger.info('!*'*40)
        self.logger.info('Unable to run and evaluate the target software.')
        self.logger.info('Self-diagnostic:')
        self.self_diagnostic(run)
        self.logger.info('!*'*40)
        if run.last_exec is not None:
            self.logger.info('CWD: %s', pathlib.Path(self.work_dir) / self.basename)
            self.logger.info('CMD: %s', run.last_exec.cmd)
            self.logger.info('STATUS: %s', run.last_exec.status)
            self.logger.info('RETURN_CODE: %s', run.last_exec.return_code)
            self.logger.info('RUNTIME: %s', run.last_exec.runtime)
            encoding = magpie.settings.output_encoding
            self.logger.info('STDOUT: (see log file)')
            try:
                s = run.last_exec.stdout.decode(encoding)
                self.logger.debug('STDOUT:\n%s', s)
            except UnicodeDecodeError:
                self.logger.debug('STDOUT: (failed to decode to: %s)\n%s', encoding, run.last_exec.stdout)
            self.logger.info('STDERR: (see log file)')
            try:
                s = run.last_exec.stderr.decode(encoding)
                self.logger.debug('STDERR:\n%s', s)
            except UnicodeDecodeError:
                self.logger.debug('STDERR: (failed to decode to: %s)\n%s', encoding, run.last_exec.stderr)
            self.logger.info('!*'*40)

    def self_diagnostic(self, run):
        for step in ['init', 'setup', 'compile', 'test', 'run']:
            if run.status == f'{step.upper()}_CLI_ERROR':
                self.logger.info('Unable to run the "%s_cmd" command', step)
                self.logger.info('--> there might be a typo (try it manually)')
                self.logger.info('--> your command might not be found (check your PATH)')
                self.logger.info('--> it might not run from the correct directory (check CWD below)')
            if run.status == f'{step.upper()}_CODE_ERROR':
                self.logger.info('The "%s_cmd" command failed with a nonzero exit code', step)
                self.logger.info('--> try to run it manually')
            if run.status == f'{step.upper()}_PARSE_ERROR':
                self.logger.info('The "%s_cmd" STDOUT/STDERR was invalid', step)
                self.logger.info('--> try to run it manually')
            if run.status == f'{step.upper()}_TIMEOUT':
                self.logger.info('The "%s_cmd" command took too long to run', step)
                self.logger.info('--> consider increasing "%s_timeout"', step)
            if run.status == f'{step.upper()}_LENGTHOUT':
                self.logger.info('The "%s_cmd" command generated too much output', step)
                self.logger.info('--> consider increasing "%s_lengthout"', step)
        if run.status == 'BATCH_TIMEOUT':
            self.logger.info('Batch execution of "run_cmd" took too long to run')
            self.logger.info('--> consider increasing "batch_timeout"')
        if run.status == 'BATCH_LENGTHOUT':
            self.logger.info('Batch execution of "run_cmd" generated too much output')
            self.logger.info('--> consider increasing "batch_lengthout"')

magpie.utils.known_software.append(BasicSoftware)

if os.name == 'posix':
    def _kill_proc_with_children(proc):
        os.killpg(os.getpgid(proc.pid), signal.SIGKILL)
elif platform.system() == 'Windows':
    def _kill_proc_with_children(proc):
        subprocess.run(['taskkill', '/F', '/T', '/PID', str(proc.pid)], check=False)
else: # we probably shouldn't even support this
    def _kill_proc_with_children(proc):
        proc.kill() # hoping there aren't any child process
