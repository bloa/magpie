import io
import os
import random

import magpie

class BasicProtocol:
    def __init__(self):
        self.search = None
        self.program = None

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
            for klass in [*magpie.xml.edits, *magpie.line.edits, *magpie.params.edits]:
                if klass.__name__ == edit:
                    self.search.config['possible_edits'].append(klass)
                    break
            else:
                raise ValueError('Invalid config file: unknown edit type "{}" in "[software] possible_edits"'.format(edit))
        if self.search.config['possible_edits'] == []:
            raise ValueError('Invalid config file: "[search] possible_edits" must be non-empty!')

        bins = [[]]
        for s in sec['batch_instances'].splitlines():
            if s == '___':
                if not bins[-1]:
                    raise ValueError('Invalid config file: empty bin in "{}"'.format(sec['search']['batch_all_samples']))
                bins.append([])
            elif s[:5] == 'file:':
                try:
                    with open(os.path.join(config['software']['path'], s[5:])) as bin_file:
                        bins[-1].extend([line.rstrip() for line in bin_file])
                except FileNotFoundError:
                    with open(s[5:]) as bin_file:
                        bins[-1].extend([line.rstrip() for line in bin_file])
            else:
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
        if isinstance(self.search, magpie.algo.LocalSearch):
            sec = config['search.ls']
            self.search.config['delete_prob'] = float(sec['delete_prob'])
            self.search.config['max_neighbours'] = int(val) if (val := sec['max_neighbours']) else None
            self.search.config['when_trapped'] = sec['when_trapped']
            self.search.config['accept_fail'] = sec['accept_fail']
            self.search.config['tabu_length'] = sec['tabu_length']

        # genetic programming only
        if isinstance(self.search, magpie.algo.GeneticProgramming):
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
        if isinstance(self.search, magpie.algo.ValidMinify):
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
                    raise ValueError('[search.minify] {} should be Boolean'.format(key))
            self.search.config['round_robin_limit'] = int(sec['round_robin_limit'])

        # log config just in case
        with io.StringIO() as ss:
            config.write(ss)
            ss.seek(0)
            self.program.logger.debug('==== CONFIG ====\n{}'.format(ss.read()))

    def run(self):
        if self.program is None:
            raise AssertionError('Program not specified')
        if self.search is None:
            raise AssertionError('Search not specified')

        # init final result dict
        result = {'stop': None, 'best_patch': []}

        # setup program
        self.search.program = self.program
        try:
            self.program.ensure_contents()
        except RuntimeError as e:
            result['stop'] = str(e)

        if not result['stop']:
            # run the algorithm a single time
            self.search.run()
            result.update(self.search.report)

        logger = self.program.logger
        logger.info('')

        # print the report
        logger.info('==== REPORT ====')
        logger.info('Termination: {}'.format(result['stop']))
        for handler in logger.handlers:
            if handler.__class__.__name__ == 'FileHandler':
                logger.info('Log file: {}'.format(handler.baseFilename))
        if result['best_patch'] and result['best_patch'].edits:
            result['diff'] = self.program.diff_patch(result['best_patch'])
            base_path = os.path.join(magpie.config.log_dir, self.program.run_label)
            logger.info('Patch file: {}'.format('{}.patch'.format(base_path)))
            logger.info('Diff file: {}'.format('{}.diff'.format(base_path)))
            logger.info('Best fitness: {}'.format(result['best_fitness']))
            logger.info('Best patch: {}'.format(result['best_patch']))
            logger.info('Diff:\n{}'.format(result['diff']))
            # for convenience, save best patch and diff to separate files
            with open('{}.patch'.format(base_path), 'w') as f:
                f.write(str(result['best_patch'])+"\n")
            with open('{}.diff'.format(base_path), 'w') as f:
                f.write(result['diff'])

        # cleanup temporary software copies
        self.program.clean_work_dir()
