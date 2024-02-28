import io
import os
import random

import magpie

class BasicProtocol:
    def __init__(self):
        self.search = None
        self.software = None

    def setup(self, config):
        # shared parameters
        sec = config['search']
        self.search.config['warmup'] = int(sec['warmup'])
        self.search.config['warmup_strategy'] = sec['warmup_strategy']
        self.search.stop['steps'] = int(val) if (val := sec['max_steps']) else None
        self.search.stop['wall'] = int(val) if (val := sec['max_time']) else None
        self.search.stop['fitness'] = int(val) if (val := sec['target_fitness']) else None
        self.search.config['cache_maxsize'] = int(val) if (val := sec['cache_maxsize']) else 0
        self.search.config['cache_keep'] = float(sec['cache_keep'])

        self.search.config['possible_edits'] = []
        for edit in sec['possible_edits'].split():
            for klass in magpie.models.known_edits:
                if klass.__name__ == edit:
                    self.search.config['possible_edits'].append(klass)
                    break
            else:
                raise ValueError(f'Invalid config file: unknown edit type "{edit}" in "[software] possible_edits"')
        if self.search.config['possible_edits'] == []:
            raise ValueError('Invalid config file: "[search] possible_edits" must be non-empty!')

        bins = [[]]
        for s in sec['batch_instances'].splitlines():
            if s == '___':
                if bins[-1]:
                    bins.append([])
            elif s[:5] == 'file:':
                try:
                    with open(os.path.join(config['software']['path'], s[5:])) as bin_file:
                        bins[-1].extend([line for line in [line.strip() for line in bin_file] if line and line[0] != '#'])
                except FileNotFoundError:
                    with open(s[5:]) as bin_file:
                        bins[-1].extend([line for line in [line.strip() for line in bin_file] if line and line[0] != '#'])
            else:
                s.strip()
                if s and s[0] != '#':
                    bins[-1].append(s)
        if len(bins) > 1 and not bins[-1]:
            bins.pop()
        tmp = sec['batch_shuffle'].lower()
        if tmp in ['true', 't', '1']:
            for a in bins:
                random.shuffle(a)
        elif tmp in ['false', 'f', '0']:
            pass
        else:
            raise ValueError('[search] batch_shuffle should be Boolean')
        tmp = sec['batch_bin_shuffle'].lower()
        if tmp in ['true', 't', '1']:
            random.shuffle(bins)
        elif tmp in ['false', 'f', '0']:
            pass
        else:
            raise ValueError('[search] batch_bin_shuffle should be Boolean')
        self.search.config['batch_bins'] = bins
        self.search.config['batch_sample_size'] = int(sec['batch_sample_size'])

        # local search only
        if isinstance(self.search, magpie.algos.LocalSearch):
            sec = config['search.ls']
            self.search.config['delete_prob'] = float(sec['delete_prob'])
            self.search.config['max_neighbours'] = int(val) if (val := sec['max_neighbours']) else None
            self.search.config['when_trapped'] = sec['when_trapped']
            self.search.config['accept_fail'] = sec['accept_fail']
            self.search.config['tabu_length'] = sec['tabu_length']

        # genetic programming only
        if isinstance(self.search, magpie.algos.GeneticProgramming):
            sec = config['search.gp']
            self.search.config['pop_size'] = int(sec['pop_size'])
            self.search.config['delete_prob'] = float(sec['delete_prob'])
            self.search.config['offspring_elitism'] = float(sec['offspring_elitism'])
            self.search.config['offspring_crossover'] = float(sec['offspring_crossover'])
            self.search.config['offspring_mutation'] = float(sec['offspring_mutation'])
            self.search.config['uniform_rate'] = float(sec['uniform_rate'])
            tmp = sec['batch_reset'].lower()
            if tmp in ['true', 't', '1']:
                self.search.config['batch_reset'] = True
            elif tmp in ['false', 'f', '0']:
                self.search.config['batch_reset'] = False
            else:
                raise ValueError('[search.gp] batch_reset should be Boolean')

        # minify only
        if isinstance(self.search, magpie.algos.ValidMinify):
            sec = config['search.minify']
            for key in [
                    'do_cleanup',
                    'do_rebuild',
                    'do_simplify',
            ]:
                tmp = sec[key].lower()
                if tmp in ['true', 't', '1']:
                    self.search.config[key] = True
                elif tmp in ['false', 'f', '0']:
                    self.search.config[key] = False
                else:
                    raise ValueError(f'[search.minify] {key} should be Boolean')
            self.search.config['round_robin_limit'] = int(sec['round_robin_limit'])

        # log config just in case
        with io.StringIO() as ss:
            config.write(ss)
            ss.seek(0)
            self.software.logger.debug(f'==== CONFIG ====\n{ss.read()}')

    def run(self):
        if self.software is None:
            raise AssertionError('Software not specified')
        if self.search is None:
            raise AssertionError('Search not specified')

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
