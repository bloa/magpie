import io
import pathlib

import magpie.settings
import magpie.utils.known


class BasicProtocol:
    def __init__(self):
        self.search = None
        self.software = None

    def run(self, config):
        if self.software is None:
            msg = 'Software not specified'
            raise AssertionError(msg)
        if self.search is None:
            msg = 'Search not specified'
            raise AssertionError(msg)

        # setup search
        self.search.setup(config)

        # log config just in case
        with io.StringIO() as ss:
            config.write(ss)
            ss.seek(0)
            self.software.logger.debug('==== CONFIG ====\n%s', ss.read())

        # init final result dict
        result = {'stop': None, 'best_patch': None}

        # setup software
        self.search.software = self.software

        # run the algorithm a single time
        self.search.run()
        result.update(self.search.report)

        logger = self.software.logger
        logger.info('')

        # print the report
        logger.info('==== REPORT ====')
        logger.info('Termination: %s', result['stop'])
        for handler in logger.handlers:
            if handler.__class__.__name__ == 'FileHandler':
                logger.info('Log file: %s', handler.baseFilename)
        if result['best_patch'] and result['best_patch'].edits:
            base_path = pathlib.Path(magpie.settings.log_dir) / self.software.run_label
            patch_file = f'{base_path}.patch'
            diff_file = f'{base_path}.diff'
            logger.info('Patch file: %s', patch_file)
            logger.info('Diff file: %s', diff_file)
            logger.info('Reference fitness: %s', result['reference_fitness'])
            logger.info('Best fitness: %s', result['best_fitness'])
            logger.info('Best patch: %s', result['best_patch'])
            logger.info('Diff:\n%s', result['diff'])
            # for convenience, save best patch and diff to separate files
            with pathlib.Path(patch_file).open('w') as f:
                f.write(str(result['best_patch']) + '\n')
            with pathlib.Path(diff_file).open('w') as f:
                f.write(result['diff'])

        # cleanup temporary software copies
        self.software.clean_work_dir()

magpie.utils.known_protocols.append(BasicProtocol)
