import os

import magpie


# ================================================================================
# Experimental protocol
# ================================================================================

class ExpProtocol:
    def __init__(self):
        self.search = None
        self.program = None

    def run(self):
        if self.program is None:
            raise AssertionError('Program not specified')
        if self.search is None:
            raise AssertionError('Search not specified')

        self.search.program = self.program

        logger = self.program.logger
        result = {'stop': None, 'best_patch': []}
        self.search.run()
        result.update(self.search.report)
        result['diff'] = self.program.diff_patch(result['best_patch'])
        logger.info('')

        logger.info('==== REPORT ====')
        logger.info('Termination: {}'.format(result['stop']))
        for handler in logger.handlers:
            if handler.__class__.__name__ == 'FileHandler':
                logger.info('Log file: {}'.format(handler.baseFilename))
        if result['best_patch']:
            logger.info('Best fitness: {}'.format(result['best_fitness']))
            logger.info('Best patch: {}'.format(result['best_patch']))
            base_path = os.path.join(magpie.config.log_dir, self.program.run_label)
            with open('{}.patch'.format(base_path), 'w') as f:
                f.write(str(result['best_patch'])+"\n")
            logger.info('Diff:\n{}'.format(result['diff']))
            with open('{}.diff'.format(base_path), 'w') as f:
                f.write(result['diff'])
        self.program.clean_work_dir()


# ================================================================================
# ExampleProgram
# ================================================================================

class ExampleProgram(magpie.base.Program):
    def __init__(self, config):
        self.base_init(config['software']['path'])
        self.possible_edits = [
            magpie.line.LineReplacement,
            magpie.line.LineInsertion,
            magpie.line.LineDeletion,
        ]
        self.target_files = config['software']['target_files'].split()
        if 'compile_cmd' in config['software']:
            self.compile_cmd = config['software']['compile_cmd']
        if 'test_cmd' in config['software']:
            self.test_cmd = config['software']['test_cmd']
        if 'run_cmd' in config['software']:
            self.run_cmd = config['software']['run_cmd']
        self.reset_timestamp()
        self.reset_logger()
        self.reset_contents()

    def get_engine(self, target_file):
        if target_file[-7:] == '.params':
            return magpie.params.ConfigFileParamsEngine
        elif target_file[-4:] == '.xml':
            return magpie.xml.XmlEngine
        else:
            return magpie.line.LineEngine


# ================================================================================

def setup_magpie(config):
    if 'magpie' in config:
        if 'log_dir' in config['magpie']:
            magpie.config.log_dir = config['magpie']['log_dir']
        if 'work_dir' in config['magpie']:
            magpie.config.log_dir = config['magpie']['work_dir']
        if 'local_original_copy' in config['magpie']:
            magpie.config.local_original_copy = config['magpie']['local_original_copy']
        if 'local_original_name' in config['magpie']:
            magpie.config.local_original_copy = config['magpie']['local_original_name']
        if 'output_encoding' in config['magpie']:
            magpie.config.output_encoding = config['magpie']['output_encoding']
        if 'edit_retries' in config['magpie']:
            magpie.config.edit_retries = config['magpie']['edit_retries']
        if 'default_timeout' in config['magpie']:
            magpie.config.default_timeout = float(config['magpie']['default_timeout'])
        if 'default_output' in config['magpie']:
            if config['magpie']['default_output'] == '':
                magpie.config.default_output = None
            else:
                magpie.config.default_output = float(config['magpie']['default_output'])
        if 'diff_method' in config['magpie']:
            magpie.config.diff_method = config['magpie']['diff_method']

def setup_protocol(protocol, config):
    setup_search(protocol.search, config)
    setup_program(protocol.program, config)

def setup_program(program, config):
    if 'software' in config:
        if 'compile_timeout' in config['software']:
            if config['software']['compile_timeout'] != '':
                program.compile_timeout = float(config['software']['compile_timeout'])
        if 'compile_output' in config['software']:
            if config['software']['compile_output'] == '':
                program.compile_output = None
            else:
                program.compile_output = float(config['software']['compile_output'])
        if 'test_timeout' in config['software']:
            if config['software']['test_timeout'] != '':
                program.test_timeout = float(config['software']['test_timeout'])
        if 'test_output' in config['software']:
            if config['software']['test_output'] == '':
                program.test_output = None
            else:
                program.test_output = float(config['software']['test_output'])
        if 'run_timeout' in config['software']:
            if config['software']['run_timeout'] != '':
                program.run_timeout = float(config['software']['run_timeout'])
        if 'run_output' in config['software']:
            if config['software']['run_output'] == '':
                program.run_output = None
            else:
                program.run_output = float(config['software']['run_output'])

def setup_search(search, config):
    if 'search' in config:
        # warmup
        if 'warmup' in config['search']:
            search.config['warmup'] = int(config['search']['warmup'])
        if 'warmup_strategy' in config['search']:
            search.config['warmup_strategy'] = config['search']['warmup_strategy']
        # stopping criteria
        if 'max_steps' in config['search']:
            search.stop['steps'] = int(config['search']['max_steps'])
        if 'max_time' in config['search']:
            search.stop['wall'] = int(config['search']['max_time'])
        if 'target_fitness' in config['search']:
            search.stop['fitness'] = int(config['search']['target_fitness'])
        # cache
        if 'cache_maxsize' in config['search']:
            search.config['cache_maxsize'] = int(config['search']['cache_maxsize'])
        if 'cache_keep' in config['search']:
            search.config['cache_keep'] = float(config['search']['cache_keep'])
