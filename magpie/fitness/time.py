import re

import magpie.utils.known
from magpie.core import BasicFitness


class TimeFitness(BasicFitness):
    def process_run_exec(self, run_result, exec_result):
        super().process_run_exec(run_result, exec_result)
        # just use time as seen by the main Python process
        run_result.fitness = round(exec_result.runtime, 4)

magpie.utils.known.fitness.append(TimeFitness)


class PosixTimeFitness(BasicFitness):
    def process_run_exec(self, run_result, exec_result):
        super().process_run_exec(run_result, exec_result)
        # assume a POSIX-compatible output on STDERR
        stderr = exec_result.stderr.decode(magpie.settings.output_encoding)
        m = re.search('real (.*)', stderr)
        try:
            run_result.fitness = float(m.group(1))
        except (AttributeError, ValueError):
            run_result.status = 'PARSE_ERROR'

magpie.utils.known.fitness.append(PosixTimeFitness)


class PerfTimeFitness(BasicFitness):
    def process_run_exec(self, run_result, exec_result):
        super().process_run_exec(run_result, exec_result)
        # assume a perf-like output on STDERR
        stderr = exec_result.stderr.decode(magpie.settings.output_encoding)
        m = re.search('(.*) seconds time elapsed', stderr)
        try:
            run_result.fitness = round(float(m.group(1)), 4)
        except (AttributeError, ValueError):
            run_result.status = 'PARSE_ERROR'

magpie.utils.known.fitness.append(PerfTimeFitness)


class PerfInstructionsFitness(BasicFitness):
    def process_run_exec(self, run_result, exec_result):
        super().process_run_exec(run_result, exec_result)
        # assume a perf-like output on STDERR
        stderr = exec_result.stderr.decode(magpie.settings.output_encoding)
        m = re.search('(.*) instructions', stderr)
        try:
            run_result.fitness = int(m.group(1).replace(',', ''))
        except (AttributeError, ValueError):
            run_result.status = 'PARSE_ERROR'

magpie.utils.known.fitness.append(PerfInstructionsFitness)
