import copy
import random
import time

from magpie.core import Patch

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
        self.report['best_fitness'] = None
        self.report['best_patch'] = None

    def do_clean_patch(self, patch):
        cleaned = copy.deepcopy(patch)
        cleaned_diff = self.software.diff_patch(cleaned)
        for (k,edit) in reversed(list(enumerate(cleaned.edits))):
            tmp = copy.deepcopy(cleaned)
            del tmp.edits[k]
            if self.software.diff_patch(tmp) == cleaned_diff:
                del cleaned.edits[k]
                # cleaned_diff = self.software.diff_patch(cleaned) # ???
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
        self.name = 'Validation Full'

    def explore(self, current_patch, current_fitness):
        # full patch only
        self.do_eval_patch(self.debug_patch)

        self.report['stop'] = 'validation end'
        return current_patch, current_fitness


class ValidMinify(ValidSearch):
    def setup(self):
        super().setup()
        self.name = 'Minify Patch'
        self.config['do_cleanup'] = True
        self.config['do_rebuild'] = True
        self.config['do_simplify'] = True
        self.config['round_robin_limit'] = -1

    def explore(self, current_patch, current_fitness):
        # cleanup
        if self.config['do_cleanup']:
            self.software.logger.info('-- cleanup --')
            cleaned_patch = copy.deepcopy(self.debug_patch)
            cleaned_diff = self.software.diff_patch(cleaned_patch)
            for (k,edit) in reversed(list(enumerate(cleaned_patch.edits))):
                tmp = copy.deepcopy(cleaned_patch)
                del tmp.edits[k]
                if self.software.diff_patch(tmp) == cleaned_diff:
                    self.software.logger.info('removed {}'.format(str(cleaned_patch.edits[k])))
                    del cleaned_patch.edits[k]
            s1, s2 = len(cleaned_patch.edits), len(self.debug_patch.edits)
            if s1 < s2:
                self.software.logger.info('cleaned size is %d (was %d)', s1, s2)
                self.software.logger.info('clean patch: {}'.format(str(cleaned_patch)))
            self.debug_patch = cleaned_patch

        # full patch first
        self.software.logger.info('-- initial patch --')
        if self.debug_patch.edits:
            run = self.do_eval_patch(self.debug_patch)
        else:
            self.report['stop'] = 'validation end (empty patch)'
            return current_patch, current_fitness

        if self.config['do_rebuild']:
            # ranking
            self.software.logger.info('-- ranking --')
            ranking = list()
            for edit in self.debug_patch.edits:
                patch = Patch([edit])
                run = self.do_eval_patch(patch)
                ranking.append((edit, run.fitness))
            ranking.sort(key=lambda c: c[1] or float('inf'))

            # rebuild
            if ranking[0][1] < self.report['initial_fitness']:
                self.software.logger.info('-- rebuild --')
                rebuild = Patch([ranking[0][0]])
                rebuild_fitness = ranking[0][1]
                for (edit,fit) in ranking[1:]:
                    patch = copy.deepcopy(rebuild)
                    patch.edits.append(edit)
                    run = self.do_eval_patch(patch)
                    if run.status == 'SUCCESS' and self.dominates(run.fitness, rebuild_fitness):
                        rebuild_fitness = run.fitness
                        rebuild.edits.append(edit)
            elif self.report['best_fitness'] > self.report['initial_fitness']:
                self.report['stop'] = 'validation end (all bad)'
                return current_patch, current_fitness

        # round robin simplify
        if self.config['do_simplify']:
            self.software.logger.info('-- simplify --')
            n = len(self.report['best_patch'].edits)+1
            rr_limit = self.config['round_robin_limit']
            last_i = 0
            while n > len(self.report['best_patch'].edits) and rr_limit != 0:
                n = len(self.report['best_patch'].edits)
                for i in range(n):
                    if i == n-1:
                        rr_limit -= 1
                    patch = Patch([e for (j, e) in enumerate(self.report['best_patch'].edits) if (j+last_i)%n != i])
                    run = self.do_eval_patch(patch)
                    if run.status == 'SUCCESS' and run.fitness == self.report['best_fitness']:
                        self.report['best_patch'] = patch # accept because smaller
                        last_i = i # round robin
                        break

        self.report['stop'] = 'validation end'
        return current_patch, current_fitness
