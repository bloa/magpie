import abc
import copy
import random

import magpie.core
import magpie.utils


class LocalSearch(magpie.core.BasicSOAlgorithm):
    def setup(self):
        super().setup()
        sec = self.software.config['search.ls']
        self.config['delete_prob'] = float(sec['delete_prob'])
        self.config['max_neighbours'] = int(val) if (val := sec['max_neighbours']) else 999999
        self.config['when_trapped'] = sec['when_trapped']

    def reset(self):
        super().reset()
        self.stats['neighbours'] = 0

    def run(self):
        try:
            # warmup
            self.hook_warmup()
            self.warmup()

            # early stop if something went wrong during warmup
            if self.report['stop']:
                return

            # start!
            self.hook_start()

            # main loop
            current_patch = self.report['best_solution']['patch']
            current_fitness = self.report['best_solution']['fitness']
            while not self.stopping_condition():
                self.hook_main_loop()
                current_patch, current_fitness = self.explore(current_patch, current_fitness)

        except KeyboardInterrupt:
            self.report['stop'] = 'keyboard interrupt'

        finally:
            # the end
            self.hook_end()

    @abc.abstractmethod
    def explore(self, current_patch, current_fitness):
        pass

    def mutate(self, patch):
        n = len(patch.edits)
        if n == 0:
            if self.config['delete_prob'] == 1:
                self.report['stop'] = 'trapped'
            else:
                patch.edits.append(self.create_edit(self.software.noop_variant))
        elif random.random() < self.config['delete_prob']:
            del patch.edits[random.randrange(0, n)]
        else:
            patch.edits.append(self.create_edit(self.software.noop_variant))

    def check_if_trapped(self):
        if self.config['max_neighbours'] is None:
            return
        if self.stats['neighbours'] < self.config['max_neighbours']:
            return
        if self.config['when_trapped'] == 'stop':
            self.report['stop'] = 'trapped'
        # TODO: restart, others?


class DummySearch(LocalSearch):
    def explore(self, current_patch, current_fitness):
        self.report['stop'] = 'dummy end'
        return current_patch, current_fitness

magpie.utils.known_algos.append(DummySearch)


class DebugSearch(LocalSearch):
    def explore(self, current_patch, current_fitness):
        debug_patch = self.report['debug_patch']
        for edit in debug_patch.edits:
            # move
            patch = magpie.core.Patch([edit])

            # compare
            variant = magpie.core.BasicVariant(self.software, patch)
            run = self.evaluate_variant(variant, counter=self.aux_log_counter())
            accept = best = False
            if run.status == 'SUCCESS':
                accept = True
                candidate = {'patch': patch, 'fitness': run.fitness, 'diff': variant.diff}
                best = magpie.utils.update_global_best(self.report['best_solution'], candidate)

            # hook
            self.hook_evaluation(variant, run, accept, best)

            # next
            self.stats['steps'] += 1

        self.report['stop'] = 'debug end'
        return current_patch, current_fitness

magpie.utils.known_algos.append(DebugSearch)


class RandomSearch(LocalSearch):
    def setup(self):
        super().setup()
        sec = self.software.config['search.random']
        self.config['delete_prob'] = 0
        self.config['min_size'] = int(sec['min_size'])
        self.config['max_size'] = int(sec['max_size'])
        assert 0 <= self.config['min_size'] <= self.config['max_size']
        self.config['distribution'] = sec['distribution']
        if self.config['min_size'] == self.config['max_size']:
            self.config['distribution'] = 'uniform'
        self.config['decay_prob'] = float(sec['decay_prob'])
        self.config['linear_bias'] = float(sec['linear_bias'])
        if self.config['distribution'] == 'linear' and self.config['linear_bias'] == 0:
            self.config['distribution'] = 'uniform'

    def explore(self, current_patch, current_fitness):
        # move
        patch = magpie.core.Patch()
        match self.config['distribution']:
            case 'uniform':
                target_size = random.randint(self.config['min_size'], self.config['max_size'])

            case 'decay':
                target_size = self.config['min_size']
                while target_size < self.config['max_size']:
                    if random.random() < self.config['decay_prob']:
                        break
                    target_size += 1
            case 'linear':
                sizes = list(range(self.config['min_size'], self.config['max_size'] + 1))
                n = len(sizes)
                weights = [1.0 + self.config['linear_bias']*(2*k/(n-1) - 1) for k in range(n)]
                target_size = random.choices(sizes, weights=weights, k=1)[0]
        while len(patch.edits) < target_size:
            self.mutate(patch)

        # compare
        variant = magpie.core.BasicVariant(self.software, patch)
        run = self.evaluate_variant(variant, counter=self.aux_log_counter())
        accept = False
        best = run.fitness == self.report['best_solution']['fitness']

        # hook
        self.hook_evaluation(variant, run, accept, best)

        # next
        self.stats['steps'] += 1
        return patch, run.fitness

magpie.utils.known_algos.append(RandomSearch)


class RandomWalk(LocalSearch):
    def setup(self):
        super().setup()
        sec = self.software.config['search.ls']
        self.config['accept_fail'] = magpie.utils.str_to_bool(sec['accept_fail'])

    def explore(self, current_patch, current_fitness):
        # move
        patch = copy.deepcopy(current_patch)
        self.mutate(patch)

        # compare
        variant = magpie.core.BasicVariant(self.software, patch)
        run = self.evaluate_variant(variant, counter=self.aux_log_counter())
        accept = self.config['accept_fail'] or run.status == 'SUCCESS'
        best = run.fitness == self.report['best_solution']['fitness']

        # accept
        if accept:
            current_patch = patch
            current_fitness = run.fitness
            self.stats['neighbours'] = 0
        else:
            self.stats['neighbours'] += 1
            self.check_if_trapped()

        # hook
        self.hook_evaluation(variant, run, accept, best)

        # next
        self.stats['steps'] += 1
        return current_patch, current_fitness

magpie.utils.known_algos.append(RandomWalk)


class FirstImprovement(LocalSearch):
    def reset(self):
        super().reset()
        self.local_tabu = set()

    def explore(self, current_patch, current_fitness):
        # move
        while True:
            patch = copy.deepcopy(current_patch)
            self.mutate(patch)
            if patch not in self.local_tabu:
                break

        # compare
        variant = magpie.core.BasicVariant(self.software, patch)
        run = self.evaluate_variant(variant, counter=self.aux_log_counter())
        accept = run.status == 'SUCCESS' and not magpie.utils.dominates(current_fitness, run.fitness)
        best = run.fitness == self.report['best_solution']['fitness']

        # accept
        if accept:
            current_patch = patch
            current_fitness = run.fitness
            self.local_tabu.clear()
            self.stats['neighbours'] = 0
        else:
            if len(patch.edits) < len(current_patch.edits):
                self.local_tabu.add(patch)
            self.stats['neighbours'] += 1
            self.check_if_trapped()

        # hook
        self.hook_evaluation(variant, run, accept, best)

        # next
        self.stats['steps'] += 1
        return current_patch, current_fitness

magpie.utils.known_algos.append(FirstImprovement)


class BestImprovement(LocalSearch):
    def reset(self):
        super().reset()
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
        variant = magpie.core.BasicVariant(self.software, patch)
        run = self.evaluate_variant(variant, counter=self.aux_log_counter())
        accept = False
        if run.status == 'SUCCESS':
            if not magpie.utils.dominates(current_fitness, run.fitness):
                if not magpie.utils.dominates(self.local_best_fitness, run.fitness):
                    accept = True
                    self.local_best_patch = patch
                    self.local_best_fitness = run.fitness
        best = run.fitness == self.report['best_solution']['fitness']

        # accept
        if self.stats['neighbours'] >= self.config['max_neighbours']:
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
            if len(patch.edits) < len(current_patch.edits):
                self.local_tabu.add(patch)
            self.stats['neighbours'] += 1
            self.check_if_trapped()

        # hook
        self.hook_evaluation(variant, run, accept, best)

        # next
        self.stats['steps'] += 1
        return current_patch, current_fitness

magpie.utils.known_algos.append(BestImprovement)


class WorstImprovement(LocalSearch):
    def reset(self):
        super().reset()
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
        variant = magpie.core.BasicVariant(self.software, patch)
        run = self.evaluate_variant(variant, counter=self.aux_log_counter())
        accept = False
        if run.status == 'SUCCESS':
            if not magpie.utils.dominates(current_fitness, run.fitness):
                if not magpie.utils.dominates(self.local_worst_fitness, run.fitness):
                    accept = True
                    self.local_worst_patch = patch
                    self.local_worst_fitness = run.fitness
        best = run.fitness == self.report['best_solution']['fitness']

        # accept
        if self.stats['neighbours'] >= self.config['max_neighbours']:
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
            if len(patch.edits) < len(current_patch.edits):
                self.local_tabu.add(patch)
            self.stats['neighbours'] += 1
            self.check_if_trapped()

        # hook
        self.hook_evaluation(variant, run, accept, best)

        # next
        self.stats['steps'] += 1
        return current_patch, current_fitness

magpie.utils.known_algos.append(WorstImprovement)


class TabuSearch(BestImprovement):
    def setup(self):
        super().setup()
        sec = self.software.config['search.ls']
        self.config['tabu_length'] = sec['tabu_length']

    def reset(self):
        super().reset()
        self.tabu_list = [magpie.core.Patch()] # queues are not iterable
        self.local_tabu = set()

    def explore(self, current_patch, current_fitness):
        # move
        while True:
            patch = copy.deepcopy(current_patch)
            self.mutate(patch)
            if patch not in self.tabu_list and patch not in self.local_tabu:
                break

        # compare
        variant = magpie.core.BasicVariant(self.software, patch)
        run = self.evaluate_variant(variant, counter=self.aux_log_counter())
        accept = False
        if run.status == 'SUCCESS':
            if not magpie.utils.dominates(self.local_best_fitness, run.fitness):
                accept = True
                self.local_best_patch = patch
                self.local_best_fitness = run.fitness
        best = run.fitness == self.report['best_solution']['fitness']

        # accept
        if self.stats['neighbours'] >= self.config['max_neighbours']:
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
            if len(patch.edits) < len(current_patch.edits):
                self.local_tabu.add(patch)
            self.stats['neighbours'] += 1
            self.check_if_trapped()

        # hook
        self.hook_evaluation(variant, run, accept, best)

        # next
        self.stats['steps'] += 1
        return current_patch, current_fitness

magpie.utils.known_algos.append(TabuSearch)
