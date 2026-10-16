import contextlib
import shlex

import magpie

from .abstract_evalmanager import AbstractEvalManager
from .runresult import RunResult


class BasicEvalManager(AbstractEvalManager):
    def __init__(self, software, exec_manager):
        self.software = software
        self.exec_manager = exec_manager
        self.config = {}
        self.batch = [['']] # single empty instance
        self.report = {}
        self.stats = {}
        self.cache = {}
        self.cache_hits = {}

    def setup(self):
        sec = self.software.config['search']
        self.config['maxsize'] = int(val) if (val := sec['cache_maxsize']) else 0
        self.config['keep'] = float(sec['cache_keep'])

        self.reset()

    def reset(self):
        self.stats = {}
        self.stats['hits'] = 0
        self.stats['misses'] = 0
        self.cache = {}
        self.cache_hits = {}

    def evaluate_variant(self, variant, counter=None, force=False):
        cached_run = None
        if not force:
            cached_run = self.cache_get(variant.diff) # potentially partial
        with self.exec_manager.add_to_env(counter=counter, patch=variant.patch):
            run = self._evaluate_variant(variant, cached_run)
        self.cache_update(variant.diff, run)
        return run

    def cache_get(self, diff):
        try:
            run = self.cache[diff]
        except KeyError:
            self.stats['misses'] += 1
            return None
        else:
            self.stats['hits'] += 1
            if self.config['maxsize'] > 0:
                self.cache_hits[diff] += 1
            run.cached = True
            run.updated = False
            return run

    def cache_update(self, diff, run):
        msize = self.config['maxsize']
        if msize == 0:
            return
        if msize < len(self.cache_hits):
            keep = self.config['keep']
            hits = sorted(self.cache.keys(), key=lambda k: 999 if len(k) == 0 else self.cache_hits[k])
            for k in hits[:int(msize*(1-keep))]:
                del self.cache[k]
            self.cache_hits = dict.fromkeys(self.cache, 0)
        if diff not in self.cache:
            self.cache_hits[diff] = 0
        self.cache[diff] = run

    def _evaluate_variant(self, variant, cached_run=None):
        # check batch sync
        if cached_run is None:
            # new variant
            self.exec_manager.write_variant(variant)
        elif not cached_run.cache.keys():
            # cached (failed) --> early exit
            return cached_run
        elif {inst for b in self.batch for inst in b}.issubset(cached_run.cache.keys()):
            # cached (complete) --> early exit
            self.process_batch_final(cached_run)
            return cached_run
        else:
            # partially cached
            self.exec_manager.write_variant(variant)

        # evaluate
        variant_work_path = self.exec_manager.variant_work_path(variant)
        run_result = cached_run or RunResult(variant, 'UNKNOWN_ERROR')
        run_result.updated = True

        with contextlib.chdir(variant_work_path):
            raw_fitness_values = {}

            # one-time setup
            if not self.software.setup_performed:
                self.software.setup_performed = True

                # make sure this is the unmodified software
                for filename in self.software.target_files:
                    model = variant.models[filename]
                    if model.dump() != model.cached_dump:
                        raise AssertionError

                # run "[software] setup_cmd" if provided
                if self.software.setup_cmd:
                    # setup
                    cli = self.compute_local_cli(variant, 'setup')
                    setup_cmd = self.software.setup_cmd.strip()
                    if '{PARAMS}' in self.software.setup_cmd:
                        setup_cmd = setup_cmd.replace('{PARAMS}', cli)
                    else:
                        setup_cmd = f'{setup_cmd} {cli}'
                    timeout = self.software.setup_timeout or magpie.settings.default_timeout
                    lengthout = self.software.setup_lengthout or magpie.settings.default_lengthout
                    exec_result = self.exec_manager.exec_cmd(shlex.split(setup_cmd),
                                                             timeout=timeout,
                                                             lengthout=lengthout)
                    run_result.status = exec_result.status
                    run_result.last_exec = exec_result
                    if run_result.status == 'SUCCESS':
                        for (name, fit) in self.software.fitness_objectives.items():
                            run_result.fitness = None
                            fit.process_setup_exec(run_result, exec_result)
                            if run_result.fitness is not None:
                                raw_fitness_values[name] = run_result.fitness
                    if run_result.status != 'SUCCESS':
                        run_result.status = f'SETUP_{run_result.status}'
                        run_result.fitness = None
                        return run_result

                # sync work directory
                self.exec_manager.sync_folder(self.software.path, variant_work_path)

            # make sure ingredient files are unmodified
            for filename in self.software.ingredient_files:
                model = variant.models[filename]
                if model.dump() != model.cached_dump:
                    raise AssertionError

            # run "[software] compile_cmd" if provided
            if self.software.compile_cmd:
                cli = self.compute_local_cli(variant, 'compile')
                compile_cmd = self.software.compile_cmd.strip()
                if '{PARAMS}' in self.software.compile_cmd:
                    compile_cmd = compile_cmd.replace('{PARAMS}', cli)
                else:
                    compile_cmd = f'{compile_cmd} {cli}'
                timeout = self.software.compile_timeout or magpie.settings.default_timeout
                lengthout = self.software.compile_lengthout or magpie.settings.default_lengthout
                exec_result = self.exec_manager.exec_cmd(shlex.split(compile_cmd),
                                                         timeout=timeout,
                                                         lengthout=lengthout)
                run_result.status = exec_result.status
                run_result.last_exec = exec_result
                if run_result.status == 'SUCCESS':
                    for (name, fit) in self.software.fitness_objectives.items():
                        run_result.fitness = None
                        fit.process_compile_exec(run_result, exec_result)
                        if run_result.fitness is not None:
                            raw_fitness_values[name] = run_result.fitness
                if run_result.status != 'SUCCESS':
                    run_result.status = f'COMPILE_{run_result.status}'
                    run_result.fitness = None
                    return run_result

            # run "[software] test_cmd" if provided
            if self.software.test_cmd:
                cli = self.compute_local_cli(variant, 'test')
                test_cmd = self.software.test_cmd.strip()
                if '{PARAMS}' in self.software.test_cmd:
                    test_cmd = test_cmd.replace('{PARAMS}', cli)
                else:
                    test_cmd = f'{test_cmd} {cli}'
                timeout = self.software.test_timeout or magpie.settings.default_timeout
                lengthout = self.software.test_lengthout or magpie.settings.default_lengthout
                exec_result = self.exec_manager.exec_cmd(shlex.split(test_cmd),
                                                         timeout=timeout,
                                                         lengthout=lengthout)
                run_result.status = exec_result.status
                run_result.last_exec = exec_result
                if run_result.status == 'SUCCESS':
                    for (name, fit) in self.software.fitness_objectives.items():
                        run_result.fitness = None
                        fit.process_test_exec(run_result, exec_result)
                        if run_result.fitness is not None:
                            raw_fitness_values[name] = run_result.fitness
                if run_result.status != 'SUCCESS':
                    run_result.status = f'TEST_{run_result.status}'
                    run_result.fitness = None
                    return run_result

            default_raw_fitness_values = raw_fitness_values.copy()
            # run "[software] run_cmd" if provided
            if self.software.run_cmd:
                cli = self.compute_local_cli(variant, 'run')
                timeout = self.software.run_timeout or magpie.settings.default_timeout
                lengthout = self.software.run_lengthout or magpie.settings.default_lengthout
                batch_timeout = self.software.batch_timeout
                batch_lengthout = self.software.batch_lengthout
                insts = [inst for b in self.batch for inst in b]
                for inst in insts:
                    raw_fitness_values = default_raw_fitness_values.copy()
                    if inst in run_result.cache:
                        continue
                    run_cmd = self.software.run_cmd.strip()
                    if '{INST}' in self.software.run_cmd:
                        run_cmd = run_cmd.replace('{INST}', inst)
                    else:
                        run_cmd = f'{run_cmd} {inst}'
                    if '{PARAMS}' in self.software.run_cmd:
                        run_cmd = run_cmd.replace('{PARAMS}', cli)
                    else:
                        run_cmd = f'{run_cmd} {cli}'
                    exec_result = self.exec_manager.exec_cmd(shlex.split(run_cmd),
                                                             timeout=timeout,
                                                             lengthout=lengthout)
                    run_result.status = exec_result.status
                    run_result.last_exec = exec_result
                    if run_result.status == 'SUCCESS':
                        for (name, fit) in self.software.fitness_objectives.items():
                            run_result.fitness = None
                            fit.process_run_exec(run_result, exec_result)
                            if run_result.fitness is not None:
                                raw_fitness_values[name] = run_result.fitness
                    run_result.fitness = self.process_final_fitness(raw_fitness_values)
                    self.process_batch_single(run_result, inst)
                    if run_result.status != 'SUCCESS':
                        run_result.status = f'RUN_{run_result.status}'
                        break
                    if batch_timeout:
                        batch_timeout -= exec_result.runtime
                        if batch_timeout < 0:
                            run_result.status = 'BATCH_TIMEOUT'
                            break
                    if batch_lengthout:
                        batch_lengthout -= exec_result.output_length
                        if batch_lengthout < 0:
                            run_result.status = 'BATCH_LENGTHOUT'
                            break
                self.process_batch_final(run_result)
            else:
                run_result.fitness = self.process_final_fitness(raw_fitness_values)

        # final process
        return run_result

    def compute_local_cli(self, variant, step):
        cli = ''
        for target in self.software.target_files:
            model = variant.models[target]
            cli = model.update_cli(variant, cli, step)
        return cli

    def process_final_fitness(self, raw_fitness_values):
        final_fitness = []
        for tree in self.software.fitness_trees:
            try:
                fit = tree.evaluate(raw_fitness_values)
            except KeyError:
                return None
            final_fitness.append(fit)
        return final_fitness

    def process_batch_single(self, run_result, inst):
        run_result.cache[inst] = (run_result.status, run_result.fitness)
        if inst != '':
            self.software.logger.debug('EXEC> %s %s %s', inst, run_result.status, run_result.fitness)

    def process_batch_final(self, run_result):
        fit_per_batch = []
        for b in self.batch:
            bin_fitness = []
            for inst in b:
                status, fitness = run_result.cache[inst]
                if status != 'SUCCESS':
                    # TODO: penalised fitness
                    run_result.fitness = None
                    return
                bin_fitness.append(fitness)
            multi = len(bin_fitness[0]) > 1
            if self.software.batch_bin_fitness_strategy == 'aggregate':
                fit_per_batch.extend(bin_fitness) # ???
            else:
                acc = []
                tmp = [list(a) for a in zip(*bin_fitness)] if multi else bin_fitness
                for a in tmp: # a_k = fitness values per instance for fitness k
                    if len(a) == 1: # single instance
                        v = a[0]
                        precision = len(str(float(v)))
                    else:
                        precision = max(len(str(float(x)).split('.')[1]) for x in a)
                        if self.software.batch_bin_fitness_strategy == 'sum':
                            v = sum(a)
                        elif self.software.batch_bin_fitness_strategy == 'average':
                            v = sum(a)/len(a)
                            precision += 1
                        elif self.software.batch_bin_fitness_strategy == 'median':
                            if len(a) % 2 == 0:
                                v = sorted(a)[len(a)//2]
                            else:
                                v = sum(sorted(a)[len(a)//2:len(a)//2+2])/2
                                precision += 1
                        elif self.software.batch_bin_fitness_strategy == 'q10':
                            if len(a) % 10 == 0:
                                v = sorted(a)[len(a)//10]
                            else:
                                v = sum(sorted(a)[len(a)//10:len(a)//10+2])/2
                                precision += 1
                        elif self.software.batch_bin_fitness_strategy == 'q25':
                            if len(a) % 4 == 0:
                                v = sorted(a)[len(a)//4]
                            else:
                                v = sum(sorted(a)[len(a)//10:len(a)//10+2])/2
                                precision += 1
                        elif self.software.batch_bin_fitness_strategy == 'q75':
                            if len(a) % 4 == 0:
                                v = sorted(a)[3*len(a)//4]
                            else:
                                v = sum(sorted(a)[3*len(a)//4:3*len(a)//4+2])/2
                                precision += 1
                        elif self.software.batch_bin_fitness_strategy == 'q90':
                            if len(a) % 10 == 0:
                                v = sorted(a)[len(a)//10]
                            else:
                                v = sum(sorted(a)[9*len(a)//10:9*len(a)//10+2])/2
                                precision += 1
                    acc.append(round(v, precision))
                fit_per_batch.append(acc)
        acc = []
        tmp = [list(a) for a in zip(*fit_per_batch)]
        for a in tmp: # a_k = fitness values per bin for fitness k
            if len(a) == 1: # single bin
                v = a[0]
                precision = len(str(float(v)))
            else:
                precision = max(len(str(float(x)).split('.')[1]) for x in a)
                if self.software.batch_fitness_strategy == 'sum':
                    v = sum(a)
                elif self.software.batch_fitness_strategy == 'average':
                    v = sum(a)/len(a)
                    precision += 1
                elif self.software.batch_fitness_strategy == 'median':
                    if len(a) % 2 == 0:
                        v = sorted(a)[len(a)//2]
                    else:
                        v = sum(sorted(a)[len(a)//2:len(a)//2+2])/2
                        precision += 1
            acc.append(round(v, precision))
        run_result.fitness = acc
