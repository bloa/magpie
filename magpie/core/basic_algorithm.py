import itertools
import random
import os
import time

from magpie.core import AbstractAlgorithm, Patch, Variant


class BasicAlgorithm(AbstractAlgorithm):
    def setup(self):
        super().setup()
        self.config['warmup'] = 3
        self.config['warmup_strategy'] = 'last'
        self.config['cache_maxsize'] = 40
        self.config['cache_keep'] = 0.2

    def reset(self):
        super().reset()
        self.stats['cache_hits'] = 0
        self.stats['cache_misses'] = 0

    def hook_reset_batch(self):
        # resample instances
        s = self.config['batch_sample_size']
        # TODO: sample with replacement, with refill
        if sum(len(b) for b in self.config['batch_bins']) <= s:
            batch = [[inst for inst in b] for b in self.config['batch_bins']]
        else:
            batch = [[] for b in self.config['batch_bins']]
            while s > 0:
                for i in range(len(batch)):
                    if len(batch[i]) < len(self.config['batch_bins'][i]):
                        batch[i].append(self.config['batch_bins'][i][len(batch[i])])
                        s -= 1
                    if s == 0:
                        break
        batch = [b for b in batch if b] # discards empty bins
        self.software.batch = batch if any(batch) else [['']] # single empty instance when no batch
        # early exit before warmup
        if self.report['initial_fitness'] is None:
            return
        # reset initial fitness
        patch = Patch([])
        variant = Variant(self.software, patch)
        run = self.evaluate_variant(variant)
        self.report['initial_fitness'] = run.fitness
        self.report['best_fitness'] = run.fitness
        self.hook_warmup_evaluation('INITIAL', patch, run)
        if run.status != 'SUCCESS':
            raise RuntimeError('initial solution has failed')
        # update best patch
        if self.report['best_patch'] and self.report['best_patch'].edits:
            variant = Variant(self.software, self.report['best_patch'])
            run = self.evaluate_variant(variant)
            best = self.dominates(run.fitness, self.report['best_fitness'])
            self.hook_batch_evaluation('BEST', self.report['best_patch'], run, best)
            if run.status == 'SUCCESS' and best:
                self.report['best_fitness'] = run.fitness
            else:
                self.report['best_patch'] = patch

    def hook_warmup(self):
        self.hook_reset_batch()
        self.stats['wallclock_start'] = self.stats['wallclock_warmup'] = time.time()
        self.software.logger.info('==== WARMUP ====')

    def hook_warmup_evaluation(self, count, patch, run):
        self.aux_log_eval(count, run.status, ' ', run.fitness, None, None, run.log)
        if run.status != 'SUCCESS':
            self.software.diagnose_error(run)

    def hook_batch_evaluation(self, count, patch, run, best=False):
        c = '*' if best else ' '
        self.aux_log_eval(count, run.status, c, run.fitness, self.report['initial_fitness'], len(patch.edits), run.log)

    def hook_start(self):
        if not self.config['possible_edits']:
            raise RuntimeError('possible_edits list is empty')
        # TODO: check that every possible edit can be created and simplify create_edit
        self.stats['wallclock_start'] = time.time() # discards warmup time
        self.software.logger.info('==== START: {} ===='.format(self.__class__.__name__))

    def hook_main_loop(self):
        pass

    def hook_evaluation(self, variant, run, accept=False, best=False):
        if best:
            c = '*'
        elif accept:
            c = '+'
        else:
            c = ' '
        self.software.logger.debug(variant.patch)
        # self.software.logger.debug(run) # uncomment for detail on last cmd
        counter = self.aux_log_counter()
        self.aux_log_eval(counter, run.status, c, run.fitness, self.report['initial_fitness'], len(variant.patch.edits), run.log)
        if accept or best:
            self.software.logger.debug(variant.diff)

    def aux_log_eval(self, counter, status, c, fitness, baseline, patch_size, data):
        if fitness is not None and baseline is not None:
            if isinstance(fitness, list):
                s = '({}%)'.format('% '.join([str(round(100*fitness[k]/baseline[k], 2)) for k in range(len(fitness))]))
            else:
                s = '({}%)'.format(round(100*fitness/baseline, 2))
        else:
            s = ''
        if patch_size is not None:
            s2 = '[{} edit(s)] '.format(patch_size)
        else:
            s2 = ''
        self.software.logger.info('{:<7} {:<20} {:>1}{:<24}{}'.format(counter, status, c, str(fitness) + ' ' + s + ' ' + s2, data))

    def aux_log_counter(self):
        return str(self.stats['steps']+1)

    def hook_end(self):
        self.stats['wallclock_end'] = time.time()
        self.stats['wallclock_total'] = self.stats['wallclock_end'] - self.stats['wallclock_start']
        if self.report['best_patch']:
            variant = Variant(self.software, self.report['best_patch'])
            self.report['diff'] = variant.diff
        self.software.logger.info('==== END ====')

    def warmup(self):
        patch = Patch([])
        variant = Variant(self.software, patch)
        if self.report['initial_patch'] is None:
            self.report['initial_patch'] = patch
        warmup_values = []
        for i in range(max(self.config['warmup'] or 1, 1), 0, -1):
            run = self.evaluate_variant(variant, force=True)
            self.hook_warmup_evaluation('WARM', patch, run)
            if run.status != 'SUCCESS':
                step = run.status.split('_')[0].lower()
                self.report['stop'] = f'failed to {step} target software'
                return
            warmup_values.append(run.fitness)
        if self.config['warmup_strategy'] == 'last':
            current_fitness = warmup_values[-1]
        elif self.config['warmup_strategy'] == 'min':
            current_fitness = min(warmup_values)
        elif self.config['warmup_strategy'] == 'max':
            current_fitness = max(warmup_values)
        elif self.config['warmup_strategy'] == 'mean':
            current_fitness = sum(warmup_values)/len(warmup_values)
        elif self.config['warmup_strategy'] == 'median':
            current_fitness = sorted(warmup_values)[len(warmup_values)//2]
        else:
            raise ValueError('unknown warmup strategy')
        run.fitness = current_fitness
        self.cache_set(variant.diff, run)
        self.hook_warmup_evaluation('INITIAL', patch, run)
        self.report['initial_fitness'] = current_fitness
        if self.report['best_patch'] is None:
            self.report['best_fitness'] = current_fitness
            self.report['best_patch'] = patch
        else:
            run = self.evaluate_patch(self.report['best_patch'], force=True)
            self.hook_warmup_evaluation('BEST', patch, run)
            if self.dominates(run.fitness, current_fitness):
                self.report['best_fitness'] = run.fitness
            else:
                self.report['best_patch'] = patch
                self.report['best_fitness'] = current_fitness

    def evaluate_variant(self, variant, force=False):
        cached_run = None
        if self.config['cache_maxsize'] > 0 and not force:
            cached_run = self.cache_get(variant.diff) # potentially partial
        run = self.software.evaluate_variant(variant, cached_run)
        if self.config['cache_maxsize'] > 0:
            self.cache_set(variant.diff, run)
        self.stats['budget'] += getattr(run, 'budget', 0) or 0
        return run

    def cache_get(self, diff):
        try:
            run = self.cache[diff]
            self.stats['cache_hits'] += 1
            if self.config['cache_maxsize'] > 0:
                self.cache_hits[diff] += 1
            return run
        except KeyError:
            self.stats['cache_misses'] += 1
            return None

    def cache_set(self, diff, run):
        msize = self.config['cache_maxsize']
        if msize > 0 and len(self.cache_hits) > msize:
            keep = self.config['cache_keep']
            hits = sorted(self.cache.keys(), key=lambda k: 999 if len(k) == 0 else self.cache_hits[k])
            for k in hits[:int(msize*(1-keep))]:
                del self.cache[k]
            self.cache_hits = { p: 0 for p in self.cache.keys()}
        if not diff in self.cache:
            self.cache_hits[diff] = 0
        self.cache[diff] = run

    def cache_copy(self, algo):
        self.cache = algo.cache
        self.cache_hits = algo.cache_hits

    def cache_reset(self):
        self.cache = {}
        self.cache_hits = {}
