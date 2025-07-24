import copy
import math
import random

import magpie.core
import magpie.utils


class GeneticProgramming(magpie.core.BasicAlgorithm):
    def __init__(self, config):
        super().__init__(config)
        self.name = 'Genetic Programming'
        sec = config['search.gp']
        self.config['pop_size'] = int(sec['pop_size'])
        self.config['delete_prob'] = float(sec['delete_prob'])
        self.config['offspring_elitism'] = float(sec['offspring_elitism'])
        self.config['offspring_crossover'] = float(sec['offspring_crossover'])
        self.config['offspring_mutation'] = float(sec['offspring_mutation'])
        try:
            self.config['batch_reset'] = magpie.utils.str_to_bool(sec['batch_reset'])
        except ValueError as e:
            msg = '[search.gp] batch_reset should be Boolean'
            raise magpie.core.ScenarioError(msg) from e

    def reset(self):
        super().reset()
        self.stats['gen'] = 0

    def aux_log_counter(self):
        gen = self.stats['gen']
        step = self.stats['steps']%self.config['pop_size']+1
        return f'{gen}-{step}'

    def run(self):
        try:
            # warmup
            self.hook_warmup()

            # initial grow first to avoid wasting warmup
            offsprings = []
            tries = magpie.settings.edit_retries
            expected = self.config['pop_size']
            while tries and len(offsprings) < expected:
                sol = magpie.core.Patch()
                self.mutate(sol)
                if sol in offsprings:
                    tries -= 1
                    continue
                offsprings.append(sol)
            got = len(offsprings)
            if got < expected:
                self.report['stop'] = f'unable to fill initial population ({got} unique edits generated < {expected})'
                return

            # actual warmup
            self.warmup()

            # early stop if something went wrong during warmup
            if self.report['stop']:
                return

            # start!
            self.hook_start()

            # initial pop
            pop = {}
            local_best_fitness = None
            for sol in offsprings:
                variant = magpie.core.Variant(self.software, sol)
                with self.software.add_to_env(counter=self.aux_log_counter(), patch=sol):
                    run = self.evaluate_variant(variant)
                accept = best = False
                if run.status == 'SUCCESS':
                    if self.dominates(run.fitness, local_best_fitness):
                        local_best_fitness = run.fitness
                        accept = True
                        if self.dominates(run.fitness, self.report['best_fitness']):
                            self.report['best_fitness'] = run.fitness
                            self.report['best_patch'] = sol
                            best = True
                self.hook_evaluation(variant, run, accept, best)
                pop[sol] = run
                self.stats['steps'] += 1

            # main loop
            while not self.stopping_condition():
                self.stats['gen'] += 1
                self.hook_main_loop()
                offsprings = []
                parents = self.select(pop)
                # elitism
                copy_parents = copy.deepcopy(parents)
                k = int(self.config['pop_size']*self.config['offspring_elitism'])
                for parent in copy_parents[:k]:
                    offsprings.append(parent)
                # crossover
                copy_parents = copy.deepcopy(parents)
                k = int(self.config['pop_size']*self.config['offspring_crossover'])
                for parent in copy_parents[:k]:
                    sol = copy.deepcopy(random.sample(parents, 1)[0])
                    if random.random() > 0.5:
                        sol = self.crossover(parent, sol)
                    else:
                        sol = self.crossover(sol, parent)
                    offsprings.append(sol)
                # mutation
                copy_parents = copy.deepcopy(parents)
                k = int(self.config['pop_size']*self.config['offspring_mutation'])
                for parent in copy_parents[:k]:
                    self.mutate(parent)
                    offsprings.append(parent)
                # regrow
                while len(offsprings) < self.config['pop_size']:
                    sol = magpie.core.Patch()
                    self.mutate(sol)
                    if sol in offsprings:
                        continue # guaranteed to terminate (valid initial population)
                    offsprings.append(sol)
                # replace
                pop.clear()
                local_best_fitness = None
                for sol in offsprings:
                    if self.stopping_condition():
                        break
                    variant = magpie.core.Variant(self.software, sol)
                    with self.software.add_to_env(counter=self.aux_log_counter(), patch=sol):
                        run = self.evaluate_variant(variant)
                    accept = best = False
                    if run.status == 'SUCCESS':
                        if self.dominates(run.fitness, local_best_fitness):
                            local_best_fitness = run.fitness
                            accept = True
                            if self.dominates(run.fitness, self.report['best_fitness']):
                                self.report['best_fitness'] = run.fitness
                                self.report['best_patch'] = sol
                                best = True
                    self.hook_evaluation(variant, run, accept, best)
                    pop[sol] = run
                    self.stats['steps'] += 1

        except KeyboardInterrupt:
            self.report['stop'] = 'keyboard interrupt'

        finally:
            # the end
            self.hook_end()

    def mutate(self, patch):
        if patch.edits and random.random() < self.config['delete_prob']:
            del patch.edits[random.randrange(0, len(patch.edits))]
        else:
            patch.edits.append(self.create_edit(self.software.noop_variant))

    def crossover(self, sol1, sol2):
        c = copy.deepcopy(sol1)
        for edit in sol2.edits:
            c.edits.append(edit)
        return c

    def filter(self, pop):
        return {sol for sol in pop if pop[sol].status == 'SUCCESS'}

    def select(self, pop):
        """ returns possible parents ordered by fitness """
        return sorted(self.filter(pop), key=lambda sol: pop[sol].fitness)

    def hook_main_loop(self):
        if self.config['batch_reset']:
            for a in self.config['batch_bins']:
                random.shuffle(a)
            self.hook_reset_batch()


class GeneticProgrammingConcat(GeneticProgramming):
    def __init__(self, config):
        super().__init__(config)
        self.name = 'Genetic Programming (Concat)'

    def crossover(self, sol1, sol2):
        c = copy.deepcopy(sol1)
        for edit in sol2.edits:
            c.edits.append(edit)
        return c

magpie.utils.known_algos.append(GeneticProgrammingConcat)


class GeneticProgramming1Point(GeneticProgramming):
    def __init__(self, config):
        super().__init__(config)
        self.name = 'Genetic Programming (1-point)'

    def crossover(self, sol1, sol2):
        c = magpie.core.Patch()
        k1 = random.randint(0, len(sol1.edits))
        k2 = random.randint(0, len(sol2.edits))
        for edit in sol1.edits[:k1]:
            c.edits.append(edit)
        for edit in sol2.edits[k2:]:
            c.edits.append(edit)
        return c

magpie.utils.known_algos.append(GeneticProgramming1Point)


class GeneticProgramming2Point(GeneticProgramming):
    def __init__(self, config):
        super().__init__(config)
        self.name = 'Genetic Programming (2-point)'

    def crossover(self, sol1, sol2):
        c = magpie.core.Patch()
        k1 = random.randint(0, len(sol1.edits))
        k2 = random.randint(0, len(sol1.edits))
        k3 = random.randint(0, len(sol2.edits))
        k4 = random.randint(0, len(sol2.edits))
        for edit in sol1.edits[:min(k1, k2)]:
            c.edits.append(edit)
        for edit in sol2.edits[min(k3, k4):max(k3, k4)]:
            c.edits.append(edit)
        for edit in sol1.edits[max(k1, k2):]:
            c.edits.append(edit)
        return c

magpie.utils.known_algos.append(GeneticProgramming2Point)


class GeneticProgrammingUniformConcat(GeneticProgramming):
    def __init__(self, config):
        super().__init__(config)
        self.name = 'Genetic Programming (uniform+concatenation)'
        self.config['uniform_rate'] = float(config['search.gp']['uniform_rate'])

    def crossover(self, sol1, sol2):
        c = magpie.core.Patch()
        for edit in sol1.edits:
            if random.random() > self.config['uniform_rate']:
                c.edits.append(edit)
        for edit in sol2.edits:
            if random.random() > self.config['uniform_rate']:
                c.edits.append(edit)
        if len(c.edits) == 0:
            sol3, sol4 = [sol1, sol2] if random.random() > 0.5 else [sol2, sol1]
            if sol3.edits:
                c.edits.append(random.choice(sol3.edits))
            elif sol4.edits:
                c.edits.append(random.choice(sol4.edits))
        return c

magpie.utils.known_algos.append(GeneticProgrammingUniformConcat)


class GeneticProgrammingUniformInter(GeneticProgramming):
    def __init__(self, config):
        super().__init__(config)
        self.name = 'Genetic Programming (uniform+interleaved)'
        self.config['uniform_rate'] = float(config['search.gp']['uniform_rate'])

    def crossover(self, sol1, sol2):
        c = magpie.core.Patch()
        l1 = [(i/len(sol1.edits), 0) for i in sorted(random.sample(range(len(sol1.edits)), math.ceil(len(sol1.edits)*self.config['uniform_rate'])))]
        l2 = [(i/len(sol2.edits), 1) for i in sorted(random.sample(range(len(sol2.edits)), math.ceil(len(sol2.edits)*self.config['uniform_rate'])))]
        for (x, k) in sorted(l1+l2):
            sol = [sol1, sol2][k]
            edit = sol.edits[int(x*len(sol.edits))]
            c.edits.append(edit)
        if len(c.edits) == 0:
            sol3, sol4 = [sol1, sol2] if random.random() > 0.5 else [sol2, sol1]
            if sol3.edits:
                c.edits.append(random.choice(sol3.edits))
            elif sol4.edits:
                c.edits.append(random.choice(sol4.edits))
        return c

magpie.utils.known_algos.append(GeneticProgrammingUniformInter)
