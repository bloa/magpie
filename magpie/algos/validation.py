import copy

import magpie.core
import magpie.utils

from .local_search import LocalSearch


class ValidSearch(LocalSearch):
    def __init__(self):
        super().__init__()
        self.debug_patch = None

    def hook_warmup(self):
        super().hook_warmup()
        if self.debug_patch is None:
            raise RuntimeError

    def hook_start(self):
        super().hook_start()
        self.report['best_fitness'] = None
        self.report['best_patch'] = self.debug_patch

    def hook_evaluation(self, variant, run, accept=False, best=False):
        # accept
        accept = best = False
        if run.status == 'SUCCESS':
            best = self.dominates(run.fitness, self.report['best_fitness']) or (run.fitness == self.report['best_fitness'] and len(variant.patch.edits) < len(self.report['best_patch'].edits))
            accept = best or run.fitness == self.report['best_fitness']
            if best:
                self.report['best_fitness'] = run.fitness
                self.report['best_patch'] = variant.patch

        super().hook_evaluation(variant, run, accept, best)

        # next
        self.stats['steps'] += 1

    def do_cleanup(self, variant):
        cleaned = copy.deepcopy(variant)
        for k in reversed(range(len(variant.patch.edits))):
            patch = copy.deepcopy(cleaned.patch)
            del patch.edits[k]
            tmp = magpie.core.Variant(self.software, patch)
            if tmp.diff == variant.diff:
                self.software.logger.info('removed %s', cleaned.patch.edits[k])
                cleaned = tmp
        s1, s2 = len(cleaned.patch.edits), len(variant.patch.edits)
        if s1 < s2:
            self.software.logger.info('cleaned size is %d (was %d)', s1, s2)
            self.software.logger.info('clean patch: %s', cleaned.patch)
        return cleaned


class ValidSingle(ValidSearch):
    def __init__(self):
        super().__init__()
        self.name = 'Validation Single'

    def explore(self, current_patch, current_fitness):
        # eval every single patch
        for edit in current_patch.edits:
            patch = magpie.core.Patch([edit])
            variant = magpie.core.Variant(self.software, patch)
            run = self.evaluate_variant(variant)
            self.hook_evaluation(variant, run)

        self.report['stop'] = 'validation end'
        return self.report['best_patch'], self.report['best_fitness']

magpie.utils.known_algos.append(ValidSingle)


class ValidTest(ValidSearch):
    def __init__(self):
        super().__init__()
        self.name = 'Validation Full'

    def explore(self, current_patch, current_fitness):
        # full patch only
        variant = magpie.core.Variant(self.software, current_patch)
        run = self.evaluate_variant(variant)
        self.hook_evaluation(variant, run)

        self.report['stop'] = 'validation end'
        return self.report['best_patch'], self.report['best_fitness']

magpie.utils.known_algos.append(ValidTest)


class ValidMinify(ValidSearch):
    def __init__(self):
        super().__init__()
        self.name = 'Minify Patch'
        self.config['do_cleanup'] = True
        self.config['do_rebuild'] = True
        self.config['do_simplify'] = True
        self.config['round_robin_limit'] = -1

    def setup(self, config):
        super().setup(config)
        sec = config['search.minify']
        for key in [
                'do_cleanup',
                'do_rebuild',
                'do_simplify',
        ]:
            tmp = sec[key].lower()
            if tmp in ['true', 't', '1']:
                self.config[key] = True
            elif tmp in ['false', 'f', '0']:
                self.config[key] = False
            else:
                msg = f'[search.minify] {key} should be Boolean'
                raise magpie.core.ScenarioError(msg)
        self.config['round_robin_limit'] = int(sec['round_robin_limit'])

    def explore(self, current_patch, current_fitness):
        variant = magpie.core.Variant(self.software, current_patch)

        # cleanup
        if self.config['do_cleanup']:
            self.software.logger.info('-- cleanup --')
            variant = self.do_cleanup(variant)
            self.report['best_patch'] = variant.patch

        # full patch first
        self.software.logger.info('-- initial patch --')
        if variant.patch.edits:
            run = self.evaluate_variant(variant)
            self.hook_evaluation(variant, run)
        else:
            self.report['stop'] = 'validation end (empty patch)'
            return self.report['best_patch'], self.report['best_fitness']

        if self.config['do_rebuild']:
            # ranking
            self.software.logger.info('-- ranking --')
            ranking = []
            for edit in variant.patch.edits:
                patch = magpie.core.Patch([edit])
                tmp = magpie.core.Variant(self.software, patch)
                run = self.evaluate_variant(tmp)
                self.hook_evaluation(tmp, run)
                ranking.append((edit, run.fitness))
            ranking.sort(key=lambda c: c[1] or float('inf'))

            # rebuild
            if ranking[0][1] < self.report['initial_fitness']:
                self.software.logger.info('-- rebuild --')
                rebuild = magpie.core.Patch([ranking[0][0]])
                rebuild_fitness = ranking[0][1]
                for (edit, _) in ranking[1:]:
                    patch = copy.deepcopy(rebuild)
                    patch.edits.append(edit)
                    tmp = magpie.core.Variant(self.software, patch)
                    run = self.evaluate_variant(tmp)
                    self.hook_evaluation(tmp, run)
                    if run.status == 'SUCCESS' and self.dominates(run.fitness, rebuild_fitness):
                        rebuild_fitness = run.fitness
                        rebuild.edits.append(edit)
            elif self.report['best_fitness'] > self.report['initial_fitness']:
                self.report['stop'] = 'validation end (all bad)'
                return self.report['best_patch'], self.report['best_fitness']

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
                    patch = magpie.core.Patch([e for (j, e) in enumerate(self.report['best_patch'].edits) if (j+last_i)%n != i])
                    tmp = magpie.core.Variant(self.software, patch)
                    run = self.evaluate_variant(tmp)
                    self.hook_evaluation(tmp, run)
                    if run.status == 'SUCCESS' and run.fitness == self.report['best_fitness']:
                        self.report['best_patch'] = patch # accept because smaller
                        last_i = i # round robin
                        break

        self.report['stop'] = 'validation end'
        return self.report['best_patch'], self.report['best_fitness']

magpie.utils.known_algos.append(ValidMinify)
