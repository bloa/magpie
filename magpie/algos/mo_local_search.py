import abc
import copy
import random

import magpie


class MOLocalSearch(magpie.core.BasicMOAlgorithm):
    def setup(self):
        super().setup()
        sec = self.software.config['search.ls']
        self.config['delete_prob'] = float(sec['delete_prob'])
        self.config['max_neighbours'] = int(val) if (val := sec['max_neighbours']) else 999999
        self.config['when_trapped'] = sec['when_trapped']

    def reset(self):
        super().reset()
        self.stats['neighbours'] = 0
        self.local_tabu = set()
        self.archive = []

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
            archive = self.report['best_solutions'][:] or [self.report['best_solution']]
            while not self.stopping_condition():
                self.hook_main_loop()
                archive = self.explore(archive)

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


class MODummySearch(MOLocalSearch):
    def explore(self, archive):
        self.report['stop'] = 'dummy end'
        return archive

magpie.utils.known_algos.append(MODummySearch)


class MORandomSearch(MOLocalSearch):
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

    def explore(self, archive):
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
        best = run.status == 'SUCCESS' and run.fitness in [sol['fitness'] for sol in self.report['best_solutions']]

        # hook
        self.hook_evaluation(variant, run, accept, best)

        # next
        self.stats['steps'] += 1
        return archive

magpie.utils.known_algos.append(MORandomSearch)


class MORandomWalk(MOLocalSearch):
    def setup(self):
        super().setup()
        sec = self.software.config['search.ls']
        self.config['accept_fail'] = magpie.utils.str_to_bool(sec['accept_fail'])

    def explore(self, archive):
        # move
        patch = copy.deepcopy(archive[0]['patch'])
        self.mutate(patch)

        # compare
        variant = magpie.core.BasicVariant(self.software, patch)
        run = self.evaluate_variant(variant, counter=self.aux_log_counter())
        accept = self.config['accept_fail'] or run.status == 'SUCCESS'
        best = run.status == 'SUCCESS' and run.fitness in [sol['fitness'] for sol in self.report['best_solutions']]

        # accept
        if accept:
            archive = [{'patch': patch, 'fitness': run.fitness, 'diff': variant.diff}]
            self.stats['neighbours'] = 0
        else:
            self.stats['neighbours'] += 1
            self.check_if_trapped()

        # hook
        self.hook_evaluation(variant, run, accept, best)

        # next
        self.stats['steps'] += 1
        return archive

magpie.utils.known_algos.append(MORandomWalk)


class MOFirstImprovement(MOLocalSearch):
    def reset(self):
        super().reset()
        self.local_tabu = set()

    def explore(self, archive):
        # move
        while True:
            current_patch = random.choice(archive)['patch']
            patch = copy.deepcopy(current_patch)
            self.mutate(patch)
            if patch not in self.local_tabu:
                break

        # compare
        variant = magpie.core.BasicVariant(self.software, patch)
        run = self.evaluate_variant(variant, counter=self.aux_log_counter())
        candidate = {'patch': patch, 'fitness': run.fitness, 'diff': variant.diff}
        accept = run.status == 'SUCCESS' and magpie.utils.update_archive(archive, candidate)
        best = run.status == 'SUCCESS' and run.fitness in [sol['fitness'] for sol in self.report['best_solutions']]

        # accept
        if accept:
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
        return archive

magpie.utils.known_algos.append(MOFirstImprovement)
