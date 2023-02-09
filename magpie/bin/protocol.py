import os

import magpie
from ..xml import xml_edits
from ..line import line_edits
from ..params import params_edits

class BasicProtocol:
    def __init__(self):
        self.search = None
        self.program = None

    def setup(self, config):
        if 'search' in config:
            # shared parameters
            if 'warmup' in config['search']:
                self.search.config['warmup'] = int(config['search']['warmup'])
            if 'warmup_strategy' in config['search']:
                self.search.config['warmup_strategy'] = config['search']['warmup_strategy']
            if 'max_steps' in config['search']:
                if config['search']['max_steps'].lower() in ['', 'none']:
                    self.search.stop['steps'] = None
                else:
                    self.search.stop['steps'] = int(config['search']['max_steps'])
            if 'max_time' in config['search']:
                if config['search']['max_time'].lower() in ['', 'none']:
                    self.search.stop['wall'] = None
                else:
                    self.search.stop['wall'] = int(config['search']['max_time'])
            if 'target_fitness' in config['search']:
                if config['search']['target_fitness'].lower() in ['', 'none']:
                    self.search.stop['fitness'] = None
                else:
                    self.search.stop['fitness'] = int(config['search']['target_fitness'])
            if 'cache_maxsize' in config['search']:
                if int(config['search']['cache_maxsize']).lower() in ['', 'none']:
                    self.search.config['cache_maxsize'] = 0
                else:
                    self.search.config['cache_maxsize'] = int(config['search']['cache_maxsize'])
            if 'cache_keep' in config['search']:
                self.search.config['cache_keep'] = float(config['search']['cache_keep'])

            if 'possible_edits' in config['search']:
                self.search.config['possible_edits'] = []
                for edit in config['search']['possible_edits'].split():
                    for klass in [*xml_edits, *line_edits, *params_edits]:
                        if klass.__name__ == edit:
                            self.search.config['possible_edits'].append(klass)
                            break
                    else:
                        raise ValueError('Invalid config file: unknown edit type "{}" in "[search] possible_edits"'.format(edit))
            if self.search.config['possible_edits'] == []:
                raise ValueError('Invalid config file: "[search] possible_edits" must be non-empty!')

            # local search only
            if isinstance(self.search, magpie.algo.LocalSearch):
                if 'delete_prob' in config['search']:
                    self.search.config['delete_prob'] = float(config['search']['delete_prob'])
                if 'max_neighbours' in config['search']:
                    if config['search']['max_neighbours'].lower() in ['', 'none']:
                        self.search.config['max_neighbours'] = None
                    else:
                        self.search.config['max_neighbours'] = int(config['search']['max_neighbours'])
                if 'when_trapped' in config['search']:
                    self.search.config['when_trapped'] = config['search']['when_trapped']
            if isinstance(self.search, magpie.algo.RandomWalk):
                if 'accept_fail' in config['search']:
                    self.search.config['accept_fail'] = config['search']['accept_fail']
            if isinstance(self.search, magpie.algo.TabuSearch):
                if 'tabu_length' in config['search']:
                    self.search.config['tabu_length'] = config['search']['tabu_length']

            # genetic programming only
            if isinstance(self.search, magpie.algo.GeneticProgramming):
                if 'pop_size' in config['search']:
                    self.search.config['pop_size'] = int(config['search']['pop_size'])
                if 'delete_prob' in config['search']:
                    self.search.config['delete_prob'] = float(config['search']['delete_prob'])
                if 'offspring_elitism' in config['search']:
                    self.search.config['offspring_elitism'] = float(config['search']['offspring_elitism'])
                if 'offspring_crossover' in config['search']:
                    self.search.config['offspring_crossover'] = float(config['search']['offspring_crossover'])
                if 'offspring_mutation' in config['search']:
                    self.search.config['offspring_mutation'] = float(config['search']['offspring_mutation'])
            if (isinstance(self.search, magpie.algo.GeneticProgrammingUniformConcat) or
                isinstance(self.search, magpie.algo.GeneticProgrammingUniformInter)):
                if 'uniform_rate' in config['search']:
                    self.search.config['uniform_rate'] = float(config['search']['uniform_rate'])


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
