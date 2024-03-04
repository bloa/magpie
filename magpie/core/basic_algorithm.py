import os
import random
import time

import magpie.utils

from .abstract_algorithm import AbstractAlgorithm
from .patch import Patch
from .variant import Variant


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
        self.cache_reset()

    def setup_scenario(self, config):
        sec = config['search']
        self.config['warmup'] = int(sec['warmup'])
        self.config['warmup_strategy'] = sec['warmup_strategy']
        self.stop['steps'] = int(val) if (val := sec['max_steps']) else None
        self.stop['wall'] = int(val) if (val := sec['max_time']) else None
        self.stop['fitness'] = int(val) if (val := sec['target_fitness']) else None
        self.config['cache_maxsize'] = int(val) if (val := sec['cache_maxsize']) else 0
        self.config['cache_keep'] = float(sec['cache_keep'])

        self.config['possible_edits'] = []
        for edit in sec['possible_edits'].split():
            try:
                klass = magpie.utils.edit_from_string(edit)
                self.config['possible_edits'].append(klass)
            except RuntimeError as exc:
                raise ValueError(f'Invalid config file: unknown edit type "{edit}" in "[software] possible_edits"') from exc
        if self.config['possible_edits'] == []:
            raise ValueError('Invalid config file: "[search] possible_edits" must be non-empty!')

        bins = [[]]
        for s in sec['batch_instances'].splitlines():
            if s == '___':
                if bins[-1]:
                    bins.append([])
            elif s[:5] == 'file:':
                try:
                    with open(os.path.join(config['software']['path'], s[5:])) as bin_file:
                        bins[-1].extend([line for line in [line.strip() for line in bin_file] if line and line[0] != '#'])
                except FileNotFoundError:
                    with open(s[5:]) as bin_file:
                        bins[-1].extend([line for line in [line.strip() for line in bin_file] if line and line[0] != '#'])
            else:
                s.strip()
                if s and s[0] != '#':
                    bins[-1].append(s)
        if len(bins) > 1 and not bins[-1]:
            bins.pop()
        tmp = sec['batch_shuffle'].lower()
        if tmp in ['true', 't', '1']:
            for a in bins:
                random.shuffle(a)
        elif tmp in ['false', 'f', '0']:
            pass
        else:
            raise ValueError('[search] batch_shuffle should be Boolean')
        tmp = sec['batch_bin_shuffle'].lower()
        if tmp in ['true', 't', '1']:
            random.shuffle(bins)
        elif tmp in ['false', 'f', '0']:
            pass
        else:
            raise ValueError('[search] batch_bin_shuffle should be Boolean')
        self.config['batch_bins'] = bins
        self.config['batch_sample_size'] = int(sec['batch_sample_size'])

    def hook_reset_batch(self):
        # resample instances
        s = self.config['batch_sample_size']
        # TODO: sample with replacement, with refill
        if sum(len(b) for b in self.config['batch_bins']) <= s:
            batch = list(self.config['batch_bins'])
        else:
            batch = [[] for b in self.config['batch_bins']]
            while s > 0:
                for i, b in enumerate(batch):
                    if len(b) < len(self.config['batch_bins'][i]):
                        b.append(self.config['batch_bins'][i][len(b)])
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
            raise RuntimeError('Initial solution has failed')
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
            raise RuntimeError('Possible_edits list is empty')
        # TODO: check that every possible edit can be created and simplify create_edit
        self.stats['wallclock_start'] = time.time() # discards warmup time
        self.software.logger.info(f'==== START: {self.__class__.__name__} ====')

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
                tmp = '% '.join([str(round(100*fitness[k]/baseline[k], 2)) for k in range(len(fitness))])
            else:
                tmp = round(100*fitness/baseline, 2)
            s = f'({tmp}%)'
        else:
            s = ''
        if patch_size is not None:
            s2 = f'[{patch_size} edit(s)] '
        else:
            s2 = ''
        tmp = f'{str(fitness)} {s} {s2}'
        self.software.logger.info(f'{counter:<7} {status:<20} {c:>1}{tmp:<24}{data}')

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
        for _ in range(max(self.config['warmup'] or 1, 1), 0, -1):
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
            raise ValueError('Unknown warmup strategy')
        run.fitness = current_fitness
        self.cache_set(variant.diff, run)
        self.hook_warmup_evaluation('INITIAL', patch, run)
        self.report['initial_fitness'] = current_fitness
        if self.report['best_patch'] is None:
            self.report['best_fitness'] = current_fitness
            self.report['best_patch'] = patch
        else:
            variant = Variant(self.software, self.report['best_patch'])
            run = self.evaluate_variant(variant, force=True)
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
        if 0 < msize < len(self.cache_hits):
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
