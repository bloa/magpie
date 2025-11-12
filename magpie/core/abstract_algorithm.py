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
        self.report['reference_solution'] = {'patch': None, 'fitness': None, 'diff': None}
        self.report['best_solution'] = {'patch': None, 'fitness': None, 'diff': None}
        self.report['best_solutions'] = []
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
        if self.stop['fitness'] and self.report['best_solution']['fitness']:
            if magpie.utils.dominates_or_equal(self.report['best_solution']['fitness'], self.stop['fitness']):
                self.report['stop'] = 'target fitness reached'
                return True
        return False
