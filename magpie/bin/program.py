import os
import re
import shlex

import magpie

from .. import config as magpie_config


class BasicProgram(magpie.base.AbstractProgram):
    def __init__(self, config):
        # AbstractProgram *requires* a path, a list of target files, and a list of possible edits
        if 'software' not in config:
            raise RuntimeError('Invalid config file: [software] block not found')
        if 'path' not in config['software']:
            raise RuntimeError('Invalid config file: [software] must define a "path" key')
        super().__init__(config['software']['path'])
        if 'target_files' not in config['software']:
            raise RuntimeError('Invalid config file: [software] must define "target_files" key')
        self.target_files = config['software']['target_files'].split()
        if not self.target_files:
            raise RuntimeError('Invalid config file: [software] must define non-empty "target_files" key')
        self.reset_contents()
        if 'possible_edits' in config['software']:
            for edit in config['software']['possible_edits'].split():
                if edit == 'LineReplacement':
                    self.possible_edits.append(magpie.line.LineReplacement)
                elif edit == 'LineInsertion':
                    self.possible_edits.append(magpie.line.LineInsertion)
                elif edit == 'LineDeletion':
                    self.possible_edits.append(magpie.line.LineDeletion)
                elif edit == 'LineMoving':
                    self.possible_edits.append(magpie.line.LineMoving)
                elif edit == 'ParamSetting':
                    self.possible_edits.append(magpie.params.ParamSetting)
                else:
                    raise RuntimeError('Invalid config file: unknown edit type "{}" in "[software] possible_edits"'.format(edit))
        if not self.possible_edits:
            raise RuntimeError('Invalid config file: [software] must define non-empty "possible_edits" key')

        # fitness type
        if 'fitness' not in config['software']:
            raise RuntimeError('Invalid config file: [software] must define non-empty "fitness" key')
        known_fitness = ['output', 'time', 'posix_time', 'perf_time', 'perf_instructions', 'repair', 'bloat_lines', 'bloat_words', 'bloat_chars']
        if config['software']['fitness'] not in known_fitness:
            raise RuntimeError('Invalid config file: [software] "fitness" key must be {}'.format('/'.join(known_fitness)))
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
        if target_file[-7:] == '.params':
            return magpie.params.ConfigFileParamsEngine
        elif target_file[-4:] == '.xml':
            return magpie.xml.XmlEngine
        else:
            return magpie.line.LineEngine

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
                    assert self.local_contents == self.contents

                    # setup
                    timeout = self.setup_timeout or magpie_config.default_timeout
                    max_output = self.setup_output or magpie_config.default_output
                    exec_result = self.exec_cmd(shlex.split(self.setup_cmd),
                                                timeout=timeout,
                                                max_output=max_output)
                    run_result.status = exec_result.status
                    if run_result.status == 'SUCCESS':
                        self.process_setup_exec(run_result, exec_result)
                    if run_result.status != 'SUCCESS':
                        run_result.status = 'SETUP_{}'.format(run_result.status)
                        return run_result

                    # sync work directory
                    self.sync_folder(self.path, work_path)


            # run "[software] compile_cmd" if provided
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
                    run_result.status = 'COMPILE_{}'.format(run_result.status)
                    return run_result

            # update command lines if needed
            cli = ''
            for target in self.target_files:
                engine = self.engines[target]
                if issubclass(engine, magpie.params.AbstractParamsEngine):
                    cli = '{} {}'.format(cli, engine.resolve_cli(self.local_contents[target]))

            # run "[software] test_cmd" if provided
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
                    run_result.status = 'TEST_{}'.format(run_result.status)
                    return run_result

            # when fitness is computed from test_cmd, run_cmd is irrelevant
            if self.fitness_type in ['repair', 'bloat']:
                return run_result

            # run "[software] run_cmd" if provided
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
                if run_result.status != 'SUCCESS':
                    run_result.status = 'RUN_{}'.format(run_result.status)
        finally:
            # make sure to go back to main directory
            os.chdir(cwd)
        return run_result

    def process_setup_exec(self, run_result, exec_result):
        # "[software] setup_cmd" must yield nonzero return code
        if exec_result.return_code != 0:
            run_result.debug = exec_result
            run_result.status = 'CODE_ERROR'

    def process_compile_exec(self, run_result, exec_result):
        # "[software] compile_cmd" must yield nonzero return code
        if exec_result.return_code != 0:
            run_result.debug = exec_result
            run_result.status = 'CODE_ERROR'

    def process_test_exec(self, run_result, exec_result):
        # if "[software] fitness" is "repair", we check STDOUT for the number of failed test cases
        if self.fitness_type == 'repair':
            stdout = exec_result.stdout.decode(magpie.config.output_encoding)
            matches = re.findall(' (\d+) (?:fail|error)', stdout)
            fails = 0
            if matches:
                for m in matches:
                    try:
                        fails += float(m)
                    except ValueError:
                        run_result.status = 'PARSE_ERROR'
                run_result.fitness = fails
                return
            matches = re.findall(' (\d+) (?:pass)', stdout)
            if matches:
                run_result.fitness = 0
            else:
                run_result.status = 'PARSE_ERROR'

        # in all other cases "[software] test_cmd" must just yield nonzero return code
        elif exec_result.return_code != 0:
            run_result.debug = exec_result
            run_result.status = 'CODE_ERROR'
            return

        # if "[software] fitness" is one of "bloat_*", we can count here
        elif self.fitness_type == 'bloat_lines':
            run_result.fitness = 0
            for filename in self.target_files:
                with open(filename) as target:
                    run_result.fitness += len(target.readlines())
        elif self.fitness_type == 'bloat_words':
            run_result.fitness = 0
            for filename in self.target_files:
                with open(filename) as target:
                    run_result.fitness += sum(len(s.split()) for s in target.readlines())
        if self.fitness_type == 'bloat_chars':
            run_result.fitness = 0
            for filename in self.target_files:
                with open(filename) as target:
                    run_result.fitness += sum(len(s) for s in target.readlines())

    def process_run_exec(self, run_result, exec_result):
        # in all cases "[software] run_cmd" must yield nonzero return code
        if exec_result.return_code != 0:
            run_result.debug = exec_result
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
                    run_result.debug = exec_result
                    run_result.status = 'PARSE_ERROR'
            else:
                run_result.debug = exec_result
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
                    run_result.debug = exec_result
                    run_result.status = 'PARSE_ERROR'
            else:
                run_result.debug = exec_result
                run_result.status = 'PARSE_ERROR'
        # if "[software] fitness" is "perf_time", we assume a perf-like output on STDERR
        elif self.fitness_type == 'perf_time':
            stderr = exec_result.stderr.decode(magpie_config.output_encoding)
            m = re.search('(.*) seconds time elapsed', stderr)
            if m:
                try:
                    run_result.fitness = round(float(m.group(1)), 4)
                except ValueError:
                    run_result.debug = exec_result
                    run_result.status = 'PARSE_ERROR'
            else:
                run_result.debug = exec_result
                run_result.status = 'PARSE_ERROR'
        # if "[software] fitness" is "perf_instructions", we assume a perf-like output on STDERR
        elif self.fitness_type == 'perf_instructions':
            stderr = exec_result.stderr.decode(magpie_config.output_encoding)
            m = re.search('(.*) instructions', stderr)
            if m:
                try:
                    run_result.fitness = int(m.group(1).replace(',', ''))
                except ValueError:
                    run_result.debug = exec_result
                    run_result.status = 'PARSE_ERROR'
            else:
                run_result.debug = exec_result
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