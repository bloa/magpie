import re

import magpie.utils.known
from magpie.core import BasicFitness


class GnuUserTimeFitness(BasicFitness):
    def process_run_exec(self, run_result, exec_result):
        super().process_run_exec(run_result, exec_result)
        # assume GNU /usr/bin/time
        stderr = exec_result.stderr.decode(magpie.settings.output_encoding)
        m = re.search(r'(\d+\.\d\d)user', stderr)
        try:
            run_result.fitness = float(m.group(1))
        except (AttributeError, ValueError):
            run_result.status = 'PARSE_ERROR'

magpie.utils.known.fitness.append(GnuUserTimeFitness)


class GnuSystemTimeFitness(BasicFitness):
    def process_run_exec(self, run_result, exec_result):
        super().process_run_exec(run_result, exec_result)
        # assume GNU /usr/bin/time
        stderr = exec_result.stderr.decode(magpie.settings.output_encoding)
        m = re.search(r'(\d+\.\d\d)system', stderr)
        try:
            run_result.fitness = float(m.group(1))
        except (AttributeError, ValueError):
            run_result.status = 'PARSE_ERROR'

magpie.utils.known.fitness.append(GnuSystemTimeFitness)


class GnuTimeFitness(BasicFitness):
    def process_run_exec(self, run_result, exec_result):
        super().process_run_exec(run_result, exec_result)
        # assume GNU /usr/bin/time
        stderr = exec_result.stderr.decode(magpie.settings.output_encoding)
        m = re.search(r'(\d*?):?(\d+):(\d\d\.\d\d)elapsed', stderr)
        try:
            run_result.fitness = 60*int(m.group(2)) + float(m.group(3))
            if m.group(1):
                run_result.fitness += 3600*int(m.group(1))
        except (AttributeError, ValueError):
            run_result.status = 'PARSE_ERROR'

magpie.utils.known.fitness.append(GnuTimeFitness)


class GnuMemoryFitness(BasicFitness):
    def process_run_exec(self, run_result, exec_result):
        super().process_run_exec(run_result, exec_result)
        # assume GNU /usr/bin/time
        stderr = exec_result.stderr.decode(magpie.settings.output_encoding)
        m = re.search(r'(\d+)maxresident', stderr)
        try:
            run_result.fitness = int(m.group(1))
        except (AttributeError, ValueError):
            run_result.status = 'PARSE_ERROR'

magpie.utils.known.fitness.append(GnuMemoryFitness)


class GnuMajorPagefaultsFitness(BasicFitness):
    def process_run_exec(self, run_result, exec_result):
        super().process_run_exec(run_result, exec_result)
        # assume GNU /usr/bin/time
        stderr = exec_result.stderr.decode(magpie.settings.output_encoding)
        m = re.search(r'\((\d+)major\+(\d+)minor\)pagefaults', stderr)
        try:
            run_result.fitness = int(m.group(1))
        except (AttributeError, ValueError):
            run_result.status = 'PARSE_ERROR'

magpie.utils.known.fitness.append(GnuMajorPagefaultsFitness)


class GnuMinorPagefaultsFitness(BasicFitness):
    def process_run_exec(self, run_result, exec_result):
        super().process_run_exec(run_result, exec_result)
        # assume GNU /usr/bin/time
        stderr = exec_result.stderr.decode(magpie.settings.output_encoding)
        m = re.search(r'\((\d+)major\+(\d+)minor\)pagefaults', stderr)
        try:
            run_result.fitness = int(m.group(2))
        except (AttributeError, ValueError):
            run_result.status = 'PARSE_ERROR'

magpie.utils.known.fitness.append(GnuMinorPagefaultsFitness)


class GnuPagefaultsFitness(BasicFitness):
    def process_run_exec(self, run_result, exec_result):
        super().process_run_exec(run_result, exec_result)
        # assume GNU /usr/bin/time
        stderr = exec_result.stderr.decode(magpie.settings.output_encoding)
        m = re.search(r'\((\d+)major\+(\d+)minor\)pagefaults', stderr)
        try:
            run_result.fitness = int(m.group(1)) + int(m.group(2))
        except (AttributeError, ValueError):
            run_result.status = 'PARSE_ERROR'

magpie.utils.known.fitness.append(GnuPagefaultsFitness)


class GnuSwapsFitness(BasicFitness):
    def process_run_exec(self, run_result, exec_result):
        super().process_run_exec(run_result, exec_result)
        # assume GNU /usr/bin/time
        stderr = exec_result.stderr.decode(magpie.settings.output_encoding)
        m = re.search(r'(\d+)swaps', stderr)
        try:
            run_result.fitness = int(m.group(1))
        except (AttributeError, ValueError):
            run_result.status = 'PARSE_ERROR'

magpie.utils.known.fitness.append(GnuSwapsFitness)
