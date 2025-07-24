import configparser
import io
import pathlib

import magpie

from .basic_protocol import BasicProtocol
from .patch import Patch

class SearchProtocol(BasicProtocol):
    def __init__(self, scenario_file):
        super().__init__(scenario_file)
        self.summary = {'stop': None, 'best_patch': None}

    def setup(self):
        super().setup()

        self.search = magpie.utils.algo_from_string(self.config['search']['algorithm'])(self.config)
        self.software = magpie.utils.software_from_string(self.config['software']['software'])(self.config)
        self.search.software = self.software

    def run(self):
        # control ANSI characters in output
        fancy = magpie.settings.color_output

        # log config just in case
        with io.StringIO() as ss:
            config = configparser.ConfigParser(interpolation=None)
            config.read_dict(self.config)
            config.write(ss)
            ss.seek(0)
            header = magpie.utils.format_header('CONFIG', fancy)
            self.software.logger.debug('%s\n%s', header, ss.read())

        # run the algorithm a single time
        header = magpie.utils.format_header(f'SEARCH: {self.search.__class__.__name__}', fancy)
        self.software.logger.info(header)
        self.search.run()
        self.summary.update(self.search.report)

    def report(self):
        # control ANSI characters in output
        fancy = magpie.settings.color_output

        self.software.logger.info('')
        header = magpie.utils.format_header('REPORT', fancy)
        self.software.logger.info(header)
        self.software.logger.info('Termination: %s', self.summary['stop'])
        for handler in self.software.logger.handlers:
            if handler.__class__.__name__ == 'FileHandler':
                self.software.logger.info('Log file: %s', handler.baseFilename)
        if self.summary['best_fitness'] and self.summary['best_patch'] and self.summary['best_patch'].edits:
            base_path = pathlib.Path(magpie.settings.log_dir) / self.software.run_label
            patch_file = f'{base_path}.patch'
            diff_file = f'{base_path}.diff'
            self.software.logger.info('Patch file: %s', patch_file)
            self.software.logger.info('Diff file: %s', diff_file)
            tmp = self.summary['reference_fitness']
            if not isinstance(tmp, list):
                tmp = [tmp]
            self.software.logger.info('Reference fitness: %s', ' '.join([magpie.settings.log_format_fitness.format(x) for x in tmp]))
            self.software.logger.debug('Raw reference fitness: %s', ' '.join([str(x) for x in tmp]))
            tmp = self.summary['best_fitness']
            if not isinstance(tmp, list):
                tmp = [tmp]
            self.software.logger.info('Best fitness: %s', ' '.join([magpie.settings.log_format_fitness.format(x) for x in tmp]))
            self.software.logger.debug('Raw best fitness: %s', ' '.join([str(x) for x in tmp]))

            self.software.logger.info('')
            header = magpie.utils.format_header('BEST PATCH', fancy)
            self.software.logger.info('%s\n%s', header, self.summary['best_patch'])

            self.software.logger.info('')
            header = magpie.utils.format_header('DIFF', fancy)
            diff = magpie.utils.format_diff(self.summary['diff'], fancy)
            self.software.logger.info('%s\n%s', header, diff)

            # for convenience, save best patch and diff to separate files
            with pathlib.Path(patch_file).open('w') as f:
                f.write(str(self.summary['best_patch']) + '\n')
            with pathlib.Path(diff_file).open('w') as f:
                f.write(self.summary['diff'])

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
