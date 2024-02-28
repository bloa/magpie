import copy

from magpie.core import Variant
from .validation import ValidSearch


class AblationAnalysis(ValidSearch):
    def setup(self):
        super().setup()
        self.name = 'Ablation Analysis'

    def explore(self, current_patch, current_fitness):
        variant = Variant(self.software, current_patch)

        # cleanup
        self.software.logger.info('-- cleanup --')
        variant = self.do_cleanup(variant)
        self.report['best_patch'] = variant.patch

        # full patch first
        self.software.logger.info('-- exploration --')
        if variant.patch.edits:
            run = self.evaluate_variant(variant)
            self.hook_evaluation(variant, run)
        else:
            self.report['stop'] = 'ablation end (empty patch)'
            return variant.patch, current_fitness

        # ranking
        rebuild = copy.deepcopy(variant.patch)
        removed = []
        while rebuild.edits:
            ranking = []
            for k, _ in enumerate(rebuild.edits):
                patch = copy.deepcopy(rebuild)
                del patch.edits[k]
                tmp = Variant(self.software, patch)
                run = self.evaluate_variant(tmp)
                self.hook_evaluation(tmp, run)
                ranking.append((k, run.fitness))
            ranking.sort(key=lambda c: c[1] or float('inf'))
            best_edit_id = ranking[0][0]
            removed.append(best_edit_id)
            rebuild.edits.pop(best_edit_id)

        # analysis
        self.software.logger.info('-- backtrack --')
        run = self.evaluate_variant(variant) # should be already cached (initial)
        self.hook_evaluation(variant, run)
        patch = copy.deepcopy(variant.patch)
        for i in removed:
            edit = patch.edits.pop(i) # modify in-place
            tmp = Variant(self.software, patch)
            run = self.evaluate_variant(tmp) # should be already cached
            run.log = f'removing {edit}'
            self.hook_evaluation(tmp, run)

        self.report['stop'] = 'ablation end'
        return self.report['best_patch'], self.report['best_fitness']
