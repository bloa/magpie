import io
import pathlib
import re

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
            msg = '==== CONFIG ====\n%s'
            if magpie.settings.color_output:
                msg = f'\033[1m{msg}\033[0m'
            self.software.logger.debug(msg, ss.read())

        # init final result dict
        result = {'stop': None, 'best_patch': None}

        # setup software
        self.search.software = self.software

        logger = self.software.logger

        # run the algorithm a single time
        logger.debug('') # because CONFIG above is also debug
        msg = '==== SEARCH: %s ===='
        if magpie.settings.color_output:
            msg = f'\033[1m{msg}\033[0m'
        logger.info(msg, self.search.__class__.__name__)
        self.search.run()
        result.update(self.search.report)

        # print the report
        logger.info('')
        msg = '==== REPORT ===='
        if magpie.settings.color_output:
            msg = f'\033[1m{msg}\033[0m'
        logger.info(msg)
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
            tmp = result['reference_fitness']
            if not isinstance(tmp, list):
                tmp = [tmp]
            logger.info('Reference fitness: %s', ' '.join([magpie.settings.log_format_fitness.format(x) for x in tmp]))
            tmp = result['best_fitness']
            if not isinstance(tmp, list):
                tmp = [tmp]
            logger.info('Best fitness: %s', ' '.join([magpie.settings.log_format_fitness.format(x) for x in tmp]))

            logger.info('')
            msg = '==== BEST PATCH ====\n%s'
            diff = result['diff']
            if magpie.settings.color_output:
                msg = '\033[1m==== BEST PATCH ====\033[0m\n%s'
                diff = self.color_diff(diff)
            logger.info(msg, result['best_patch'])

            logger.info('')
            msg = '==== DIFF ====\n%s'
            diff = result['diff']
            if magpie.settings.color_output:
                msg = '\033[1m==== DIFF ====\033[0m\n%s'
                diff = self.color_diff(diff)
            logger.info(msg, diff)

            # for convenience, save best patch and diff to separate files
            with pathlib.Path(patch_file).open('w') as f:
                f.write(str(result['best_patch']) + '\n')
            with pathlib.Path(diff_file).open('w') as f:
                f.write(result['diff'])

        # cleanup temporary software copies
        self.software.clean_work_dir()

    @staticmethod
    def color_diff(diff):
        out = diff[:]
        for patt, repl in [
                (r'^(\*\*\*\*.*)$', r'\033[36m\1\033[0m'),
                (r'^(--- .* ----)$', r'\033[36m\1\033[0m'),
                (r'^(\*\*\* .* \*\*\*\*)$', r'\033[36m\1\033[0m'),
                (r'^((?:---|\+\+\+|\*\*\*) .*)$', r'\033[1m\1\033[0m'),
                (r'^(-.*)$', r'\033[31m\1\033[0m'),
                (r'^(\+.*)$', r'\033[32m\1\033[0m'),
                (r'^(!.*)$', r'\033[33m\1\033[0m'),
                (r'^(@@ .* @@)', r'\033[36m\1\033[0m'),
        ]:
            out = re.sub(patt, repl, out, flags=re.MULTILINE)
        return out

magpie.utils.known_protocols.append(BasicProtocol)
