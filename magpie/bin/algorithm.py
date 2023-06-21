import itertools
import random
import os
import time

import magpie

from .. import config as magpie_config


class BasicAlgorithm(magpie.base.AbstractAlgorithm):
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
        self.program.batch = batch if any(batch) else [['']] # single empty instance when no batch
        # early exit before warmup
        if self.report['initial_fitness'] is None:
            return
        # reset initial fitness
        empty_patch = magpie.base.Patch()
        run = self.evaluate_patch(empty_patch)
        self.report['initial_fitness'] = run.fitness
        self.report['best_fitness'] = run.fitness
        self.hook_warmup_evaluation('INITIAL', empty_patch, run)
        if run.status != 'SUCCESS':
            raise RuntimeError('initial solution has failed')
        # update best patch
        if self.report['best_patch'] and self.report['best_patch'].edits:
            run = self.evaluate_patch(self.report['best_patch'])
            best = self.dominates(run.fitness, self.report['best_fitness'])
            self.hook_batch_evaluation('BEST', self.report['best_patch'], run, best)
            if run.status == 'SUCCESS' and best:
                self.report['best_fitness'] = run.fitness
            else:
                self.report['best_patch'] = empty_patch

    def hook_warmup(self):
        self.hook_reset_batch()
        self.stats['wallclock_start'] = self.stats['wallclock_warmup'] = time.time()
        self.program.logger.info('==== WARMUP ====')

    def hook_warmup_evaluation(self, count, patch, run):
        self.aux_log_eval(count, run.status, ' ', run.fitness, None, None, run.log)
        if run.status != 'SUCCESS':
            self.program.logger.info('!*'*40)
            self.program.logger.info('CWD: {}'.format(os.path.join(self.program.work_dir, self.program.basename)))
            self.program.logger.info('CMD: {}'.format(run.debug.cmd))
            self.program.logger.info('STATUS: {}'.format(run.debug.status))
            self.program.logger.info('RETURN_CODE: {}'.format(run.debug.return_code))
            self.program.logger.info('RUNTIME: {}'.format(run.debug.runtime))
            try:
                s = run.debug.stdout.decode(magpie_config.output_encoding)
                self.program.logger.info('STDOUT:\n{}'.format(s))
            except UnicodeDecodeError:
                self.program.logger.info('STDOUT: (failed to decode to: {})\n{}'.format(magpie_config.output_encoding, run.debug.stdout))
            try:
                s = run.debug.stderr.decode(magpie_config.output_encoding)
                self.program.logger.info('STDERR:\n{}'.format(s))
            except UnicodeDecodeError:
                s = magpie_config.output_encoding
                self.program.logger.info('STDERR: (failed to decode to: {})\n{}'.format(magpie_config.output_encoding, run.debug.stderr))
            self.program.logger.info('!*'*40)
            self.program.logger.info('Magpie stopped because it was unable to run the (unmodified) target software')
            self.program.logger.info('Self-diagnostic:')
            self.program.self_diagnostic(run)
            self.program.logger.info('!*'*40)

    def hook_batch_evaluation(self, count, patch, run, best=False):
        c = '*' if best else ' '
        self.aux_log_eval(count, run.status, c, run.fitness, self.report['initial_fitness'], len(patch.edits), run.log)

    def hook_start(self):
        if not self.config['possible_edits']:
            raise RuntimeError('possible_edits list is empty')
        # TODO: check that every possible edit can be created and simplify create_edit
        self.stats['wallclock_start'] = time.time() # discards warmup time
        self.program.logger.info('==== START: {} ===='.format(self.__class__.__name__))

    def hook_main_loop(self):
        pass

    def hook_evaluation(self, patch, run, accept=False, best=False):
        if best:
            c = '*'
        elif accept:
            c = '+'
        else:
            c = ' '
        self.program.logger.debug(patch)
        # self.program.logger.debug(run) # uncomment for detail on last cmd
        counter = self.aux_log_counter()
        self.aux_log_eval(counter, run.status, c, run.fitness, self.report['initial_fitness'], len(patch.edits), run.log)
        if accept or best:
            self.program.logger.debug(self.program.diff_patch(patch)) # recomputes contents but meh

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
        self.program.logger.info('{:<7} {:<20} {:>1}{:<24}{}'.format(counter, status, c, str(fitness) + ' ' + s + ' ' + s2, data))

    def aux_log_counter(self):
        return str(self.stats['steps']+1)

    def hook_end(self):
        self.stats['wallclock_end'] = time.time()
        self.stats['wallclock_total'] = self.stats['wallclock_end'] - self.stats['wallclock_start']
        if self.report['best_patch']:
            self.report['diff'] = self.program.diff_patch(self.report['best_patch'])
        self.program.logger.info('==== END ====')
        self.program.logger.info('Reason: {}'.format(self.report['stop']))

    def warmup(self):
        empty_patch = magpie.base.Patch()
        if self.report['initial_patch'] is None:
            self.report['initial_patch'] = empty_patch
        warmup_values = []
        for i in range(max(self.config['warmup'] or 1, 1), 0, -1):
            self.program.base_fitness = None
            self.program.truth_table = {}
            run = self.evaluate_patch(empty_patch, force=True, forget=True)
            l = 'INITIAL' if i == 1 else 'WARM'
            self.hook_warmup_evaluation('WARM', empty_patch, run)
            if run.status != 'SUCCESS':
                raise RuntimeError('initial solution has failed')
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
        self.hook_warmup_evaluation('INITIAL', empty_patch, run)
        self.report['initial_fitness'] = current_fitness
        if self.report['best_patch'] is None:
            self.report['best_fitness'] = current_fitness
            self.report['best_patch'] = empty_patch
        else:
            run = self.evaluate_patch(self.report['best_patch'], force=True)
            self.hook_warmup_evaluation('BEST', empty_patch, run)
            if self.dominates(run.fitness, current_fitness):
                self.report['best_fitness'] = run.fitness
            else:
                self.report['best_patch'] = empty_patch
                self.report['best_fitness'] = current_fitness
        if self.program.base_fitness is None:
            self.program.base_fitness = current_fitness

    def evaluate_patch(self, patch, force=False, forget=False):
        contents = self.program.apply_patch(patch)
        diff = None
        cached_run = None
        if self.config['cache_maxsize'] > 0 and not force:
            diff = self.program.diff_contents(contents)
            cached_run = self.cache_get(diff)
            # no return: now handled in evaluate_contents
        run = self.program.evaluate_contents(contents, cached_run)
        if self.config['cache_maxsize'] > 0 and not forget:
            if not diff:
                diff = self.program.diff_contents(contents)
            self.cache_set(diff, run)
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
