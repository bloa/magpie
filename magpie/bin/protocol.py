import os

import magpie

class BasicProtocol:
    def __init__(self):
        self.search = None
        self.program = None

    def run(self):
        if self.program is None:
            raise AssertionError('Program not specified')
        if self.search is None:
            raise AssertionError('Search not specified')

        self.search.program = self.program

        # run the algorithm a single time
        logger = self.program.logger
        result = {'stop': None, 'best_patch': []}
        self.search.run()
        result.update(self.search.report)
        result['diff'] = self.program.diff_patch(result['best_patch'])
        logger.info('')

        # print the report
        logger.info('==== REPORT ====')
        logger.info('Termination: {}'.format(result['stop']))
        for handler in logger.handlers:
            if handler.__class__.__name__ == 'FileHandler':
                logger.info('Log file: {}'.format(handler.baseFilename))
        if result['best_patch']:
            logger.info('Best fitness: {}'.format(result['best_fitness']))
            logger.info('Best patch: {}'.format(result['best_patch']))
            base_path = os.path.join(magpie.config.log_dir, self.program.run_label)
            logger.info('Diff:\n{}'.format(result['diff']))
            # for convenience, save best patch and diff to separate files
            with open('{}.patch'.format(base_path), 'w') as f:
                f.write(str(result['best_patch'])+"\n")
            with open('{}.diff'.format(base_path), 'w') as f:
                f.write(result['diff'])

        # cleanup temporary software copies
        self.program.clean_work_dir()
