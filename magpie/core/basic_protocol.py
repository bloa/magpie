import io
import pathlib

import magpie


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

        # control ANSI characters in output
        fancy = magpie.settings.color_output

        # log config just in case
        with io.StringIO() as ss:
            config.write(ss)
            ss.seek(0)
            header = magpie.utils.format_header('CONFIG', fancy)
            self.software.logger.debug('%s\n%s', header, ss.read())

        # init final result dict
        result = {'stop': None, 'best_patch': None}

        # setup software
        self.search.software = self.software

        logger = self.software.logger

        # run the algorithm a single time
        header = magpie.utils.format_header(f'SEARCH: {self.search.__class__.__name__}', fancy)
        logger.info(header)
        self.search.run()
        result.update(self.search.report)

        # print the report
        logger.info('')
        header = magpie.utils.format_header('REPORT', fancy)
        logger.info(header)
        logger.info('Termination: %s', result['stop'])
        for handler in logger.handlers:
            if handler.__class__.__name__ == 'FileHandler':
                logger.info('Log file: %s', handler.baseFilename)
        if result['best_fitness'] and result['best_patch'] and result['best_patch'].edits:
            base_path = pathlib.Path(magpie.settings.log_dir) / self.software.run_label
            patch_file = f'{base_path}.patch'
            diff_file = f'{base_path}.diff'
            logger.info('Patch file: %s', patch_file)
            logger.info('Diff file: %s', diff_file)
            tmp = result['reference_fitness']
            if not isinstance(tmp, list):
                tmp = [tmp]
            logger.info('Reference fitness: %s', ' '.join([magpie.settings.log_format_fitness.format(x) for x in tmp]))
            logger.debug('Raw reference fitness: %s', ' '.join([str(x) for x in tmp]))
            tmp = result['best_fitness']
            if not isinstance(tmp, list):
                tmp = [tmp]
            logger.info('Best fitness: %s', ' '.join([magpie.settings.log_format_fitness.format(x) for x in tmp]))
            logger.debug('Raw best fitness: %s', ' '.join([str(x) for x in tmp]))

            logger.info('')
            header = magpie.utils.format_header('BEST PATCH', fancy)
            logger.info('%s\n%s', header, result['best_patch'])

            logger.info('')
            header = magpie.utils.format_header('DIFF', fancy)
            diff = magpie.utils.format_diff(result['diff'], fancy)
            logger.info('%s\n%s', header, diff)

            # for convenience, save best patch and diff to separate files
            with pathlib.Path(patch_file).open('w') as f:
                f.write(str(result['best_patch']) + '\n')
            with pathlib.Path(diff_file).open('w') as f:
                f.write(result['diff'])

        # cleanup temporary software copies
        self.software.clean_work_dir()

magpie.utils.known_protocols.append(BasicProtocol)
