import io
import os

import magpie.settings
import magpie.utils.known

class BasicProtocol:
    def __init__(self):
        self.search = None
        self.software = None

    def run(self, config):
        if self.software is None:
            raise AssertionError('Software not specified')
        if self.search is None:
            raise AssertionError('Search not specified')

        # setup search
        self.search.setup_scenario(config)

        # log config just in case
        with io.StringIO() as ss:
            config.write(ss)
            ss.seek(0)
            self.software.logger.debug(f'==== CONFIG ====\n{ss.read()}')

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
        tmp = result['stop']
        logger.info(f'Termination: {tmp}')
        for handler in logger.handlers:
            if handler.__class__.__name__ == 'FileHandler':
                logger.info(f'Log file: {handler.baseFilename}')
        if result['best_patch'] and result['best_patch'].edits:
            base_path = os.path.join(magpie.settings.log_dir, self.software.run_label)
            patch_file = f'{base_path}.patch'
            diff_file = f'{base_path}.diff'
            logger.info(f'Patch file: {patch_file}')
            logger.info(f'Diff file: {diff_file}')
            logger.info(f"Best fitness: {result['best_fitness']}")
            logger.info(f"Best patch: {result['best_patch']}")
            logger.info(f"Diff:\n{result['diff']}")
            # for convenience, save best patch and diff to separate files
            with open(patch_file, 'w') as f:
                f.write(str(result['best_patch'])+"\n")
            with open(diff_file, 'w') as f:
                f.write(result['diff'])

        # cleanup temporary software copies
        self.software.clean_work_dir()

magpie.utils.known_protocols.append(BasicProtocol)
