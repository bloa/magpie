import os
import pathlib
import shlex

import magpie.settings

from .abstract_software import AbstractSoftware
from .errors import ScenarioError
from .runresult import RunResult


class BasicSoftware(AbstractSoftware):
    def __init__(self, config):
        self.config = config

        # AbstractSoftware *requires* a path, a list of target files, and a list of possible edits
        if not (val := config['software']['path']):
            msg = 'Invalid config file: "[software] path" must be defined'
            raise ScenarioError(msg)
        super().__init__(val, reset=False)
        if not (val := config['software']['target_files']):
            msg = 'Invalid config file: "[software] target_files" must defined'
            raise ScenarioError(msg)
        self.target_files = val.split()

        # model rules
        self.model_rules = []
        try:
            for rule in config['software']['model_rules'].split('\n'):
                if rule: # discard potential initial empty line
                    k, v = rule.split(':')
                    self.model_rules.append((k.strip(), v.strip()))
        except ValueError as e:
            msg = f'Badly formated rule: "{rule}"'
            raise ScenarioError(msg) from e

        # model config
        self.model_config = []
        try:
            for rule in config['software']['model_config'].split('\n'):
                if rule: # discard potential initial empty line
                    k, v = rule.split(':')
                    v = v.strip()
                    if v[0]+v[-1] != '[]':
                        msg = f'Badly formated section name: "{rule}"'
                        raise ScenarioError(msg)
                    self.model_config.append((k.strip(), v[1:-1]))
        except ValueError as e:
            msg = f'Badly formated rule: "{rule}"'
            raise ScenarioError(msg) from e

        # fitness type
        if 'fitness' not in config['software']:
            msg = 'Invalid config file: "[software] fitness" must be defined'
            raise ScenarioError(msg)
        self.fitness = []
        tmp = config['software']['fitness'].split('<')
        tmp2 = []
        _msg = 'Invalid config file: bad templating in "[software] fitness"'
        if '>' in tmp[0]:
            msg = f'{_msg} (unexpected ">" before any "<")'
            raise ScenarioError(msg)
        i = 0
        while i < len(tmp):
            if i > 0:
                if not tmp2:
                    msg = f'{_msg} (missing fitness name before "<")'
                    raise ScenarioError(msg)
                l = tmp[i].split('>')
                if len(l) != 2:
                    if len(l) == 1:
                        msg = f'{_msg} (missing ">" for fitness "{tmp2[-1]}")'
                    else:
                        msg = f'{_msg} (unpaired ">")'
                    raise ScenarioError(msg)
                tmp2[-1] = f'{tmp2[-1].strip()}<{l[0]}>'
                tmp[i] = l[1]
            tmp2.extend(tmp[i].split())
            i += 1
        for s in [s.strip() for s in tmp2]:
            if s[0] == '-':
                fit = magpie.utils.convert.fitness_from_string(s[1:])(self)
                fit.maximize = True
            else:
                fit = magpie.utils.convert.fitness_from_string(s)(self)
            self.fitness.append(fit)

        # execution-related parameters
        self.init_performed = False
        self.init_cmd = None
        self.init_timeout = None
        self.setup_performed = False
        self.setup_cmd = None
        self.setup_timeout = None
        self.setup_lengthout = None
        self.compile_cmd = None
        self.compile_timeout = None
        self.compile_lengthout = None
        self.test_cmd = None
        self.test_timeout = None
        self.test_lengthout = None
        self.run_cmd = None
        self.run_timeout = None
        self.run_lengthout = None
        self.batch_timeout = None
        self.batch_lengthout = None

        # init
        if 'init_cmd' in config['software']:
            if config['software']['init_cmd'].lower() in ['', 'none']:
                self.init_cmd = None
            else:
                self.init_cmd = config['software']['init_cmd']
        if 'init_timeout' in config['software']:
            if config['software']['init_timeout'].lower() in ['', 'none']:
                self.init_timeout = None
            else:
                self.init_timeout = float(config['software']['init_timeout'])
        if 'init_lengthout' in config['software']:
            if config['software']['init_lengthout'].lower() in ['', 'none']:
                self.init_lengthout = None
            else:
                self.init_lengthout = int(config['software']['init_lengthout'])

        # setup
        if 'setup_cmd' in config['software']:
            if config['software']['setup_cmd'].lower() in ['', 'none']:
                self.setup_cmd = None
            else:
                self.setup_cmd = config['software']['setup_cmd']
        if 'setup_timeout' in config['software']:
            if config['software']['setup_timeout'].lower() in ['', 'none']:
                self.setup_timeout = None
            else:
                self.setup_timeout = float(config['software']['setup_timeout'])
        if 'setup_lengthout' in config['software']:
            if config['software']['setup_lengthout'].lower() in ['', 'none']:
                self.setup_lengthout = None
            else:
                self.setup_lengthout = int(config['software']['setup_lengthout'])

        # compile
        if 'compile_cmd' in config['software']:
            if config['software']['compile_cmd'].lower() in ['', 'none']:
                self.compile_cmd = None
            else:
                self.compile_cmd = config['software']['compile_cmd']
        if 'compile_timeout' in config['software']:
            if config['software']['compile_timeout'].lower() in ['', 'none']:
                self.compile_timeout = None
            else:
                self.compile_timeout = float(config['software']['compile_timeout'])
        if 'compile_lengthout' in config['software']:
            if config['software']['compile_lengthout'].lower() in ['', 'none']:
                self.compile_lengthout = None
            else:
                self.compile_lengthout = int(config['software']['compile_lengthout'])

        # test
        if 'test_cmd' in config['software']:
            if config['software']['test_cmd'].lower() in ['', 'none']:
                self.test_cmd = None
            else:
                self.test_cmd = config['software']['test_cmd']
        if 'test_timeout' in config['software']:
            if config['software']['test_timeout'].lower() in ['', 'none']:
                self.test_timeout = None
            else:
                self.test_timeout = float(config['software']['test_timeout'])
        if 'test_lengthout' in config['software']:
            if config['software']['test_lengthout'].lower() in ['', 'none']:
                self.test_lengthout = None
            else:
                self.test_lengthout = int(config['software']['test_lengthout'])

        # run
        if 'run_cmd' in config['software']:
            if config['software']['run_cmd'].lower() in ['', 'none']:
                self.run_cmd = None
            else:
                self.run_cmd = config['software']['run_cmd']
        if 'run_timeout' in config['software']:
            if config['software']['run_timeout'].lower() in ['', 'none']:
                self.run_timeout = None
            else:
                self.run_timeout = float(config['software']['run_timeout'])
        if 'run_lengthout' in config['software']:
            if config['software']['run_lengthout'].lower() in ['', 'none']:
                self.run_lengthout = None
            else:
                self.run_lengthout = int(config['software']['run_lengthout'])

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
        if 'batch_timeout' in config['software']:
            if config['software']['batch_timeout'].lower() in ['', 'none']:
                self.batch_timeout = None
            else:
                self.batch_timeout = float(config['software']['batch_timeout'])
        if 'batch_lengthout' in config['software']:
            if config['software']['batch_lengthout'].lower() in ['', 'none']:
                self.batch_lengthout = None
            else:
                self.batch_lengthout = int(config['software']['batch_lengthout'])

        # reset everything
        self.reset_timestamp()
        self.reset_logger()
        self.reset_workdir()
        self.reset_contents()

    def reset_contents(self):
        if not self.init_performed:
            self.init_performed = True
            if self.init_cmd:
                cwd = pathlib.Path.cwd()
                try:
                    os.chdir(self.path)
                    timeout = self.init_timeout or magpie.settings.default_timeout
                    lengthout = self.init_lengthout or magpie.settings.default_lengthout
                    exec_result = self.exec_cmd(shlex.split(self.init_cmd),
                                                timeout=timeout,
                                                lengthout=lengthout)
                    run_result = RunResult(None, exec_result.status)
                    if run_result.status == 'SUCCESS':
                        for fit in self.fitness:
                            fit.process_init_exec(run_result, exec_result)
                    if run_result.status != 'SUCCESS':
                        run_result.status = f'INIT_{run_result.status}'
                        run_result.last_exec = exec_result
                        self.diagnose_error(run_result)
                        msg = '(cmd_init) failed to init target software'
                        raise RuntimeError(msg)
                finally:
                    os.chdir(cwd)
        super().reset_contents()

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

        cwd = pathlib.Path.cwd()
        try:
            os.chdir(work_path)

            # serves as base before run_cmd
            default_variant_fitness = [None for _ in self.fitness]
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
                        for fit in self.fitness:
                            fit.process_setup_exec(run_result, exec_result)
                    if run_result.status != 'SUCCESS':
                        run_result.status = f'SETUP_{run_result.status}'
                        run_result.fitness = None
                        return run_result

                # sync work directory
                self.sync_folder(self.path, work_path)

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
                    for i, fit in enumerate(self.fitness):
                        run_result.fitness = None
                        fit.process_compile_exec(run_result, exec_result)
                        if run_result.fitness is not None:
                            default_variant_fitness[i] = run_result.fitness
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
                    for i, fit in enumerate(self.fitness):
                        run_result.fitness = None
                        fit.process_test_exec(run_result, exec_result)
                        if run_result.fitness is not None:
                            default_variant_fitness[i] = run_result.fitness
                if run_result.status == 'SUCCESS':
                    run_result.fitness = default_variant_fitness
                else:
                    run_result.status = f'TEST_{run_result.status}'
                    run_result.fitness = None
                    return run_result

            # run "[software] run_cmd" if provided
            if self.run_cmd:
                cli = self.compute_local_cli(variant, 'run')
                timeout = self.run_timeout or magpie.settings.default_timeout
                lengthout = self.run_lengthout or magpie.settings.default_lengthout
                batch_timeout = self.batch_timeout
                batch_lengthout = self.batch_lengthout
                insts = [inst for b in self.batch for inst in b]
                for inst in insts:
                    variant_fitness = default_variant_fitness[:]
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
                        for i, fit in enumerate(self.fitness):
                            run_result.fitness = None
                            fit.process_run_exec(run_result, exec_result)
                            if run_result.fitness is not None:
                                variant_fitness[i] = run_result.fitness
                    self.process_batch_single(run_result, inst, variant_fitness)
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

        finally:
            os.chdir(cwd)

        # final process
        return run_result

    def compute_local_cli(self, variant, step):
        cli = ''
        for target in self.target_files:
            model = variant.models[target]
            cli = model.update_cli(variant, cli, step)
        return cli

    def process_batch_single(self, run_result, inst, variant_fitness):
        run_result.cache[inst] = (run_result.status, variant_fitness)
        if inst != '':
            self.logger.debug('EXEC> %s %s %s', inst, run_result.status, variant_fitness)

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
