import copy
import itertools
import random
import time

from pyggi.base import Algorithm, Patch

class LocalSearch(Algorithm):
    def setup(self):
        super().setup()
        self.name = 'Local Search'
        self.config['strategy'] = 'first'
        self.config['warmup'] = 3
        self.config['horizon'] = 1
        self.config['delete_prob'] = 0.5
        self.config['max_neighbours'] = None
        self.config['trapped_strategy'] = 'continue'
        self.config['mutate_strategy'] = None

    def hook_warmup(self):
        self.program.logger.info('==== WARMUP ====')

    def hook_warmup_evaluation(self, count, patch, run):
        self.aux_log_eval(count, run.status, ' ', run.fitness, None, patch)

    def hook_evaluation(self, patch, run, accept, best):
        if best:
            c = '*'
        elif accept:
            c = '+'
        else:
            c = ' '
        self.aux_log_eval(self.stats['steps']+1, run.status, c, run.fitness, self.report['initial_fitness'], patch)
        if accept or best:
            self.program.logger.debug(self.program.diff(patch))

    def aux_log_eval(self, counter, status, c, fitness, baseline, data):
        s = ' ({}%)'.format(round(100*fitness/baseline, 2)) if fitness and baseline else ''
        self.program.logger.info('{}\t{}\t{}{}{}\t{}'.format(counter, status, c, fitness, s, data))

    def run(self):
        # warmup
        self.hook_warmup()
        empty_patch = Patch()
        if self.report['initial_patch'] is None:
            self.report['initial_patch'] = empty_patch
        for i in range(self.config['warmup']+1, 0, -1):
            self.program.base_fitness = None
            self.program.truth_table = {}
            run = self.evaluate_patch(empty_patch, force=True)
            l = 'INITIAL' if i == 1 else 'WARM'
            self.hook_warmup_evaluation(l, empty_patch, run)
            self.program.logger.debug(run)
            assert run.status == 'SUCCESS', 'initial solution has failed'
            current_fitness = run.fitness
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

        # start!
        self.stats['steps'] = 0
        self.stats['neighbours'] = 0
        self.hook_start()

        try:
            # main loop
            current_patch = self.report['best_patch']
            while not self.stopping_condition():
                self.hook_main_loop()
                current_patch, current_fitness = self.explore(current_patch, current_fitness)

        finally:
            # the end
            self.hook_end()

    def mutate(self, patch, force=None):
        if self.config['mutate_strategy'] == 'clean':
            n = len(patch)
            if n > 0:
                for _ in range(random.randint(1, min(n, self.config['horizon']))):
                    patch.remove(random.randrange(0, n))
                    n -= 1
            else:
                self.report['stop'] = 'trapped'
        elif self.config['mutate_strategy'] == 'grow':
            for _ in range(random.randint(1, self.config['horizon'])):
                patch.add(self.program.create_edit(patch))
        else:
            n = len(patch)
            for _ in range(random.randint(1, self.config['horizon'])):
                if n > 0 and random.random() < self.config['delete_prob']:
                    patch.remove(random.randrange(0, n))
                    n -= 1
                else:
                    patch.add(self.program.create_edit(patch))

    def check_if_trapped(self):
        if self.config['max_neighbours'] is None:
            return
        if self.stats['neighbours'] < self.config['max_neighbours']:
            return
        if self.config['trapped_strategy'] == 'fail':
            self.report['stop'] = 'trapped'
        # elif self.config['trapped_strategy'] == 'continue':
        #     pass
        # else:
        #     assert(False, 'unknown strategy: {}'.format(self.config['trapped_strategy']))


class DummySearch(LocalSearch):
    def setup(self):
        super().setup()
        self.name = 'Dummy Search'

    def explore(self, current_patch, current_fitness):
        self.report['stop'] = 'dummy end'
        return current_patch, current_fitness


class DebugSearch(LocalSearch):
    def setup(self):
        super().setup()
        self.name = 'Debug Search'

    def explore(self, current_patch, current_fitness):
        debug_patch = self.report['debug_patch']
        for edit in debug_patch.edit_list:
            # move
            patch = Patch([edit])

            # compare
            run = self.evaluate_patch(patch)
            accept = best = False
            if run.status == 'SUCCESS':
                accept = True
                if self.dominates(run.fitness, self.report['best_fitness']):
                    self.report['best_fitness'] = run.fitness
                    self.report['best_patch'] = patch
                    best = True

            # hook
            self.hook_evaluation(patch, run, accept, best)

            # next
            self.stats['steps'] += 1

        self.report['stop'] = 'debug end'
        return current_patch, current_fitness


class RandomSearch(LocalSearch):
    def setup(self):
        super().setup()
        self.name = 'Random Search'

    def explore(self, current_patch, current_fitness):
        # move
        patch = Patch()
        self.mutate(patch)

        # compare
        run = self.evaluate_patch(patch)
        best = False
        if run.status == 'SUCCESS':
            if self.dominates(run.fitness, self.report['best_fitness']):
                self.report['best_fitness'] = run.fitness
                self.report['best_patch'] = patch
                best = True

        # hook
        self.hook_evaluation(patch, run, False, best)

        # next
        self.stats['steps'] += 1
        return patch, run.fitness


class RandomWalk(LocalSearch):
    def setup(self):
        super().setup()
        self.name = 'Random Walk'
        self.config['accept_fail'] = False

    def explore(self, current_patch, current_fitness):
        # move
        patch = copy.deepcopy(current_patch)
        self.mutate(patch)

        # compare
        run = self.evaluate_patch(patch)
        accept = self.config['accept_fail']
        best = False
        if run.status == 'SUCCESS':
            accept = True
            if self.dominates(run.fitness, self.report['best_fitness']):
                self.report['best_fitness'] = run.fitness
                self.report['best_patch'] = patch
                best = True

        # accept
        if accept:
            current_patch = patch
            current_fitness = run.fitness
            self.stats['neighbours'] = 0
        else:
            self.stats['neighbours'] += 1
            self.check_if_trapped()

        # hook
        self.hook_evaluation(patch, run, accept, best)

        # next
        self.stats['steps'] += 1
        return current_patch, current_fitness


class FirstImprovement(LocalSearch):
    def setup(self):
        super().setup()
        self.name = 'First Improvement'
        self.local_tabu = set()

    def explore(self, current_patch, current_fitness):
        # move
        while True:
            patch = copy.deepcopy(current_patch)
            self.mutate(patch)
            if patch not in self.local_tabu:
                break

        # compare
        run = self.evaluate_patch(patch)
        accept = best = False
        if run.status == 'SUCCESS':
            if not self.dominates(current_fitness, run.fitness):
                accept = True
                if self.dominates(run.fitness, self.report['best_fitness']):
                    self.report['best_fitness'] = run.fitness
                    self.report['best_patch'] = patch
                    best = True

        # accept
        if accept:
            current_patch = patch
            current_fitness = run.fitness
            self.local_tabu.clear()
            self.stats['neighbours'] = 0
        else:
            if len(patch) < len(current_patch):
                self.local_tabu.add(patch)
            self.stats['neighbours'] += 1
            self.check_if_trapped()

        # hook
        self.hook_evaluation(patch, run, accept, best)

        # next
        self.stats['steps'] += 1
        return current_patch, current_fitness


class BestImprovement(LocalSearch):
    def setup(self):
        super().setup()
        self.name = 'Best Improvement'
        self.config['max_neighbours'] = 20
        self.local_best_patch = None
        self.local_best_fitness = None
        self.local_tabu = set()

    def explore(self, current_patch, current_fitness):
        # move
        while True:
            patch = copy.deepcopy(current_patch)
            self.mutate(patch)
            if patch not in self.local_tabu:
                break

        # compare
        run = self.evaluate_patch(patch)
        accept = best = False
        if run.status == 'SUCCESS':
            if not self.dominates(current_fitness, run.fitness):
                if not self.dominates(self.local_best_fitness, run.fitness):
                    self.local_best_patch = patch
                    self.local_best_fitness = run.fitness
                    if self.dominates(run.fitness, self.report['best_fitness']):
                        self.report['best_fitness'] = run.fitness
                        self.report['best_patch'] = patch
                        best = True

        # accept
        accept = self.stats['neighbours'] >= self.config['max_neighbours']
        if accept:
            if self.local_best_patch is not None:
                current_patch = self.local_best_patch
                current_fitness = self.local_best_fitness
                self.local_best_patch = None
                self.local_best_fitness = None
                self.local_tabu.clear()
                self.stats['neighbours'] = 0
            else:
                self.check_if_trapped()
        else:
            if len(patch) < len(current_patch):
                self.local_tabu.add(patch)
            self.stats['neighbours'] += 1
            self.check_if_trapped()

        # hook
        self.hook_evaluation(patch, run, accept, best)

        # next
        self.stats['steps'] += 1
        return current_patch, current_fitness


class WorstImprovement(LocalSearch):
    def setup(self):
        super().setup()
        self.name = 'Worst Improvement'
        self.config['max_neighbours'] = 20
        self.local_worst_patch = None
        self.local_worst_fitness = None
        self.local_tabu = set()

    def explore(self, current_patch, current_fitness):
        # move
        while True:
            patch = copy.deepcopy(current_patch)
            self.mutate(patch)
            if patch not in self.local_tabu:
                break

        # compare
        run = self.evaluate_patch(patch)
        accept = best = False
        if run.status == 'SUCCESS':
            if not self.dominates(current_fitness, run.fitness):
                if not self.dominates(self.local_worst_fitness, run.fitness):
                    self.local_worst_patch = patch
                    self.local_worst_fitness = run.fitness
                if self.dominates(run.fitness, self.report['best_fitness']):
                    self.report['best_fitness'] = run.fitness
                    self.report['best_patch'] = patch
                    best = True

        # accept
        accept = self.stats['neighbours'] >= self.config['max_neighbours']
        if accept:
            if self.local_worst_patch is not None:
                current_patch = self.local_worst_patch
                current_fitness = self.local_worst_fitness
                self.local_worst_patch = None
                self.local_worst_fitness = None
                self.local_tabu.clear()
                self.stats['neighbours'] = 0
            else:
                self.check_if_trapped()
        else:
            if len(patch) < len(current_patch):
                self.local_tabu.add(patch)
            self.stats['neighbours'] += 1
            self.check_if_trapped()

        # hook
        self.hook_evaluation(patch, run, accept, best)

        # next
        self.stats['steps'] += 1
        return current_patch, current_fitness


class TabuSearch(BestImprovement):
    def setup(self):
        super().setup()
        self.name = 'Tabu Search'
        self.config['tabu_length'] = 10
        self.tabu_list = [Patch()] # queues are not iterable
        self.local_tabu = set()

    def explore(self, current_patch, current_fitness):
        # move
        while True:
            patch = copy.deepcopy(current_patch)
            self.mutate(patch)
            if patch not in self.tabu_list and patch not in self.local_tabu:
                break

        # compare
        run = self.evaluate_patch(patch)
        accept = best = False
        if run.status == 'SUCCESS':
            if not self.dominates(self.local_best_fitness, run.fitness):
                self.local_best_patch = patch
                self.local_best_fitness = run.fitness
            if self.dominates(run.fitness, self.report['best_fitness']):
                self.report['best_fitness'] = run.fitness
                self.report['best_patch'] = patch
                best = True

        # accept
        accept = self.stats['neighbours'] >= self.config['max_neighbours']
        if accept:
            if self.local_best_patch is not None:
                current_patch = self.local_best_patch
                current_fitness = self.local_best_fitness
                self.local_best_patch = None
                self.local_best_fitness = None
                self.local_tabu.clear()
                self.stats['neighbours'] = 0
                self.tabu_list.append(self.local_best_patch)
                while len(self.tabu_list) >= self.config['tabu_length']:
                    self.tabu_list.pop(0)
            else:
                self.check_if_trapped()
        else:
            if len(patch) < len(current_patch):
                self.local_tabu.add(patch)
            self.stats['neighbours'] += 1
            self.check_if_trapped()

        # hook
        self.hook_evaluation(patch, run, accept, best)

        # next
        self.stats['steps'] += 1
        return current_patch, current_fitness
