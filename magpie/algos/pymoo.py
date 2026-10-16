import abc
import random

import numpy as np

import magpie

import pymoo.algorithms.moo.moead
import pymoo.algorithms.moo.nsga2
import pymoo.core.crossover
import pymoo.core.duplicate
import pymoo.core.mutation
import pymoo.core.problem
import pymoo.core.sampling
import pymoo.optimize
import pymoo.util.ref_dirs
import pymoo.termination
import pymoo.termination.collection

pymoo.config.Config.warnings['not_compiled'] = False

class PymooProblem(pymoo.core.problem.ElementwiseProblem):
    def __init__(self, software, algorithm):
        super().__init__(n_var=1, n_obj=len(software.fitness_trees), n_ieq_constr=0)
        self.software = software
        self.algorithm = algorithm

    def _evaluate(self, x, out, *args, **kwargs):
        if self.algorithm.stopping_condition():
            out['F'] = [np.inf for _ in self.software.fitness_trees]
            return
        patch = x[0]
        variant = magpie.core.BasicVariant(self.software, patch)
        run = self.algorithm.evaluate_variant(variant, counter='?')
        accept = best = False
        if run.status == 'SUCCESS':
            best = run.fitness in [sol['fitness'] for sol in self.algorithm.report['best_solutions']]
            out['F'] = run.fitness
        else:
            out['F'] = [np.inf for _ in self.software.fitness_trees]
        self.algorithm.hook_evaluation(variant, run, accept, best)
        self.algorithm.stats['steps'] += 1

class PymooSampling(pymoo.core.sampling.Sampling):
    def __init__(self, software, algorithm):
        super().__init__()
        self.software = software
        self.algorithm = algorithm

    def _do(self, problem, n_samples, **kwargs):
        X = np.full((n_samples, 1), None, dtype=object)
        for i in range(n_samples):
            patch = magpie.core.Patch()
            patch.edits.append(self.algorithm.create_edit(self.software.noop_variant))
            X[i, 0] = patch
        return X

class PymooCrossover(pymoo.core.crossover.Crossover):
    def __init__(self):
        super().__init__(2, 2)

    def _do(self, problem, X, **kwargs):
        _, n_matings, _ = X.shape
        Y = np.full_like(X, None, dtype=object)
        for k in range(n_matings):
            a, b = X[0, k, 0], X[1, k, 0]
            c, d = magpie.core.Patch(), magpie.core.Patch()
            k1 = random.randint(0, len(a.edits))
            k2 = random.randint(0, len(b.edits))
            c.edits.extend(a.edits[:k1])
            c.edits.extend(b.edits[k2:])
            d.edits.extend(b.edits[:k2])
            d.edits.extend(a.edits[k1:])
            Y[0, k, 0], Y[1, k, 0] = c, d
        return Y

class PymooMutation(pymoo.core.mutation.Mutation):
    def __init__(self, algorithm):
        super().__init__()
        self.algorithm = algorithm

    def _do(self, problem, X, **kwargs):
        for i in range(len(X)):
            self.algorithm.mutate(X[i, 0])
        return X

class PymooDuplicateElimination(pymoo.core.duplicate.ElementwiseDuplicateElimination):
    def is_equal(self, a, b):
        return a.X[0] == b.X[0]

class PymooAlgorithm(magpie.core.BasicMOAlgorithm):
    def setup(self):
        super().setup()
        self.delete_prob = 0.5

    def reset(self):
        super().reset()
        self.stats['gen'] = None

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
            self.pymoo()

        except KeyboardInterrupt:
            self.report['stop'] = 'keyboard interrupt'

        finally:
            # the end
            self.hook_end()

    @abc.abstractmethod
    def pymoo(self):
        pass

    def _termination(self):
        tmp = []
        if self.stop['wall']:
            tmp.append(pymoo.termination.get_termination('time', self.stop['wall']))
        if self.stop['steps']:
            tmp.append(pymoo.termination.get_termination('n_gen', self.stop['steps']))
        if self.stop['gens']:
            tmp.append(pymoo.termination.get_termination('n_evals', self.stop['gens']))
        return pymoo.termination.collection.TerminationCollection(*tmp)

    def mutate(self, patch):
        n = len(patch.edits)
        if n == 0:
            if self.delete_prob == 1:
                self.report['stop'] = 'trapped'
            else:
                patch.edits.append(self.create_edit(self.software.noop_variant))
        elif random.random() < self.delete_prob:
            del patch.edits[random.randrange(0, n)]
        else:
            patch.edits.append(self.create_edit(self.software.noop_variant))

class PymooNsgaii(PymooAlgorithm):
    def setup(self):
        super().setup()
        sec = self.software.config['search.nsgaii']
        self.delete_prob = float(sec['delete_prob'])
        self.pop_size = int(sec['pop_size'])

    def reset(self):
        super().reset()
        self.stats['gen'] = 0

    def pymoo(self):
        problem = PymooProblem(self.software, self)

        algorithm = pymoo.algorithms.moo.nsga2.NSGA2(
            pop_size=self.pop_size,
            sampling=PymooSampling(self.software, self),
            crossover=PymooCrossover(),
            mutation=PymooMutation(self),
            eliminate_duplicates=PymooDuplicateElimination()
        )
        algorithm.setup(problem, termination=self._termination(), verbose=False)
        while algorithm.has_next() and not self.stopping_condition():
            pop = algorithm.ask()
            algorithm.evaluator.eval(problem, pop)
            algorithm.tell(infills=pop)
            self.stats['gen'] += 1

    def aux_log_counter(self):
        gen = self.stats['gen']
        step = (self.stats['steps']%self.pop_size)+1
        return f'{gen}-{step}'


magpie.utils.known_algos.append(PymooNsgaii)


class PymooMoead(PymooAlgorithm):
    def setup(self):
        super().setup()
        sec = self.software.config['search.moead']
        self.delete_prob = float(sec['delete_prob'])
        self.n_neighbors = int(sec['n_neighbors'])
        self.prob_neighbor_mating = float(sec['prob_neighbor_mating'])
        self.refdirs_strategy = sec['refdirs_strategy']
        self.refdirs_partitions = int(sec['refdirs_partitions'])

        # just in case
        assert len(self.software.fitness_trees) > 1, 'multi-objective'

    def reset(self):
        super().reset()
        self.stats['gen'] = 1

    def pymoo(self):
        problem = PymooProblem(self.software, self)

        ref_dirs = pymoo.util.ref_dirs.get_reference_directions(
            self.refdirs_strategy,
            len(self.software.fitness_trees),
            n_partitions=self.refdirs_partitions,
        )

        algorithm = pymoo.algorithms.moo.moead.MOEAD(
            ref_dirs,
            n_neighbors=self.n_neighbors,
            prob_neighbor_mating=self.prob_neighbor_mating,
            sampling=PymooSampling(self.software, self),
            crossover=PymooCrossover(),
            mutation=PymooMutation(self),
        )

        algorithm.setup(problem, termination=self._termination(), verbose=False)
        while algorithm.has_next() and not self.stopping_condition():
            pop = algorithm.ask()
            algorithm.evaluator.eval(problem, pop)
            algorithm.tell(infills=pop)
            self.stats['gen'] = algorithm.n_gen

    def aux_log_counter(self):
        gen = self.stats['gen']
        step = self.stats['steps'] #%(self.refdirs_partitions+1)+1
        return f'{gen}:{step}'

magpie.utils.known_algos.append(PymooMoead)
