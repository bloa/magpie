import configparser
import io
import pathlib

import magpie

from .basic_protocol import BasicProtocol
from .patch import Patch

class SearchProtocol(BasicProtocol):
    def __init__(self, scenario_file):
        super().__init__(scenario_file)
        self.summary = {
            'stop': None,
            'best_solution': None,
            'best_solutions': [],
        }

    def setup(self):
        super().setup()

        self.search = magpie.utils.algo_from_string(self.config['search']['algorithm'])(self.config)
        self.software = magpie.utils.software_from_string(self.config['software']['software'])(self.config)
        self.search.software = self.software

    def run(self):
        # control ANSI characters in output
        fancy = magpie.settings.color_output
        logger = self.software.logger

        # log config just in case
        with io.StringIO() as ss:
            config = configparser.ConfigParser(interpolation=None)
            config.read_dict(self.config)
            config.write(ss)
            ss.seek(0)
            header = magpie.utils.format_header('CONFIG', fancy)
            logger.debug('%s\n%s', header, ss.read())

        # run the algorithm a single time
        header = magpie.utils.format_header(f'SEARCH: {self.search.__class__.__name__}', fancy)
        logger.info(header)
        self.search.run()
        self.summary.update(self.search.report)

    def report(self):
        # control ANSI characters in output
        fancy = magpie.settings.color_output
        logger = self.software.logger

        logger.info('')
        header = magpie.utils.format_header('REPORT', fancy)
        logger.info(header)

        # main report
        logger.info('Termination: %s', self.summary['stop'])
        for handler in logger.handlers:
            if handler.__class__.__name__ == 'FileHandler':
                path = pathlib.Path(handler.baseFilename).resolve()
                cwd = pathlib.Path.cwd().resolve()
                if path.is_relative_to(cwd):
                    path = path.relative_to(cwd)
                logger.info('Log file: %s', path)
        solution = self.summary['reference_solution']
        if solution['fitness']:
            tmp = solution['fitness']
            if not isinstance(tmp, list):
                tmp = [tmp]
            logger.info('[ref] fitness: %s', ' '.join([magpie.settings.log_format_fitness.format(x) for x in tmp]))
            logger.debug('[ref] fitness (raw): %s', ' '.join([str(x) for x in tmp]))
        solution = self.summary['best_solution']
        if solution['patch'] and solution['patch'].edits:
            tmp = solution['fitness']
            if not isinstance(tmp, list):
                tmp = [tmp]
            logger.info('[best] fitness: %s', ' '.join([magpie.settings.log_format_fitness.format(x) for x in tmp]))
            logger.debug('[best] fitness (raw): %s', ' '.join([str(x) for x in tmp]))
        for (i, solution) in enumerate(self.summary['best_solutions']):
            if solution['patch'] and solution['patch'].edits:
                tmp = solution['fitness']
                if not isinstance(tmp, list):
                    tmp = [tmp]
                logger.info('[best-%d] fitness: %s', i, ' '.join([magpie.settings.log_format_fitness.format(x) for x in tmp]))
                logger.debug('[best-%d] fitness (raw): %s', i, ' '.join([str(x) for x in tmp]))

        # reference solution (usually empty patch)
        solution = self.summary['reference_solution']
        if solution['patch'] and solution['patch'].edits:
            logger.info('')
            header = magpie.utils.format_header('[REF] PATCH', fancy)
            logger.info('%s\n%s', header, solution['patch'])

            logger.info('')
            header = magpie.utils.format_header('[REF] DIFF', fancy)
            diff = magpie.utils.format_diff(self.summary['diff'][:], fancy)
            logger.info('%s\n%s', header, diff)

        # best solution (single objective)
        solution = self.summary['best_solution']
        if solution['patch'] and solution['patch'].edits:
            logger.info('')
            header = magpie.utils.format_header('[BEST] PATCH', fancy)
            logger.info('%s\n%s', header, solution['patch'])
            logger.info('')
            header = magpie.utils.format_header('[BEST] DIFF', fancy)
            diff = magpie.utils.format_diff(solution['diff'][:], fancy)
            logger.info('%s\n%s', header, diff)

            # for convenience, save best patch and diff to separate files
            base_path = pathlib.Path(magpie.settings.log_dir) / self.software.run_label
            patch_file = f'{base_path}.best.patch'
            diff_file = f'{base_path}.best.diff'
            logger.info('[best] patch file: %s', patch_file)
            logger.info('[best] diff file: %s', diff_file)
            with pathlib.Path(patch_file).open('w') as f:
                f.write(str(solution['patch']) + '\n')
            with pathlib.Path(diff_file).open('w') as f:
                f.write(solution['diff'])

        # best solutions (multi objective)
        for (i, solution) in enumerate(self.summary['best_solutions']):
            if solution['patch'] and solution['patch'].edits:
                logger.info('')
                header = magpie.utils.format_header(f'[BEST-{i}] PATCH', fancy)
                logger.info('%s\n%s', header, solution['patch'])
                logger.info('')
                header = magpie.utils.format_header(f'[BEST-{i}] DIFF', fancy)
                diff = magpie.utils.format_diff(solution['diff'][:], fancy)
                logger.info('%s\n%s', header, diff)

                # for convenience, save best patch and diff to separate files
                base_path = pathlib.Path(magpie.settings.log_dir) / self.software.run_label
                patch_file = f'{base_path}.best-{i}.patch'
                diff_file = f'{base_path}.best-{i}.diff'
                logger.info('[best-%d] patch file: %s', i, patch_file)
                logger.info('[best-%d] diff file: %s', i, diff_file)
                with pathlib.Path(patch_file).open('w') as f:
                    f.write(str(solution['patch']) + '\n')
                with pathlib.Path(diff_file).open('w') as f:
                    f.write(solution['diff'])

    def cleanup(self):
        # cleanup temporary software copies
        self.software.clean_work_dir()

magpie.utils.known_protocols.append(SearchProtocol)


class SearchPatchProtocol(SearchProtocol):
    def setup(self, patch):
        super().setup()

        # setup patch
        if patch.endswith('.patch'):
            with pathlib.Path(patch).open('r') as f:
                patch = f.read().strip()
        self.search.debug_patch = Patch.from_string(patch)

magpie.utils.known_protocols.append(SearchPatchProtocol)
