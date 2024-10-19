import pathlib

import magpie.utils.known
from magpie.core import BasicFitness


class BloatLinesFitness(BasicFitness):
    def process_test_exec(self, run_result, exec_result):
        super().process_test_exec(run_result, exec_result)
        # ignore exec_result, counts lines from disk directly
        run_result.fitness = 0
        for filename in self.software.target_files:
            renamed = run_result.variant.models[filename].renamed_filename
            with pathlib.Path(renamed).open('r') as target:
                run_result.fitness += len(target.readlines())

magpie.utils.known.fitness.append(BloatLinesFitness)


class BloatWordsFitness(BasicFitness):
    def process_test_exec(self, run_result, exec_result):
        super().process_test_exec(run_result, exec_result)
        # ignore exec_result, counts words from disk directly
        run_result.fitness = 0
        for filename in self.software.target_files:
            renamed = run_result.variant.models[filename].renamed_filename
            with pathlib.Path(renamed).open('r') as target:
                run_result.fitness += sum(len(s.split()) for s in target)

magpie.utils.known.fitness.append(BloatWordsFitness)


class BloatCharsFitness(BasicFitness):
    def process_test_exec(self, run_result, exec_result):
        super().process_test_exec(run_result, exec_result)
        # ignore exec_result, counts chars from disk directly
        run_result.fitness = 0
        for filename in self.software.target_files:
            renamed = run_result.variant.models[filename].renamed_filename
            with pathlib.Path(renamed).open('r') as target:
                run_result.fitness += sum(len(s) for s in target)

magpie.utils.known.fitness.append(BloatCharsFitness)
