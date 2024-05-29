import abc
import random
import time

import magpie.settings


class AbstractAlgorithm(abc.ABC):
    def __init__(self):
        self.software = None
        self.config = {}
        self.config['possible_edits'] = []
        self.stop = {}
        self.stop['wall'] = None # seconds
        self.stop['steps'] = None
        self.stop['budget'] = None
        self.stop['fitness'] = None
        self.reset()

    def reset(self):
        self.stats = {}
        self.stats['budget'] = 0
        self.stats['steps'] = 0
        self.stats['wallclock_start'] = time.time() # dummy
        self.report = {}
        self.report['initial_patch'] = None
        self.report['reference_patch'] = None
        self.report['reference_fitness'] = None
        self.report['best_fitness'] = None
        self.report['best_patch'] = None
        self.report['stop'] = None

    @abc.abstractmethod
    def run(self):
        pass

    def create_edit(self, variant=None):
        ref = variant or self.software.noop_variant
        klass = random.choice(self.config['possible_edits'])
        tries = magpie.settings.edit_retries
        while (edit := klass.auto_create(ref)) is None:
            tries -= 1
            if tries == 0:
                msg = f'Unable to create an edit of class {klass.__name__}'
                raise RuntimeError(msg)
        return edit

    def dominates(self, fit1, fit2):
        if fit1 is None:
            return False
        if fit2 is None:
            return True
        if isinstance(fit1, list):
            for i, (x, y) in enumerate(zip(fit1, fit2)):
                if x < y:
                    return not self.software.fitness[i].maximize
                if x > y:
                    return self.software.fitness[i].maximize
            return False
        if self.software.fitness[0].maximize:
            return fit1 > fit2
        else:
            return fit1 < fit2

    def dominates_or_equal(self, fit1, fit2):
        return self.dominates(fit1, fit2) or fit1 == fit2

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
        if self.stop['fitness'] and self.report['best_fitness']:
            if self.dominates_or_equal(self.report['best_fitness'], self.stop['fitness']):
                self.report['stop'] = 'target fitness reached'
                return True
        return False
