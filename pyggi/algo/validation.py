import copy
import itertools
import random
import time

from pyggi.base import Algorithm, Patch

from . import LocalSearch

class ValidSearch(LocalSearch):
    def do_clean_patch(self, patch):
        cleaned = copy.deepcopy(patch)
        cleaned_diff = self.program.diff(cleaned)
        for (k,edit) in reversed(list(enumerate(cleaned.edit_list))):
            tmp = copy.deepcopy(cleaned)
            del tmp.edit_list[k]
            if self.program.diff(tmp) == cleaned_diff:
                del cleaned.edit_list[k]
                cleaned_diff = self.program.diff(cleaned)
        return cleaned

    def do_eval_patch(self, patch):
        # eval
        run = self.evaluate_patch(patch)

        # accept
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

        return run


class ValidSingle(ValidSearch):
    def setup(self):
        super().setup()
        self.name = 'Validation Single'
        self.debug_patch = None

    def hook_main_loop(self):
        self.cleaned_patch = self.do_clean_patch(self.debug_patch)
        self.program.logger.debug('CLEAN_PATCH: {}'.format(str(cleaned_patch)))
        self.program.logger.debug('CLEAN_SIZE: %d (was %d)', len(cleaned_patch), len(self.debug_patch))

    def explore(self, current_patch, current_fitness):
        if self.debug_patch is None:
            raise ValueError()
        self.report['best_fitness'] = None
        self.report['best_patch'] = None

        # eval every single patch
        for edit in full_patch.edit_list:
            patch = Patch([edit])
            self.do_eval_patch(patch)

        self.report['stop'] = 'validation end'
        return current_patch, current_fitness


class ValidTest(ValidSearch):
    def setup(self):
        super().setup()
        self.name = 'Validation Ranking'
        self.debug_patch = Patch()

    def explore(self, current_patch, current_fitness):
        if self.debug_patch is None:
            raise ValueError()
        self.cleaned_patch = self.do_clean_patch(self.debug_patch)
        self.program.logger.debug('CLEAN_PATCH: {}'.format(str(self.cleaned_patch)))
        self.program.logger.debug('CLEAN_SIZE: %d (was %d)', len(self.cleaned_patch), len(self.debug_patch))
        self.report['best_fitness'] = None
        self.report['best_patch'] = None
        self.report['cleaned_patch'] = self.cleaned_patch

        # full patch only
        self.do_eval_patch(self.cleaned_patch)

        self.report['stop'] = 'validation end'
        return current_patch, current_fitness


class ValidRanking(ValidSearch):
    def setup(self):
        super().setup()
        self.name = 'Validation Ranking'
        self.debug_patch = None

    def explore(self, current_patch, current_fitness):
        if self.debug_patch is None:
            raise ValueError()
        self.cleaned_patch = self.do_clean_patch(self.debug_patch)
        self.program.logger.debug('CLEAN_PATCH: {}'.format(str(self.cleaned_patch)))
        self.program.logger.debug('CLEAN_SIZE: %d (was %d)', len(self.cleaned_patch), len(self.debug_patch))
        self.report['best_fitness'] = None
        self.report['best_patch'] = None
        self.report['cleaned_patch'] = self.cleaned_patch

        # full patch first
        if self.debug_patch.edit_list:
            self.do_eval_patch(self.debug_patch)
        else:
            self.report['stop'] = 'validation end (empty patch)'
            return current_patch, current_fitness

        # ranking
        ranking = list()
        for edit in self.debug_patch.edit_list:
            patch = Patch([edit])
            run = self.do_eval_patch(patch)
            ranking.append((edit, run.fitness))
        ranking.sort(key=lambda c: c[1])

        if ranking[0][1] > self.report['initial_fitness']:
            self.report['stop'] = 'validation end (all bad)'
            return current_patch, current_fitness

        # rebuild
        rebuild = Patch()
        rebuild_fitness = None
        for (k,(edit,fit)) in enumerate(ranking):
            # move
            patch = copy.deepcopy(rebuild)
            patch.add(edit)

            # compare
            if k == 0:
                rebuild.add(edit)
                rebuild_fitness = fit
                continue
            run = self.do_eval_patch(patch)
            if run.status == 'SUCCESS' and self.dominates(run.fitness, rebuild_fitness):
                rebuild_fitness = run.fitness
                rebuild.add(edit)

        self.report['stop'] = 'validation end'
        return current_patch, current_fitness


class ValidAblation(ValidSearch):
    def setup(self):
        super().setup()
        self.name = 'Validation Ablation'
        self.debug_patch = None

    def explore(self, current_patch, current_fitness):
        if self.debug_patch is None:
            raise ValueError()
        self.cleaned_patch = self.do_clean_patch(self.debug_patch)
        self.program.logger.debug('CLEAN_PATCH: {}'.format(str(self.cleaned_patch)))
        self.program.logger.debug('CLEAN_SIZE: %d (was %d)', len(self.cleaned_patch), len(self.debug_patch))
        self.report['best_fitness'] = None
        self.report['best_patch'] = None
        self.report['cleaned_patch'] = self.cleaned_patch

        # full patch first
        if self.debug_patch.edit_list:
            run = self.do_eval_patch(self.debug_patch)
        else:
            self.report['stop'] = 'validation end (empty patch)'
            return current_patch, current_fitness

        # ranking
        self.program.logger.info('-- ranking --')
        ranking = list()
        for edit in self.debug_patch.edit_list:
            patch = Patch([edit])
            run = self.do_eval_patch(patch)
            if run.fitness:
                ranking.append((edit, run.fitness))
        ranking.sort(key=lambda c: c[1])

        # rebuild
        if ranking[0][1] > self.report['initial_fitness']:
            self.program.logger.info('-- rebuild --')
            rebuild = Patch(ranking[0])
            rebuild_fitness = ranking[0][1]
            for (edit,fit) in ranking[1:]:
                patch = copy.deepcopy(rebuild)
                patch.add(edit)
                run = self.do_eval_patch(patch)
                if run.status == 'SUCCESS' and self.dominates(run.fitness, rebuild_fitness):
                    rebuild_fitness = run.fitness
                    rebuild.add(edit)

        # round robin ablation
        self.program.logger.info('-- ablation --')
        n = len(self.debug_patch.edit_list)+1
        last_i = 0
        while n > len(self.report['best_patch'].edit_list):
            n = len(self.report['best_patch'].edit_list)
            for i in range(n):
                patch = Patch([e for (j, e) in enumerate(self.report['best_patch'].edit_list) if (j+last_i)%n != i])
                run = self.do_eval_patch(patch)
                if run.fitness == self.report['best_fitness']:
                    self.report['best_patch'] = patch # accept because smaller
                    last_i = i # round robin
                    break

        self.report['stop'] = 'validation end'
        return current_patch, current_fitness
