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

def apply_global_config(config):
    if 'magpie' in config:
        if 'log_dir' in config['magpie']:
            magpie.config.log_dir = config['magpie']['log_dir']
        if 'work_dir' in config['magpie']:
            magpie.config.log_dir = config['magpie']['work_dir']
        if 'local_original_copy' in config['magpie']:
            magpie.config.local_original_copy = config['magpie']['local_original_copy']
        if 'local_original_name' in config['magpie']:
            magpie.config.local_original_copy = config['magpie']['local_original_name']
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

    if 'software' in config:
        if 'compile_timeout' in config['software']:
            magpie.config.compile_timeout = float(config['software']['compile_timeout'])
        if 'compile_output' in config['software']:
            if config['software']['compile_output'] == '':
                magpie.config.compile_output = None
            else:
                magpie.config.compile_output = float(config['software']['compile_output'])
        if 'test_timeout' in config['software']:
            magpie.config.test_timeout = float(config['software']['test_timeout'])
        if 'test_output' in config['software']:
            if config['software']['test_output'] == '':
                magpie.config.test_output = None
            else:
                magpie.config.test_output = float(config['software']['test_output'])
        if 'run_timeout' in config['software']:
            magpie.config.run_timeout = float(config['software']['run_timeout'])
        if 'run_output' in config['software']:
            if config['software']['run_output'] == '':
                magpie.config.run_output = None
            else:
                magpie.config.run_output = float(config['software']['run_output'])

def setup_protocol(protocol, config):
    if 'search' in config:
        if 'warmup' in config['search']:
            protocol.search.config['warmup'] = int(config['search']['warmup'])
        if 'warmup_strategy' in config['search']:
            protocol.search.config['warmup_strategy'] = config['search']['warmup_strategy']
        if 'max_steps' in config['search']:
            protocol.search.stop['steps'] = int(config['search']['max_steps'])
        if 'max_time' in config['search']:
            protocol.search.stop['wall'] = int(config['search']['max_time'])
        if 'target_fitness' in config['search']:
            protocol.search.stop['fitness'] = int(config['search']['target_fitness'])
