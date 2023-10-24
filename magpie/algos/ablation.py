import copy
import random
import time

from magpie.core import Patch
from .validation import ValidSearch


class AblationAnalysis(ValidSearch):
    def setup(self):
        super().setup()
        self.name = 'Ablation Analysis'
        self.debug_patch = None

    def hook_analysis(self, patch, edit, run):
        self.aux_log_eval('~', run.status, '', run.fitness, self.report['initial_fitness'], len(patch.edits), edit)
        self.software.logger.debug('+++ edit +++')
        self.software.logger.debug(self.software.diff_patch(patch))
        self.software.logger.debug('+++ partial patch +++')
        self.software.logger.debug(self.software.diff_patch(patch))

    def explore(self, current_patch, current_fitness):
        if self.debug_patch is None:
            raise ValueError()
        self.cleaned_patch = self.do_clean_patch(self.debug_patch)
        self.software.logger.debug('CLEAN_PATCH: {}'.format(str(self.cleaned_patch)))
        self.software.logger.debug('CLEAN_SIZE: %d (was %d)', len(self.cleaned_patch.edits), len(self.debug_patch.edits))
        self.report['best_fitness'] = None
        self.report['best_patch'] = None
        self.report['cleaned_patch'] = self.cleaned_patch

        # full patch first
        if self.debug_patch.edits:
            self.do_eval_patch(self.cleaned_patch)
        else:
            self.report['stop'] = 'ablation end (empty patch)'
            return current_patch, current_fitness

        # ranking
        rebuild = copy.deepcopy(self.cleaned_patch)
        removed_edits_ids = list()
        while rebuild.edits:
            ranking = list()
            for i, edit in enumerate(rebuild.edits):
                patch = Patch(rebuild.edits[:i] + rebuild.edits[i+1:])
                run = self.do_eval_patch(patch)
                ranking.append((i, run.fitness))
            ranking.sort(key=lambda c: c[1] or float('inf'))
            best_edit_id = ranking[0][0]
            removed_edits_ids.append(best_edit_id)
            rebuild.edits.pop(best_edit_id)

        # analysis
        self.software.logger.info('==== ANALYSIS ====')
        patch = copy.deepcopy(self.cleaned_patch)
        run = self.evaluate_patch(patch) # should be already cached (initial)
        self.hook_analysis(patch, '', run)
        for i in removed_edits_ids:
            edit = patch.edits.pop(i)
            run = self.evaluate_patch(patch) # should be already cached
            self.hook_analysis(patch, 'removing {}'.format(edit), run)

        self.report['stop'] = 'ablation end'
        return current_patch, current_fitness
