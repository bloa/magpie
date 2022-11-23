import copy
import math
import random
import time

from ..base import Algorithm, Patch

class GeneticProgramming(Algorithm):
    def setup(self):
        super().setup()
        self.name = 'Genetic Programming'
        self.config['horizon'] = 1
        self.config['pop_size'] = 10
        self.config['offspring_elitism'] = 0.1
        self.config['offspring_crossover'] = 0.5
        self.config['offspring_mutation'] = 0.4
        self.config['nb_instances'] = None
        self.stats['gen'] = 0

    def aux_log_counter(self):
        return '{} {}'.format(self.stats['gen'], self.stats['steps']+1)

    def run(self):
        try:
            # warmup
            self.hook_warmup()
            self.warmup()

            # start!
            self.hook_start()

            # initial pop
            pop = dict()
            local_best = None
            local_best_fitness = None
            while len(pop) < self.config['pop_size']:
                dist = 1 + int(random.random()*self.config['horizon']-1)
                sol = Patch()
                for _ in range(dist):
                    self.mutate(sol)
                if sol in pop:
                    continue
                run = self.evaluate_patch(sol)
                accept = best = False
                if run.status == 'SUCCESS':
                    if self.dominates(run.fitness, local_best_fitness):
                        self.program.logger.debug(self.program.diff_patch(sol))
                        local_best_fitness = run.fitness
                        local_best = sol
                        accept = True
                        if self.dominates(run.fitness, self.report['best_fitness']):
                            self.report['best_fitness'] = run.fitness
                            self.report['best_patch'] = sol
                            best = True
                self.hook_evaluation(sol, run, accept, best)
                pop[sol] = run
                self.stats['steps'] += 1

            # main loop
            while not self.stopping_condition():
                self.hook_main_loop()
                offsprings = list()
                parents = self.select(pop)
                # elitism
                copy_parents = copy.deepcopy(parents)
                k = int(self.config['pop_size']*self.config['offspring_elitism'])
                for parent in copy_parents[:k]:
                    offsprings.append(parent)
                # crossover
                copy_pop = copy.deepcopy(self.filter(pop))
                copy_parents = copy.deepcopy(parents)
                k = int(self.config['pop_size']*self.config['offspring_crossover'])
                for parent in copy_parents[:k]:
                    sol = random.sample(copy_pop, 1)[0]
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
                    dist = 1 + int(random.random()*self.config['horizon']-1)
                    sol = Patch()
                    for _ in range(dist):
                        self.mutate(sol)
                    if sol in pop:
                        continue
                    offsprings.append(sol)
                # replace
                pop.clear()
                local_best = None
                local_best_fitness = None
                for sol in offsprings:
                    if self.stopping_condition():
                        break
                    run = self.evaluate_patch(sol)
                    accept = best = False
                    if run.status == 'SUCCESS':
                        if self.dominates(run.fitness, local_best_fitness):
                            self.program.logger.debug(self.program.diff_patch(sol))
                            local_best_fitness = run.fitness
                            local_best = sol
                            accept = True
                            if self.dominates(run.fitness, self.report['best_fitness']):
                                self.report['best_fitness'] = run.fitness
                                self.report['best_patch'] = sol
                                best = True
                    self.hook_evaluation(sol, run, accept, best)
                    pop[sol] = run
                    self.stats['steps'] += 1
                # next
                self.stats['gen'] += 1

        except KeyboardInterrupt:
            self.report['stop'] = 'keyboard interrupt'

        finally:
            # the end
            self.hook_end()

    def mutate(self, patch):
        if patch.edits and random.random() < 0.5:
            del patch.edits[random.randrange(0, len(patch.edits))]
        else:
            patch.edits.append(self.program.create_edit())

    def crossover(self, sol1, sol2):
        c = copy.deepcopy(sol1)
        for edit in sol2.edits:
            c.edits.append(edit)
        return c

    def filter(self, pop):
        tmp = {sol for sol in pop if pop[sol].status == 'SUCCESS'}
        return tmp

    def select(self, pop):
        """ returns possible parents ordered by fitness """
        tmp = self.filter(pop)
        tmp = sorted(tmp, key=lambda sol: pop[sol].fitness)
        return tmp

class GeneticProgrammingConcat(GeneticProgramming):
    def setup(self):
        super().setup()
        self.name = 'Genetic Programming (Concat)'

    def crossover(self, sol1, sol2):
        c = copy.deepcopy(sol1)
        for edit in sol2.edits:
            c.edits.append(edit)
        return c

class GeneticProgramming1Point(GeneticProgramming):
    def setup(self):
        super().setup()
        self.name = 'Genetic Programming (1-point)'

    def crossover(self, sol1, sol2):
        c = Patch()
        k1 = random.randint(0, len(sol1.edits))
        k2 = random.randint(0, len(sol2.edits))
        for edit in sol1.edits[:k1]:
            c.edits.append(edit)
        for edit in sol2.edits[k2:]:
            c.edits.append(edit)
        return c

class GeneticProgramming2Point(GeneticProgramming):
    def setup(self):
        super().setup()
        self.name = 'Genetic Programming (2-point)'

    def crossover(self, sol1, sol2):
        c = Patch()
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

class GeneticProgrammingUniformConcat(GeneticProgramming):
    def setup(self):
        super().setup()
        self.name = 'Genetic Programming (uniform+concatenation)'
        self.config['uniform_rate'] = 0.5

    def crossover(self, sol1, sol2):
        c = Patch()
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

class GeneticProgrammingUniformInter(GeneticProgramming):
    def setup(self):
        super().setup()
        self.name = 'Genetic Programming (uniform+interleaved)'
        self.config['uniform_rate'] = 0.5

    def crossover(self, sol1, sol2):
        c = Patch()
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
