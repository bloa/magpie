import math
import pathlib
import random
import time

import magpie.settings
import magpie.utils

from .abstract_algorithm import AbstractAlgorithm
from .basic_evalcache import BasicEvalCache
from .errors import ScenarioError
from .patch import Patch
from .variant import Variant


class BasicAlgorithm(AbstractAlgorithm):
    def __init__(self, config):
        self.eval_cache = BasicEvalCache()
        super().__init__()
        sec = config['search']
        self.config['warmup'] = magpie.utils.str_to_int_or_none(sec['warmup'])
        self.config['warmup_strategy'] = sec['warmup_strategy']
        self.stop['steps'] = int(val) if (val := sec['max_steps']) else None
        self.stop['wall'] = int(val) if (val := sec['max_time']) else None
        self.stop['fitness'] = [float(s) for s in val.split('s')] if (val := sec['target_fitness']) else None

        self.config['possible_edits'] = []
        try:
            for edit in sec['possible_edits'].split():
                self.config['possible_edits'].append(magpie.utils.edit_from_string(edit))
        except RuntimeError:
            msg = f'Invalid config file: unknown edit type "{edit}" in "[software] possible_edits"'
            raise ScenarioError(msg) from None
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
        try:
            if magpie.utils.str_to_bool(sec['batch_shuffle']):
                for a in bins:
                    random.shuffle(a)
        except ValueError as e:
            msg = '[search] batch_shuffle should be Boolean'
            raise ScenarioError(msg) from e
        try:
            if magpie.utils.str_to_bool(sec['batch_bin_shuffle']):
                random.shuffle(bins)
        except ValueError as e:
            msg = '[search] batch_bin_shuffle should be Boolean'
            raise ScenarioError(msg) from e
        self.config['batch_bins'] = bins
        self.config['batch_sample_size'] = int(sec['batch_sample_size'])

    def reset(self):
        super().reset()
        self.stats['cache_hits'] = 0
        self.stats['cache_misses'] = 0
        self.eval_cache.reset()

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
        with self.software.add_to_env(counter='REF'):
            run = self.evaluate_variant(variant)
            self.hook_warmup_evaluation('REF', patch, run)
        self.report['reference_fitness'] = run.fitness
        self.report['best_fitness'] = run.fitness
        if run.status != 'SUCCESS':
            msg = 'Reference software evaluation failed'
            raise RuntimeError(msg)
        # update best patch
        if self.report['best_patch'] and self.report['best_patch'].edits:
            variant = Variant(self.software, self.report['best_patch'])
            with self.software.add_to_env(counter='BEST', patch=self.report['best_patch']):
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
        header = magpie.utils.format_subheader('WARMUP', magpie.settings.color_output)
        self.software.logger.info(header)

    def hook_warmup_evaluation(self, counter, patch, run):
        data = self.aux_log_data(patch, run, counter, None, False, False)
        self.aux_log_print(data, run, False, False)
        if run.status != 'SUCCESS':
            self.software.diagnose_error(run)

    def hook_batch_evaluation(self, counter, patch, run, best=False):
        data = self.aux_log_data(patch, run, counter, self.report['reference_fitness'], False, best)
        self.aux_log_print(data, run, False, best)

    def hook_start(self):
        if not self.config['possible_edits']:
            msg = 'Possible_edits list is empty'
            raise RuntimeError(msg)
        # TODO: check that every possible edit can be created and simplify create_edit
        self.stats['wallclock_start'] = time.time() # discards warmup time
        self.software.logger.info('')
        header = magpie.utils.format_subheader('START', magpie.settings.color_output)
        self.software.logger.info(header)

    def hook_main_loop(self):
        pass

    def hook_evaluation(self, variant, run, accept=False, best=False):
        data = self.aux_log_data(variant.patch, run, self.aux_log_counter(), self.report['reference_fitness'], accept, best)
        self.aux_log_print(data, run, accept, best)

    def aux_log_counter(self):
        return str(self.stats['steps']+1)

    def aux_log_data(self, patch, run, counter, baseline, accept, best):
        data = {}
        data['counter'] = counter or self.aux_log_counter()
        data['status'] = run.status
        data['best'] = '*' if best else '+' if accept else ' '
        data['rawfitness'] = data['fitness'] = 'None'
        if run.fitness is not None:
            tmp = run.fitness
            assert isinstance(run.fitness, list)
            data['rawfitness'] = ' '.join([str(x) for x in tmp])
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
        data['diff'] = run.variant.diff
        data['size'] = f'{len(patch.edits) if patch else 0} edit(s)'
        data['cached'] = ''
        if run.cached:
            if run.updated:
                data['cached'] = '[part.cached]'
            else:
                data['cached'] = '[cached]'
        encoding = magpie.settings.output_encoding
        data['lastcmd'] = run.last_exec.cmd
        try:
            data['stdout'] = run.last_exec.stdout.decode(encoding, errors='strict')
        except UnicodeDecodeError:
            data['stdout'] = run.last_exec.stdout.decode(encoding, errors='replace')
        try:
            data['stderr'] = run.last_exec.stderr.decode(encoding, errors='strict')
        except UnicodeDecodeError:
            data['stderr'] = run.last_exec.stderr.decode(encoding, errors='replace')
        for key in ['diff', 'stdout', 'stderr']:
            data[key] = f'<<{key.upper()}\n{data[key]}\n{key.upper()}' if data[key] else '""'
        return data

    def aux_log_print(self, data, run, accept, best):
        def aux(val):
            return any([
                val == 'always',
                val == 'error' and run.status != 'SUCCESS',
                val == 'accept' and accept,
                val == 'best' and best,
            ])
        msg = magpie.settings.log_format_info_summary.format(**data)
        if magpie.settings.color_output:
            msg = self.aux_log_color(msg, run, accept=accept, best=best)
        self.software.logger.info(msg)
        for key in magpie.settings.log_format_debug.keys():
            if aux(magpie.settings.log_capture[key]):
                msg = magpie.settings.log_format_debug[key].format(**data)
                self.software.logger.debug(msg)

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
        header = magpie.utils.format_subheader('END', magpie.settings.color_output)
        self.software.logger.info(header)

    def warmup(self):
        patch = Patch([])
        variant = Variant(self.software, patch)
        if self.report['initial_patch'] is None:
            self.report['initial_patch'] = patch
        if self.report['reference_patch'] is None:
            self.report['reference_patch'] = patch
        warmup_values = []
        for _ in range(max(self.config['warmup'] or 1, 1), 0, -1):
            with self.software.add_to_env(counter='WARM'):
                run = self.evaluate_variant(variant, force=True)
                self.hook_warmup_evaluation('WARM', patch, run)
            if run.status != 'SUCCESS':
                step = run.status.split('_')[0].lower()
                self.report['stop'] = f'failed to {step} target software'
                return
            warmup_values.append(run.fitness)
        current_fitness = self._aggregate_warmup(warmup_values, self.config['warmup_strategy'])
        run.fitness = current_fitness
        self.eval_cache.update(variant.diff, run)
        self.hook_warmup_evaluation('REF', patch, run)
        self.report['reference_fitness'] = current_fitness
        if self.report['best_patch'] is None:
            self.report['best_fitness'] = current_fitness
            self.report['best_patch'] = patch
        else:
            variant = Variant(self.software, self.report['best_patch'])
            with self.software.add_to_env(counter='BEST', patch=self.report['best_patch']):
                run = self.evaluate_variant(variant, force=True)
                self.hook_warmup_evaluation('BEST', patch, run)
            if self.dominates(run.fitness, current_fitness):
                self.report['best_fitness'] = run.fitness
            else:
                self.report['best_patch'] = patch
                self.report['best_fitness'] = current_fitness

    @classmethod
    def _aggregate_warmup(cls, warmup_values, strategy):
        def aux(values):
            match strategy:
                case 'last':
                    return values[-1]
                case 'min':
                    return min(values)
                case 'max':
                    return max(values)
                case 'mean':
                    return sum(values)/len(values)
                case 'median':
                    tmp = sorted(values)
                    k = len(values)//2
                    return tmp[k] if len(tmp)%2 == 1 else (tmp[k-1]+tmp[k])/2
                case _:
                    msg = f'Unknown warmup strategy "{strategy}"'
                    raise ValueError(msg)
        if isinstance(warmup_values[0], list):
            return [aux(values) for values in list(zip(*warmup_values))]
        else:
            return aux(warmup_values)

    def evaluate_variant(self, variant, force=False):
        cached_run = None
        if not force:
            cached_run = self.eval_cache.get(variant.diff) # potentially partial
        run = self.software.evaluate_variant(variant, cached_run)
        self.eval_cache.update(variant.diff, run)
        self.stats['budget'] += getattr(run, 'budget', 0) or 0
        return run
