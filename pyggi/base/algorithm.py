from abc import ABC, abstractmethod
import itertools
import random
import time

class Algorithm(ABC):
    def __init__(self):
        self.setup()

    def setup(self):
        self.config = {}
        self.config['cache'] = True
        self.config['cache_maxsize'] = 40
        self.config['cache_keep'] = 0.2
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

    def hook_start(self):
        self.stats['wallclock_start'] = time.time()
        self.program.logger.info('==== START ====')

    def hook_main_loop(self):
        pass

    def hook_end(self):
        self.stats['wallclock_end'] = time.time()
        self.stats['wallclock_total'] = self.stats['wallclock_end'] - self.stats['wallclock_start']
        self.program.logger.info('==== END ====')
        self.program.logger.info('Reason: {}'.format(self.report['stop']))

    def evaluate_patch(self, patch, force=False, forget=False):
        diff = None
        if self.config['cache'] and not force:
            diff = self.program.diff(patch)
            run = self.cache_get(diff)
            if run:
                return run
        run = self.program.evaluate_patch(patch)
        if self.config['cache'] and not forget:
            if not diff:
                diff = self.program.diff(patch)
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
