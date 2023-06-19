import copy
import random
import time

from ..base import Patch

from . import LocalSearch

class ValidSearch(LocalSearch):
    def setup(self):
        super().setup()
        self.debug_patch = None

    def hook_warmup(self):
        super().hook_warmup()
        if self.debug_patch is None:
            raise ValueError()

    def hook_start(self):
        super().hook_start()
        self.cleaned_patch = self.do_clean_patch(self.debug_patch)
        self.program.logger.debug('CLEAN_PATCH: {}'.format(str(self.cleaned_patch)))
        self.program.logger.debug('CLEAN_SIZE: %d (was %d)', len(self.cleaned_patch.edits), len(self.debug_patch.edits))
        self.report['best_fitness'] = None
        self.report['best_patch'] = None
        self.report['cleaned_patch'] = self.cleaned_patch

    def do_clean_patch(self, patch):
        cleaned = copy.deepcopy(patch)
        cleaned_diff = self.program.diff_patch(cleaned)
        for (k,edit) in reversed(list(enumerate(cleaned.edits))):
            tmp = copy.deepcopy(cleaned)
            del tmp.edits[k]
            if self.program.diff_patch(tmp) == cleaned_diff:
                del cleaned.edits[k]
                # cleaned_diff = self.program.diff_patch(cleaned) # ???
        return cleaned

    def do_eval_patch(self, patch):
        # eval
        run = self.evaluate_patch(patch)

        # accept
        accept = best = False
        if run.status == 'SUCCESS':
            accept = True
            if (self.dominates(run.fitness, self.report['best_fitness']) or (run.fitness == self.report['best_fitness'] and len(patch.edits) < len(self.report['best_patch'].edits))):
                self.report['best_fitness'] = run.fitness
                self.report['best_patch'] = patch
                best = True

        # hook
        self.hook_evaluation(patch, run, accept, best)

        # next
        self.stats['steps'] += 1

        return run


class ValidSingle(ValidSearch):
    def setup(self):
        super().setup()
        self.name = 'Validation Single'

    def explore(self, current_patch, current_fitness):
        # eval every single patch
        for edit in self.debug_patch.edits:
            patch = Patch([edit])
            self.do_eval_patch(patch)

        self.report['stop'] = 'validation end'
        return current_patch, current_fitness


class ValidTest(ValidSearch):
    def setup(self):
        super().setup()
        self.name = 'Validation Ranking'

    def explore(self, current_patch, current_fitness):
        # full patch only
        self.do_eval_patch(self.cleaned_patch)

        self.report['stop'] = 'validation end'
        return current_patch, current_fitness


class ValidRanking(ValidSearch):
    def setup(self):
        super().setup()
        self.name = 'Validation Ranking'

    def explore(self, current_patch, current_fitness):
        # full patch first
        if self.debug_patch.edits:
            self.do_eval_patch(self.debug_patch)
        else:
            self.report['stop'] = 'validation end (empty patch)'
            return current_patch, current_fitness

        # ranking
        ranking = list()
        for edit in self.debug_patch.edits:
            patch = Patch([edit])
            run = self.do_eval_patch(patch)
            ranking.append((edit, run.fitness))
        ranking.sort(key=lambda c: c[1] or float('inf'))

        if ranking[0][1] > self.report['initial_fitness']:
            self.report['stop'] = 'validation end (all bad)'
            return current_patch, current_fitness

        # rebuild
        rebuild = Patch()
        rebuild_fitness = None
        for (k,(edit,fit)) in enumerate(ranking):
            # move
            patch = copy.deepcopy(rebuild)
            patch.edits.append(edit)

            # compare
            if k == 0:
                rebuild.edits.append(edit)
                rebuild_fitness = fit
                continue
            run = self.do_eval_patch(patch)
            if run.status == 'SUCCESS' and self.dominates(run.fitness, rebuild_fitness):
                rebuild_fitness = run.fitness
                rebuild.edits.append(edit)

        self.report['stop'] = 'validation end'
        return current_patch, current_fitness


class ValidSimplify(ValidSearch):
    def setup(self):
        super().setup()
        self.name = 'Validation Simplify'

    def explore(self, current_patch, current_fitness):
        # full patch first
        if self.debug_patch.edits:
            run = self.do_eval_patch(self.debug_patch)
        else:
            self.report['stop'] = 'validation end (empty patch)'
            return current_patch, current_fitness

        # round robin simplify
        n = len(self.report['best_patch'].edits)+1
        last_i = 0
        while n > len(self.report['best_patch'].edits):
            n = len(self.report['best_patch'].edits)
            for i in range(n):
                patch = Patch([e for (j, e) in enumerate(self.report['best_patch'].edits) if (j+last_i)%n != i])
                run = self.do_eval_patch(patch)
                if run.fitness == self.report['best_fitness']:
                    self.report['best_patch'] = patch # accept because smaller
                    last_i = i # round robin
                    break

        self.report['stop'] = 'validation end'
        return current_patch, current_fitness


class ValidRankingSimplify(ValidSearch):
    def setup(self):
        super().setup()
        self.name = 'Validation Simplify'

    def explore(self, current_patch, current_fitness):
        # full patch first
        if self.debug_patch.edits:
            run = self.do_eval_patch(self.debug_patch)
        else:
            self.report['stop'] = 'validation end (empty patch)'
            return current_patch, current_fitness

        # ranking
        self.program.logger.info('-- ranking --')
        ranking = list()
        for edit in self.debug_patch.edits:
            patch = Patch([edit])
            run = self.do_eval_patch(patch)
            ranking.append((edit, run.fitness))
        ranking.sort(key=lambda c: c[1] or float('inf'))

        # rebuild
        if ranking[0][1] < self.report['initial_fitness']:
            self.program.logger.info('-- rebuild --')
            rebuild = Patch([ranking[0][0]])
            rebuild_fitness = ranking[0][1]
            for (edit,fit) in ranking[1:]:
                patch = copy.deepcopy(rebuild)
                patch.edits.append(edit)
                run = self.do_eval_patch(patch)
                if run.status == 'SUCCESS' and self.dominates(run.fitness, rebuild_fitness):
                    rebuild_fitness = run.fitness
                    rebuild.edits.append(edit)

        # round robin simplify
        self.program.logger.info('-- simplify --')
        n = len(self.report['best_patch'].edits)+1
        last_i = 0
        while n > len(self.report['best_patch'].edits):
            n = len(self.report['best_patch'].edits)
            for i in range(n):
                patch = Patch([e for (j, e) in enumerate(self.report['best_patch'].edits) if (j+last_i)%n != i])
                run = self.do_eval_patch(patch)
                if run.status == 'SUCCESS' and run.fitness == self.report['best_fitness']:
                    self.report['best_patch'] = patch # accept because smaller
                    last_i = i # round robin
                    break

        self.report['stop'] = 'validation end'
        return current_patch, current_fitness
