import math
import pathlib
import random
import time

import magpie.settings
import magpie.utils

from .abstract_algorithm import AbstractAlgorithm
from .errors import ScenarioError
from .patch import Patch
from .variant import Variant


class BasicAlgorithm(AbstractAlgorithm):
    def __init__(self):
        super().__init__()
        self.config['warmup'] = 3
        self.config['warmup_strategy'] = 'last'
        self.config['cache_maxsize'] = 40
        self.config['cache_keep'] = 0.2

    def reset(self):
        super().reset()
        self.stats['cache_hits'] = 0
        self.stats['cache_misses'] = 0
        self.cache_reset()

    def setup(self, config):
        sec = config['search']
        self.config['warmup'] = int(sec['warmup'])
        self.config['warmup_strategy'] = sec['warmup_strategy']
        self.stop['steps'] = int(val) if (val := sec['max_steps']) else None
        self.stop['wall'] = int(val) if (val := sec['max_time']) else None
        self.stop['fitness'] = [float(s) for s in val.split('s')] if (val := sec['target_fitness']) else None
        self.config['cache_maxsize'] = int(val) if (val := sec['cache_maxsize']) else 0
        self.config['cache_keep'] = float(sec['cache_keep'])

        self.config['possible_edits'] = []
        try:
            for edit in sec['possible_edits'].split():
                self.config['possible_edits'].append(magpie.utils.edit_from_string(edit))
        except RuntimeError:
            msg = f'Invalid config file: unknown edit type "{edit}" in "[software] possible_edits"'
            raise ScenarioError(msg)
        if self.config['possible_edits'] == []:
            msg = 'Invalid config file: "[search] possible_edits" must be non-empty!'
            raise ScenarioError(msg)

        bins = [[]]
        for s in sec['batch_instances'].splitlines():
            if s == '___':
                if bins[-1]:
                    bins.append([])
            elif s[:5] == 'file:':
                try:
                    with (pathlib.Path(config['software']['path']) / s[5:]).open('r') as bin_file:
                        bins[-1].extend([line for line in [line.strip() for line in bin_file] if line and line[0] != '#'])
                except FileNotFoundError:
                    with pathlib.Path(s[5:]).open('r') as bin_file:
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
            msg = '[search] batch_shuffle should be Boolean'
            raise ScenarioError(msg)
        tmp = sec['batch_bin_shuffle'].lower()
        if tmp in ['true', 't', '1']:
            random.shuffle(bins)
        elif tmp in ['false', 'f', '0']:
            pass
        else:
            msg = '[search] batch_bin_shuffle should be Boolean'
            raise ScenarioError(msg)
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
        if self.report['reference_fitness'] is None:
            return
        # reset reference fitness
        patch = Patch([])
        variant = Variant(self.software, patch)
        run = self.evaluate_variant(variant)
        self.report['reference_fitness'] = run.fitness
        self.report['best_fitness'] = run.fitness
        self.hook_warmup_evaluation('REF', patch, run)
        if run.status != 'SUCCESS':
            msg = 'Reference software evaluation failed'
            raise RuntimeError(msg)
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
        msg = '~~~~ WARMUP ~~~~'
        if magpie.settings.color_output:
            msg = f'\033[1m{msg}\033[0m'
        self.software.logger.info(msg)

    def hook_warmup_evaluation(self, counter, patch, run):
        data = self.aux_log_data(None, run, counter, None, False, False)
        if magpie.settings.log_format_info:
            msg = magpie.settings.log_format_info.format(**data)
            if magpie.settings.color_output:
                msg = self.aux_log_color(msg, run)
            self.software.logger.info(msg)
        if run.status != 'SUCCESS':
            self.software.diagnose_error(run)

    def hook_batch_evaluation(self, counter, patch, run, best=False):
        data = self.aux_log_data(None, run, counter, self.report['reference_fitness'], False, best)
        if magpie.settings.log_format_info:
            msg = magpie.settings.log_format_info.format(**data)
            if magpie.settings.color_output:
                msg = self.aux_log_color(msg, run, best=best)
            self.software.logger.info(msg)

    def hook_start(self):
        if not self.config['possible_edits']:
            msg = 'Possible_edits list is empty'
            raise RuntimeError(msg)
        # TODO: check that every possible edit can be created and simplify create_edit
        self.stats['wallclock_start'] = time.time() # discards warmup time
        self.software.logger.info('')
        msg = '~~~~ START ~~~~'
        if magpie.settings.color_output:
            msg = f'\033[1m{msg}\033[0m'
        self.software.logger.info(msg)

    def hook_main_loop(self):
        pass

    def hook_evaluation(self, variant, run, accept=False, best=False):
        data = self.aux_log_data(variant.patch, run, self.aux_log_counter(), self.report['reference_fitness'], accept, best)
        if magpie.settings.log_format_info:
            msg = magpie.settings.log_format_info.format(**data)
            if magpie.settings.color_output:
                msg = self.aux_log_color(msg, run, accept=accept, best=best)
            self.software.logger.info(msg)
        if magpie.settings.log_format_debug:
            msg = magpie.settings.log_format_debug.format(**data)
            self.software.logger.debug(msg)

    def aux_log_counter(self):
        return str(self.stats['steps']+1)

    def aux_log_data(self, patch, run, counter, baseline, accept, best):
        data = {}
        data['counter'] = counter or self.aux_log_counter()
        data['status'] = run.status
        data['best'] = '*' if best else '+' if accept else ' '
        data['fitness'] = 'None'
        if run.fitness is not None:
            tmp = run.fitness
            if not isinstance(run.fitness, list):
                tmp = [tmp]
            data['fitness'] = ' '.join([magpie.settings.log_format_fitness.format(x) for x in tmp])
        data['ratio'] = '--'
        if run.fitness is not None and baseline is not None:
            if isinstance(run.fitness, list):
                tmp = [fit/base if base != 0 else math.inf for fit, base in zip(run.fitness, baseline)]
            else:
                tmp = [run.fitness/baseline]
            data['ratio'] = ' '.join([magpie.settings.log_format_ratio.format(x) for x in tmp])
        data['extra'] = 'extra'
        data['log'] = run.log or ''
        data['patch'] = str(patch)
        data['patchifaccept'] = magpie.settings.log_format_patchif.format(patch=data['patch']) if accept else ''
        data['patchifbest'] = magpie.settings.log_format_patchif.format(patch=data['patch']) if best else ''
        data['diff'] = run.variant.diff
        data['diffifaccept'] = magpie.settings.log_format_diffif.format(diff=data['diff']) if accept else ''
        data['diffifbest'] = magpie.settings.log_format_diffif.format(diff=data['diff']) if best else ''
        data['size'] = f'{len(patch.edits) if patch else 0} edit(s)'
        data['cached'] = ''
        if run.cached:
            if run.updated:
                data['cached'] = '[part.cached]'
            else:
                data['cached'] = '[cached]'
        return data

    def aux_log_color(self, msg, run, accept=False, best=False):
        if magpie.settings.color_output is False:
            return msg
        if run.cached and not run.updated:
            return f'\033[30m{msg}\033[0m'
        if best:
            return f'\033[32m{msg}\033[0m'
        if accept:
            return f'\033[33m{msg}\033[0m'
        if run.status != 'SUCCESS':
            return f'\033[31m{msg}\033[0m'
        return msg

    def hook_end(self):
        self.stats['wallclock_end'] = time.time()
        self.stats['wallclock_total'] = self.stats['wallclock_end'] - self.stats['wallclock_start']
        if self.report['best_patch']:
            variant = Variant(self.software, self.report['best_patch'])
            self.report['diff'] = variant.diff
        msg = '~~~~ END ~~~~'
        if magpie.settings.color_output:
            msg = f'\033[1m{msg}\033[0m'
        self.software.logger.info(msg)

    def warmup(self):
        patch = Patch([])
        variant = Variant(self.software, patch)
        if self.report['initial_patch'] is None:
            self.report['initial_patch'] = patch
        if self.report['reference_patch'] is None:
            self.report['reference_patch'] = patch
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
            msg = 'Unknown warmup strategy'
            raise ValueError(msg)
        run.fitness = current_fitness
        self.cache_set(variant.diff, run)
        self.hook_warmup_evaluation('REF', patch, run)
        self.report['reference_fitness'] = current_fitness
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
        except KeyError:
            self.stats['cache_misses'] += 1
            return None
        else:
            self.stats['cache_hits'] += 1
            if self.config['cache_maxsize'] > 0:
                self.cache_hits[diff] += 1
            run.cached = True
            run.updated = False
            return run

    def cache_set(self, diff, run):
        msize = self.config['cache_maxsize']
        if 0 < msize < len(self.cache_hits):
            keep = self.config['cache_keep']
            hits = sorted(self.cache.keys(), key=lambda k: 999 if len(k) == 0 else self.cache_hits[k])
            for k in hits[:int(msize*(1-keep))]:
                del self.cache[k]
            self.cache_hits = dict.fromkeys(self.cache, 0)
        if diff not in self.cache:
            self.cache_hits[diff] = 0
        self.cache[diff] = run

    def cache_copy(self, algo):
        self.cache = algo.cache
        self.cache_hits = algo.cache_hits

    def cache_reset(self):
        self.cache = {}
        self.cache_hits = {}
