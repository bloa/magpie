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
    if 'magpie' not in config:
        return
    if 'compile_timeout' in config['magpie']:
        magpie.config.compile_timeout = float(config['magpie']['compile_timeout'])
    if 'compile_output' in config['magpie']:
        if config['magpie']['compile_output'] == '':
            magpie.config.compile_output = None
        else:
            magpie.config.compile_output = float(config['magpie']['compile_output'])
    if 'test_timeout' in config['magpie']:
        magpie.config.test_timeout = float(config['magpie']['test_timeout'])
    if 'test_output' in config['magpie']:
        if config['magpie']['test_output'] == '':
            magpie.config.test_output = None
        else:
            magpie.config.test_output = float(config['magpie']['test_output'])
    if 'run_timeout' in config['magpie']:
        magpie.config.run_timeout = float(config['magpie']['run_timeout'])
    if 'run_output' in config['magpie']:
        if config['magpie']['run_output'] == '':
            magpie.config.run_output = None
        else:
            magpie.config.run_output = float(config['magpie']['run_output'])

def setup_protocol(protocol, config):
    if 'warmup' in config:
        if 'n' in config['warmup']:
            protocol.search.config['warmup'] = int(config['warmup']['n'])
        if 'strategy' in config['warmup']:
            protocol.search.config['warmup_strategy'] = config['warmup']['strategy']
    if 'search' in config:
        if 'max_iter' in config['search']:
            protocol.search.stop['steps'] = int(config['search']['max_iter'])
        if 'max_time' in config['search']:
            protocol.search.stop['wall'] = int(config['search']['max_time'])
        if 'target_fitness' in config['search']:
            protocol.search.stop['fitness'] = int(config['search']['target_fitness'])
