from abc import ABC, abstractmethod
import random
import os
import time

from .. import config as magpie_config
from .patch import Patch

class Algorithm(ABC):
    def __init__(self):
        self.setup()

    def setup(self):
        self.config = {}
        self.config['warmup'] = 3
        self.config['warmup_strategy'] = 'last'
        self.config['cache_maxsize'] = 40
        self.config['cache_keep'] = 0.2
        self.config['possible_edits'] = []
        self.stop = {}
        self.stop['wall'] = None # seconds
        self.stop['steps'] = None
        self.stop['budget'] = None
        self.stop['fitness'] = None
        self.reset()

    def reset(self):
        self.stats = {}
        self.stats['cache_hits'] = 0
        self.stats['cache_misses'] = 0
        self.stats['budget'] = 0
        self.stats['steps'] = 0
        self.report = {}
        self.report['initial_patch'] = None
        self.report['initial_fitness'] = None
        self.report['best_fitness'] = None
        self.report['best_patch'] = None
        self.report['stop'] = None
        self.cache_reset()

    @abstractmethod
    def run(self):
        pass

    def hook_warmup(self):
        self.stats['wallclock_start'] = time.time()
        self.program.logger.info('==== WARMUP ====')

    def hook_warmup_evaluation(self, count, patch, run):
        self.aux_log_eval(count, run.status, ' ', run.fitness, None, None, run.log)
        self.program.logger.debug(run)
        if run.status != 'SUCCESS':
            self.program.logger.info('!*'*40)
            self.program.logger.info('Magpie stopped because it was unable to run the (unmodified) target software')
            self.program.logger.info('Self-diagnostic:')
            self.program.self_diagnostic(run)
            self.program.logger.info('!*'*40)
            self.program.logger.info('CWD: {}'.format(os.path.join(self.program.work_dir, self.program.basename)))
            self.program.logger.info('CMD: {}'.format(run.debug.cmd))
            self.program.logger.info('STDOUT:\n{}'.format(run.debug.stdout.decode(magpie_config.output_encoding)))
            self.program.logger.info('STDERR:\n{}'.format(run.debug.stderr.decode(magpie_config.output_encoding)))
            self.program.logger.info('!*'*40)

    def hook_start(self):
        if not self.config['possible_edits']:
            raise RuntimeError('possible_edits list is empty')
        self.stats['wallclock_start'] = time.time() # discards warmup time
        self.program.logger.info('==== START: {} ===='.format(self.__class__.__name__))


    def hook_main_loop(self):
        pass

    def hook_evaluation(self, patch, run, accept=False, best=False):
        if best:
            c = '*'
        elif accept:
            c = '+'
        else:
            c = ' '
        self.program.logger.debug(patch)
        self.program.logger.debug(run)
        counter = self.aux_log_counter()
        self.aux_log_eval(counter, run.status, c, run.fitness, self.report['initial_fitness'], len(patch.edits), run.log)
        if accept or best:
            self.program.logger.debug(self.program.diff_patch(patch)) # recomputes contents but meh
        elif run.log == 'wtf': # DEBUG
            self.program.logger.info(self.program.diff_patch(patch))

    def aux_log_eval(self, counter, status, c, fitness, baseline, patch_size, data):
        if fitness is not None and baseline is not None:
            if isinstance(fitness, list):
                s = '({}%)'.format('% '.join([str(round(100*fitness[k]/baseline[k], 2)) for k in range(len(fitness))]))
            else:
                s = '({}%)'.format(round(100*fitness/baseline, 2))
        else:
            s = ''
        if patch_size is not None:
            s2 = '[{} edit(s)] '.format(patch_size)
        else:
            s2 = ''
        self.program.logger.info('{:<7} {:<20} {:>1}{:<24}{}'.format(counter, status, c, str(fitness) + ' ' + s + ' ' + s2, data))

    def aux_log_counter(self):
        return str(self.stats['steps']+1)

    def hook_end(self):
        self.stats['wallclock_end'] = time.time()
        self.stats['wallclock_total'] = self.stats['wallclock_end'] - self.stats['wallclock_start']
        if self.report['best_patch']:
            self.report['diff'] = self.program.diff_patch(self.report['best_patch'])
        self.program.logger.info('==== END ====')
        self.program.logger.info('Reason: {}'.format(self.report['stop']))

    def create_edit(self):
        edit = random.choice(self.config['possible_edits']).create(self.program)
        tries = magpie_config.edit_retries
        while tries > 0:
            if edit.target is not None:
                return edit
            tries -= 1
            edit = random.choice(self.config['possible_edits']).create(self.program)
        raise RuntimeError('unable to create edit')

    def warmup(self):
        empty_patch = Patch()
        if self.report['initial_patch'] is None:
            self.report['initial_patch'] = empty_patch
        warmup_values = []
        for i in range(max(self.config['warmup'] or 1, 1), 0, -1):
            self.program.base_fitness = None
            self.program.truth_table = {}
            run = self.evaluate_patch(empty_patch, force=True)
            l = 'INITIAL' if i == 1 else 'WARM'
            self.hook_warmup_evaluation('WARM', empty_patch, run)
            if run.status != 'SUCCESS':
                raise RuntimeError('initial solution has failed')
            warmup_values.append(run.fitness)
        if self.config['warmup_strategy'] == 'last':
            current_fitness = warmup_values[-1]
        elif self.config['warmup_strategy'] == 'min':
            current_fitness = min(warmup_values)
        elif self.config['warmup_strategy'] == 'max':
            current_fitness = max(warmup_values)
        elif self.config['warmup_strategy'] == 'mean':
            current_fitness = sum(warmup_values)/len(warmup_values)
        elif self.config['warmup_strategy'] == 'median':
            current_fitness = sorted(warmup_values)[len(warmup_values)//2]
        else:
            raise ValueError('unknown warmup strategy')
        run.fitness = current_fitness
        self.hook_warmup_evaluation('INITIAL', empty_patch, run)
        self.report['initial_fitness'] = current_fitness
        if self.report['best_patch'] is None:
            self.report['best_fitness'] = current_fitness
            self.report['best_patch'] = empty_patch
        else:
            run = self.evaluate_patch(self.report['best_patch'], force=True)
            self.hook_warmup_evaluation('BEST', empty_patch, run)
            if self.dominates(run.fitness, current_fitness):
                self.report['best_fitness'] = run.fitness
            else:
                self.report['best_patch'] = empty_patch
                self.report['best_fitness'] = current_fitness
        if self.program.base_fitness is None:
            self.program.base_fitness = current_fitness

    def evaluate_patch(self, patch, force=False, forget=False):
        contents = self.program.apply_patch(patch)
        diff = None
        if self.config['cache_maxsize'] > 0 and not force:
            diff = self.program.diff_contents(contents)
            run = self.cache_get(diff)
            if run:
                return run
        run = self.program.evaluate_contents(contents)
        if self.config['cache_maxsize'] > 0 and not forget:
            if not diff:
                diff = self.program.diff_contents(contents)
            self.cache_set(diff, run)
        self.stats['budget'] += getattr(run, 'budget', 0) or 0
        return run

    def cache_get(self, diff):
        try:
            run = self.cache[diff]
            self.stats['cache_hits'] += 1
            if self.config['cache_maxsize'] > 0:
                self.cache_hits[diff] += 1
            return run
        except KeyError:
            self.stats['cache_misses'] += 1
            return None

    def cache_set(self, diff, run):
        msize = self.config['cache_maxsize']
        if msize > 0 and len(self.cache_hits) > msize:
            keep = self.config['cache_keep']
            hits = sorted(self.cache.keys(), key=lambda k: 999 if len(k) == 0 else self.cache_hits[k])
            for k in hits[:int(msize*(1-keep))]:
                del self.cache[k]
            self.cache_hits = { p: 0 for p in self.cache.keys()}
        if not diff in self.cache:
            self.cache_hits[diff] = 0
        self.cache[diff] = run

    def cache_copy(self, algo):
        self.cache = algo.cache
        self.cache_hits = algo.cache_hits

    def cache_reset(self):
        self.cache = {}
        self.cache_hits = {}

    def dominates(self, fit1, fit2):
        if fit1 is None:
            return False
        if fit2 is None:
            return True
        if isinstance(fit1, list):
            for x,y in zip(fit1, fit2):
                if x < y:
                    return True
                if x > y:
                    return False
            return False
        else:
            return fit1 < fit2

    def stopping_condition(self):
        if self.report['stop'] is not None:
            return True
        if self.stop['budget'] is not None:
            if self.stats['budget'] >= self.stop['budget']:
                self.report['stop'] = 'budget'
                return True
        if self.stop['wall'] is not None:
            now = time.time()
            if now >= self.stats['wallclock_start'] + self.stop['wall']:
                self.report['stop'] = 'time budget'
                return True
        if self.stop['steps'] is not None:
            if self.stats['steps'] >= self.stop['steps']:
                self.report['stop'] = 'step budget'
                return True
        if self.stop['fitness'] is not None: # todo: list
            if self.report['best_fitness'] <= self.stop['fitness']:
                self.report['stop'] = 'target fitness reached'
                return True
        return False
