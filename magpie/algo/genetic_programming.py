import copy
import math
import random
import time

from ..base import Algorithm, Patch

class GeneticProgramming(Algorithm):
    def setup(self):
        self.name = 'Genetic Programming'
        self.config['warmup'] = 3
        self.config['horizon'] = 1
        self.config['pop_size'] = 10
        self.config['offspring_elitism'] = 0.1
        self.config['offspring_crossover'] = 0.5
        self.config['offspring_mutation'] = 0.4
        self.config['rolling'] = True
        self.config['nb_instances'] = None
        self.stats['gen'] = 0

    def hook_warmup(self):
        self.program.logger.info('==== WARMUP ====')

    def hook_warmup_evaluation(self, count, patch, run):
        self.aux_log_eval(count, run.status, ' ', run.fitness, None, None, patch)

    def hook_evaluation(self, patch, run, best):
        if best:
            c = '*'
        else:
            c = ' '
        self.aux_log_eval('{} {}'.format(self.stats['gen'], self.stats['steps']+1), run.status, c, run.fitness, self.report['initial_fitness'], len(patch.edits), run.log)
        if best:
            self.program.logger.debug(self.program.diff_patch(patch))

    def aux_log_eval(self, counter, status, c, fitness, baseline, patch_size, data):
        if fitness and baseline:
            if isinstance(fitness, list):
                s = ' ({}%)'.format('% '.join([str(round(100*fitness[k]/baseline[k], 2)) for k in range(len(fitness))]))
            else:
                s = ' ({}%)'.format(round(100*fitness/baseline, 2))
        else:
            s = ''
        if patch_size is not None:
            s2 = ' [{} edit(s)]'.format(patch_size)
        else:
            s2 = ''
        self.program.logger.info('{}\t{}\t{}{}{}{}\t{}'.format(counter, status, c, fitness, s, s2, data))

    def run(self):
        # warmup
        self.hook_warmup()
        empty_patch = Patch()
        for i in range(self.config['warmup']+1, 0, -1):
            self.program.base_fitness = None
            self.program.truth_table = {}
            run = self.evaluate_patch(empty_patch, force=True)
            l = 'INITIAL' if i == 1 else 'WARM'
            self.hook_warmup_evaluation(l, empty_patch, run)
            if run.status != 'SUCCESS':
                raise RuntimeError('initial solution has failed')
        self.report['initial_fitness'] = run.fitness
        self.report['best_fitness'] = run.fitness
        self.report['best_patch'] = empty_patch

        # start!
        self.stats['steps'] = 0
        self.hook_start()

        try:
            # initial pop
            pop = dict()
            local_best = None
            local_best_fitness = None
            while len(pop) < self.config['pop_size']:
                dist = 1 + int(random.random()*self.config['horizon']-1)
                sol = copy.deepcopy(empty_patch)
                for _ in range(dist):
                    self.mutate(sol)
                if sol in pop:
                    continue
                run = self.evaluate_patch(sol)
                h = [self.stats['gen'], self.stats['steps']+1, run.status, ' ', run.fitness, sol]
                if run.status == 'SUCCESS':
                    if self.dominates(run.fitness, local_best_fitness):
                        self.program.logger.debug(self.program.diff_patch(sol))
                        local_best_fitness = run.fitness
                        local_best = sol
                        h[3] = '+'
                logger.debug(run)
                logger.info('{}\t{}\t{}\t{}{}\t{}'.format(*h))
                pop[sol] = run
                self.stats['steps'] += 1

            # main loop
            while not self.stopping_condition():
                self.hook_main_loop()
                offsprings = list()
                parents = self.select(pop)
                # elitism
                copy_parents = copy.deepcopy(parents)
                for parent in copy_parents[:self.config['offspring_elitism']]:
                    offsprings.append(parent)
                # crossover
                copy_pop = copy.deepcopy(self.filter(pop))
                copy_parents = copy.deepcopy(parents)
                for parent in copy_parents[:self.config['offspring_crossover']]:
                    sol = random.sample(copy_pop, 1)[0]
                    if random.random() > 0.5:
                        sol = self.crossover(parent, sol)
                    else:
                        sol = self.crossover(sol, parent)
                    offsprings.append(sol)
                # mutation
                copy_parents = copy.deepcopy(parents)
                for parent in copy_parents[:self.config['offspring_mutation']]:
                    self.mutate(parent)
                    offsprings.append(parent)
                # regrow
                while len(offsprings) < self.config['pop_size']:
                    dist = 1 + int(random.random()*self.config['horizon']-1)
                    sol = copy.deepcopy(empty_patch)
                    for _ in range(dist):
                        self.mutate(sol)
                    if sol in pop:
                        continue
                    offsprings.append(sol)
                # update instances
                if self.config['rolling']:
                    self.program.instances = self.sample_instances(self.config['nb_instances'])
                    logger.debug('INSTANCES: %s', repr(self.program.instances))
                    self.program.base_fitness = None
                    self.program.truth_table = {}
                    self.cache_reset()
                    run = self.evaluate_patch(empty_patch)
                    logger.debug(run)
                    logger.info("{}\t{}\t{}".format('INITIAL', run.status, run.fitness))
                    self.report['initial_fitness'] = run.fitness
                    self.report['best_fitness'] = run.fitness
                    self.report['best_patch'] = empty_patch
                # replace
                pop.clear()
                local_best = None
                local_best_fitness = None
                for sol in offsprings:
                    if self.stopping_condition():
                        break
                    run = self.evaluate_patch(sol)
                    h = [self.stats['gen']+1, self.stats['steps']+1, run.status, ' ', run.fitness, sol]
                    if run.status == 'SUCCESS':
                        if self.dominates(run.fitness, local_best_fitness):
                            self.program.logger.debug(self.program.diff_patch(sol))
                            local_best = sol
                            local_best_fitness = run.fitness
                            h[3] = '+'
                    logger.debug(run)
                    logger.info('{}\t{}\t{}\t{}{}\t{}'.format(*h))
                    pop[sol] = run
                    self.stats['steps'] += 1
                if local_best is not None:
                    self.report['best_fitness'] = local_best_fitness
                    self.report['best_patch'] = local_best
                # next
                self.stats['gen'] += 1

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
        tmp = {sol for sol in tmp if pop[sol].percentage < 150}
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
