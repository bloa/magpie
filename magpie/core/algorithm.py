from abc import ABC, abstractmethod
import itertools
import random
import os
import time

from .. import config as magpie_config
from .patch import Patch

class AbstractAlgorithm(ABC):
    def __init__(self):
        self.setup()

    def setup(self):
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

    def create_edit(self):
        edit_klass = random.choice(self.config['possible_edits'])
        tries = magpie_config.edit_retries
        while (edit := edit_klass.create(self.software)) is None:
            tries -= 1
            if tries == 0:
                raise RuntimeError('unable to create an edit of class {}'.format(edit_klass.__name__))
        return edit

    def evaluate_patch(self, patch, force=False, forget=False):
        contents = self.software.apply_patch(patch)
        return self.software.evaluate_contents(contents)

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
            if self.report['best_fitness'] is not None:
                if self.report['best_fitness'] <= self.stop['fitness']:
                    self.report['stop'] = 'target fitness reached'
                    return True
        return False
