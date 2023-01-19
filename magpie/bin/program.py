import os
import shlex

import magpie

from .. import config as magpie_config


class BasicProgram(magpie.base.AbstractProgram):
    def __init__(self, config):
        # AbstractProgram *requires* a path, a list of target files, and a list of possible edits

        # logger isn't available yet
        if 'software' not in config:
            raise RuntimeError('Invalid config file: [software] block not found')
        if 'path' not in config['software']:
            raise RuntimeError('Invalid config file: [software] must define a "path" key')
        super().__init__(config['software']['path'])
        # we can use logger now
        if 'target_files' not in config['software']:
            raise RuntimeError('Invalid config file: [software] must define "target_files" key')
        self.target_files = config['software']['target_files'].split()
        self.reset_contents()
        if 'possible_edits' in config['software']:
            raise NotImplementedError
        else:
            self.possible_edits = [
                magpie.line.LineReplacement,
                magpie.line.LineInsertion,
                magpie.line.LineDeletion,
            ]

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
            self.setup_cmd = config['software']['setup_cmd']
        if 'setup_timeout' in config['software']:
            if config['software']['setup_timeout'] != '':
                self.setup_timeout = float(config['software']['setup_timeout'])
        if 'setup_output' in config['software']:
            if config['software']['setup_output'] != '':
                self.setup_output = float(config['software']['setup_output'])

        # compile
        if 'compile_cmd' in config['software']:
            self.compile_cmd = config['software']['compile_cmd']
        if 'compile_timeout' in config['software']:
            if config['software']['compile_timeout'] != '':
                self.compile_timeout = float(config['software']['compile_timeout'])
        if 'compile_output' in config['software']:
            if config['software']['compile_output'] != '':
                self.compile_output = float(config['software']['compile_output'])

        # test
        if 'test_cmd' in config['software']:
            self.test_cmd = config['software']['test_cmd']
        if 'test_timeout' in config['software']:
            if config['software']['test_timeout'] != '':
                self.test_timeout = float(config['software']['test_timeout'])
        if 'test_output' in config['software']:
            if config['software']['test_output'] != '':
                self.test_output = float(config['software']['test_output'])

        # run
        if 'run_cmd' in config['software']:
            self.run_cmd = config['software']['run_cmd']
        if 'run_timeout' in config['software']:
            if config['software']['run_timeout'] != '':
                self.run_timeout = float(config['software']['run_timeout'])
        if 'run_output' in config['software']:
            if config['software']['run_output'] != '':
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
                    elif run_result.status == 'CLI_ERROR':
                        run_result.status = 'SETUP_CLI'
                    elif run_result.status in ['TIMEOUT', 'LENGTHOUT']:
                        run_result.status = 'SETUP_{}'.format(run_result.status)
                    if run_result.status != 'SUCCESS':
                        return run_result

                    # sync work directory
                    self.sync_folder(self.path, work_path)


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
                elif run_result.status == 'CLI_ERROR':
                    run_result.status = 'COMPILE_CLI'
                elif run_result.status in ['TIMEOUT', 'LENGTHOUT']:
                    run_result.status = 'COMPILE_{}'.format(run_result.status)
                if run_result.status != 'SUCCESS':
                    return run_result

            # update command lines if needed
            cli = ''
            for target in self.target_files:
                engine = self.engines[target]
                if issubclass(engine, magpie.params.AbstractParamsEngine):
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
                elif run_result.status == 'CLI_ERROR':
                    run_result.status = 'TEST_CLI'
                elif run_result.status in ['TIMEOUT', 'LENGTHOUT']:
                    run_result.status = 'TEST_{}'.format(run_result.status)
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
                elif run_result.status == 'CLI_ERROR':
                    run_result.status = 'RUN_CLI'
                elif run_result.status in ['TIMEOUT', 'LENGTHOUT']:
                    run_result.status = 'RUN_{}'.format(run_result.status)
        finally:
            # make sure to go back to main directory
            os.chdir(cwd)
        return run_result

    def process_setup_exec(self, run_result, exec_result):
        if exec_result.return_code != 0:
            run_result.debug = exec_result
            run_result.status = 'SETUP_ERROR'

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

    def self_diagnostic(self, run):
        for step in ['setup', 'compile', 'test', 'run']:
            if run.status == '{}_CLI'.format(step.upper()):
                self.logger.info('Unable to run the "{}_cmd" command'.format(step))
                self.logger.info('--> there might be a typo (try it manually)')
                self.logger.info('--> your command might not be found (check your PATH)')
                self.logger.info('--> it might not run from the correct directory (check CWD below)')
            if run.status == '{}_ERROR'.format(step.upper()):
                self.logger.info('The "{}_cmd" command failed with a nonzero exit code'.format(step))
                self.logger.info('--> try to run it manually')
            if run.status == '{}_TIMEOUT'.format(step.upper()):
                self.logger.info('The "{}_cmd" command took too long to run'.format(step))
                self.logger.info('--> increase {}_timeout'.format(step))
            if run.status == '{}_LENGTHOUT'.format(step.upper()):
                self.logger.info('The "{}_cmd" command generated too much output'.format(step))
                self.logger.info('--> increase {}_output'.format(step))
