import os
import re
import shlex

import magpie

from .. import config as magpie_config


class BasicProgram(magpie.base.AbstractProgram):
    def __init__(self, config):
        # AbstractProgram *requires* a path, a list of target files, and a list of possible edits
        if 'software' not in config:
            raise ValueError('Invalid config file: "[software]" block not found')
        if 'path' not in config['software']:
            raise ValueError('Invalid config file: "[software] path" must be defined')
        super().__init__(config['software']['path'])
        if 'target_files' not in config['software']:
            raise ValueError('Invalid config file: "[software] target_files" must defined')
        self.target_files = config['software']['target_files'].split()
        if not self.target_files:
            raise ValueError('Invalid config file: "[software] target_files" must be non-empty')

        # xml-related parameters
        if 'srcml' in config:
            if 'process_pseudo_blocks' in config['srcml']:
                v = config['srcml']['process_pseudo_blocks']
                if v.lower() in ['true', 't', '1']:
                    magpie.xml.SrcmlEngine.PROCESS_PSEUDO_BLOCKS = True
                elif v.lower() in ['false', 'f', '0']:
                    magpie.xml.SrcmlEngine.PROCESS_PSEUDO_BLOCKS = False
                else:
                    raise ValueError('Invalid config file: "[srcml] process_pseudo_blocks" should be Boolean')
            if 'process_literals' in config['srcml']:
                v = config['srcml']['process_literals']
                if v.lower() in ['true', 't', '1']:
                    magpie.xml.SrcmlEngine.PROCESS_LITERALS = True
                elif v.lower() in ['false', 'f', '0']:
                    magpie.xml.SrcmlEngine.PROCESS_LITERALS = False
                else:
                    raise ValueError('Invalid config file: "[srcml] process_literals" should be Boolean')
            if 'process_operators' in config['srcml']:
                v = config['srcml']['process_operators']
                if v.lower() in ['true', 't', '1']:
                    magpie.xml.SrcmlEngine.PROCESS_OPERATORS = True
                elif v.lower() in ['false', 'f', '0']:
                    magpie.xml.SrcmlEngine.PROCESS_OPERATORS = False
                else:
                    raise ValueError('Invalid config file: "[srcml] process_operators" should be Boolean')
            if 'internodes' in config['srcml']:
                magpie.xml.SrcmlEngine.INTERNODES = set(config['srcml']['internodes'].split())
            if 'rename' in config['srcml']:
                h = {}
                for rule in config['srcml']['rename'].split("\n"):
                    if rule.strip(): # discard potential initial empty line
                        try:
                            k, v = rule.split(':')
                        except ValueError:
                            raise ValueError('badly formated rule: "{}"'.format(rule))
                        h[k] = set(v.split())
                magpie.xml.SrcmlEngine.TAG_RENAME = h
            if 'focus' in config['srcml']:
                magpie.xml.SrcmlEngine.TAG_FOCUS = set(config['srcml']['focus'].split())

        # engine rules
        if 'engine_rules' in config['software']:
            self.engine_rules = []
            for rule in config['software']['engine_rules'].split("\n"):
                if rule: # discard potential initial empty line
                    try:
                        k, v = rule.split(':')
                    except ValueError:
                        raise ValueError('badly formated rule: "{}"'.format(rule))
                    self.engine_rules.append((k.strip(), magpie.bin.engine_from_string(v.strip())))
        else:
            self.engine_rules = [
                ('*.params', magpie.params.ConfigFileParamsEngine),
                ('*.xml', magpie.xml.SrcmlEngine),
                ('*', magpie.line.LineEngine),
            ]

        # reset contents here, AFTER xml parameters
        self.reset_contents()

        # fitness type
        if 'fitness' not in config['software']:
            raise ValueError('Invalid config file: "[software] fitness" must be defined')
        known_fitness = ['output', 'time', 'posix_time', 'perf_time', 'perf_instructions', 'repair', 'bloat_lines', 'bloat_words', 'bloat_chars']
        if config['software']['fitness'] not in known_fitness:
            raise ValueError('Invalid config file: "[software] fitness" key must be {}'.format('/'.join(known_fitness)))
        self.fitness_type = config['software']['fitness']

        # execution-related parameters
        self.setup_performed = False
        self.setup_cmd = None
        self.setup_timeout = None
        self.setup_output = None
        self.compile_cmd = None
        self.compile_timeout = None
        self.compile_output = None
        self.test_cmd = None
        self.test_timeout = None
        self.test_output = None
        self.run_cmd = None
        self.run_timeout = None
        self.run_output = None

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
        if 'setup_output' in config['software']:
            if config['software']['setup_output'].lower() in ['', 'none']:
                self.setup_output = None
            else:
                self.setup_output = float(config['software']['setup_output'])

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
        if 'compile_output' in config['software']:
            if config['software']['compile_output'].lower() in ['', 'none']:
                self.compile_output = None
            else:
                self.compile_output = float(config['software']['compile_output'])

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
        if 'test_output' in config['software']:
            if config['software']['test_output'].lower() in ['', 'none']:
                self.test_output = None
            else:
                self.test_output = float(config['software']['test_output'])

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
        if 'run_output' in config['software']:
            if config['software']['run_output'].lower() in ['', 'none']:
                self.run_output = None
            else:
                self.run_output = float(config['software']['run_output'])

    def get_engine(self, target_file):
        for (pattern, engine) in self.engine_rules:
            if any([target_file == pattern,
                    pattern == '*',
                    pattern.startswith('*') and target_file.endswith(pattern[1:]),
            ]):
                return engine
        raise RuntimeError('Unknown engine for target file {}'.format(target_file))

    def evaluate_local(self):
        cwd = os.getcwd()
        work_path = os.path.join(self.work_dir, self.basename)
        run_result = magpie.base.RunResult('UNKNOWN_ERROR')
        try:
            # go to work directory
            os.chdir(work_path)

            # one-time setup
            if not self.setup_performed:
                self.setup_performed = True
                # run "[software] setup_cmd" if provided
                if self.setup_cmd:
                    # make sure this is the unmodified software
                    for filename in self.target_files:
                        engine = self.get_engine(filename)
                        assert engine.dump(self.local_contents[filename]) == engine.dump(self.contents[filename])

                    # setup
                    cli = self.compute_local_cli('setup')
                    setup_cmd = '{} {}'.format(self.setup_cmd, cli).strip()
                    timeout = self.setup_timeout or magpie_config.default_timeout
                    max_output = self.setup_output or magpie_config.default_output
                    exec_result = self.exec_cmd(shlex.split(setup_cmd),
                                                timeout=timeout,
                                                max_output=max_output)
                    run_result.status = exec_result.status
                    run_result.debug = exec_result
                    if run_result.status == 'SUCCESS':
                        self.process_setup_exec(run_result, exec_result)
                    if run_result.status != 'SUCCESS':
                        run_result.status = 'SETUP_{}'.format(run_result.status)
                        return run_result

                    # sync work directory
                    self.sync_folder(self.path, work_path)

            # run "[software] compile_cmd" if provided
            if self.compile_cmd:
                cli = self.compute_local_cli('compile')
                compile_cmd = '{} {}'.format(self.compile_cmd, cli).strip()
                timeout = self.compile_timeout or magpie_config.default_timeout
                max_output = self.compile_output or magpie_config.default_output
                exec_result = self.exec_cmd(shlex.split(compile_cmd),
                                            timeout=timeout,
                                            max_output=max_output)
                run_result.status = exec_result.status
                run_result.debug = exec_result
                if run_result.status == 'SUCCESS':
                    self.process_compile_exec(run_result, exec_result)
                if run_result.status != 'SUCCESS':
                    run_result.status = 'COMPILE_{}'.format(run_result.status)
                    return run_result

            # run "[software] test_cmd" if provided
            if self.test_cmd:
                cli = self.compute_local_cli('test')
                test_cmd = '{} {}'.format(self.test_cmd, cli).strip()
                timeout = self.test_timeout or magpie_config.default_timeout
                max_output = self.test_output or magpie_config.default_output
                exec_result = self.exec_cmd(shlex.split(test_cmd),
                                            timeout=timeout,
                                            max_output=max_output)
                run_result.status = exec_result.status
                run_result.debug = exec_result
                if run_result.status == 'SUCCESS':
                    self.process_test_exec(run_result, exec_result)
                if run_result.status != 'SUCCESS':
                    run_result.status = 'TEST_{}'.format(run_result.status)
                    return run_result

            # when fitness is computed from test_cmd, run_cmd is irrelevant
            if self.fitness_type in ['repair', 'bloat']:
                return run_result

            # run "[software] run_cmd" if provided
            if self.run_cmd:
                cli = self.compute_local_cli('run')
                run_cmd = '{} {}'.format(self.run_cmd, cli).strip()
                timeout = self.run_timeout or magpie_config.default_timeout
                max_output = self.run_output or magpie_config.default_output
                exec_result = self.exec_cmd(shlex.split(run_cmd),
                                            timeout=timeout,
                                            max_output=max_output)
                run_result.status = exec_result.status
                run_result.debug = exec_result
                if run_result.status == 'SUCCESS':
                    self.process_run_exec(run_result, exec_result)
                if run_result.status != 'SUCCESS':
                    run_result.status = 'RUN_{}'.format(run_result.status)
        finally:
            # make sure to go back to main directory
            os.chdir(cwd)
        return run_result

    def process_setup_exec(self, run_result, exec_result):
        # "[software] setup_cmd" must yield nonzero return code
        if exec_result.return_code != 0:
            run_result.status = 'CODE_ERROR'

    def process_compile_exec(self, run_result, exec_result):
        # "[software] compile_cmd" must yield nonzero return code
        if exec_result.return_code != 0:
            run_result.status = 'CODE_ERROR'

    def process_test_exec(self, run_result, exec_result):
        # if "[software] fitness" is "repair", we check STDOUT for the number of failed test cases
        if self.fitness_type == 'repair':
            stdout = exec_result.stdout.decode(magpie.config.output_encoding)
            matches = re.findall(r'\b(\d+) (?:fail|error)', stdout)
            fails = 0
            if matches:
                for m in matches:
                    try:
                        fails += float(m)
                    except ValueError:
                        run_result.status = 'PARSE_ERROR'
                run_result.fitness = fails
                return
            matches = re.findall(r'\b(\d+) (?:pass)', stdout)
            if matches:
                run_result.fitness = 0
            else:
                run_result.status = 'PARSE_ERROR'

        # in all other cases "[software] test_cmd" must just yield nonzero return code
        elif exec_result.return_code != 0:
            run_result.status = 'CODE_ERROR'
            return

        # if "[software] fitness" is one of "bloat_*", we can count here
        if self.fitness_type == 'bloat_lines':
            run_result.fitness = 0
            for filename in self.target_files:
                with open(self.get_engine(filename).renamed_contents_file(filename)) as target:
                    run_result.fitness += len(target.readlines())
        elif self.fitness_type == 'bloat_words':
            run_result.fitness = 0
            for filename in self.target_files:
                with open(self.get_engine(filename).renamed_contents_file(filename)) as target:
                    run_result.fitness += sum(len(s.split()) for s in target.readlines())
        elif self.fitness_type == 'bloat_chars':
            run_result.fitness = 0
            for filename in self.target_files:
                with open(self.get_engine(filename).renamed_contents_file(filename)) as target:
                    run_result.fitness += sum(len(s) for s in target.readlines())

    def process_run_exec(self, run_result, exec_result):
        # in all cases "[software] run_cmd" must yield nonzero return code
        if exec_result.return_code != 0:
            run_result.status = 'CODE_ERROR'
            return

        # if "[software] fitness" is "output", we check STDOUT for the string "MAGPIE_FITNESS:"
        if self.fitness_type == 'output':
            stdout = exec_result.stdout.decode(magpie_config.output_encoding)
            m = re.search('MAGPIE_FITNESS: (.*)', stdout)
            if m:
                try:
                    run_result.fitness = float(m.group(1))
                except ValueError:
                    run_result.status = 'PARSE_ERROR'
            else:
                run_result.status = 'PARSE_ERROR'

        # if "[software] fitness" is "time", we just use time as seen by the main Python process
        elif self.fitness_type == 'time':
            run_result.fitness = round(exec_result.runtime, 4)

        # if "[software] fitness" is "posix_time", we assume a POSIX-compatible output on STDERR
        elif self.fitness_type == 'posix_time':
            stderr = exec_result.stderr.decode(magpie_config.output_encoding)
            m = re.search('real (.*)', stderr)
            if m:
                try:
                    run_result.fitness = float(m.group(1))
                except ValueError:
                    run_result.status = 'PARSE_ERROR'
            else:
                run_result.status = 'PARSE_ERROR'

        # if "[software] fitness" is "perf_time", we assume a perf-like output on STDERR
        elif self.fitness_type == 'perf_time':
            stderr = exec_result.stderr.decode(magpie_config.output_encoding)
            m = re.search('(.*) seconds time elapsed', stderr)
            if m:
                try:
                    run_result.fitness = round(float(m.group(1)), 4)
                except ValueError:
                    run_result.status = 'PARSE_ERROR'
            else:
                run_result.status = 'PARSE_ERROR'

        # if "[software] fitness" is "perf_instructions", we assume a perf-like output on STDERR
        elif self.fitness_type == 'perf_instructions':
            stderr = exec_result.stderr.decode(magpie_config.output_encoding)
            m = re.search('(.*) instructions', stderr)
            if m:
                try:
                    run_result.fitness = int(m.group(1).replace(',', ''))
                except ValueError:
                    run_result.status = 'PARSE_ERROR'
            else:
                run_result.status = 'PARSE_ERROR'

    def self_diagnostic(self, run):
        for step in ['setup', 'compile', 'test', 'run']:
            if run.status == '{}_CLI_ERROR'.format(step.upper()):
                self.logger.info('Unable to run the "{}_cmd" command'.format(step))
                self.logger.info('--> there might be a typo (try it manually)')
                self.logger.info('--> your command might not be found (check your PATH)')
                self.logger.info('--> it might not run from the correct directory (check CWD below)')
            if run.status == '{}_CODE_ERROR'.format(step.upper()):
                self.logger.info('The "{}_cmd" command failed with a nonzero exit code'.format(step))
                self.logger.info('--> try to run it manually')
            if run.status == '{}_PARSE_ERROR'.format(step.upper()):
                self.logger.info('The "{}_cmd" STDOUT/STDERR was invalid'.format(step))
                self.logger.info('--> try to run it manually')
            if run.status == '{}_TIMEOUT'.format(step.upper()):
                self.logger.info('The "{}_cmd" command took too long to run'.format(step))
                self.logger.info('--> consider increasing "{}_timeout"'.format(step))
            if run.status == '{}_LENGTHOUT'.format(step.upper()):
                self.logger.info('The "{}_cmd" command generated too much output'.format(step))
                self.logger.info('--> consider increasing "{}_output"'.format(step))
