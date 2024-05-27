import re

import magpie.utils.known
from magpie.core import BasicFitness


class OutputFitness(BasicFitness):
    def process_run_exec(self, run_result, exec_result):
        super().process_run_exec(run_result, exec_result)
        # check STDOUT for the string "MAGPIE_FITNESS:"
        stdout = exec_result.stdout.decode(magpie.settings.output_encoding)
        m = re.search('MAGPIE_FITNESS: (.*)', stdout)
        try:
            run_result.fitness = float(m.group(1))
        except (AttributeError, ValueError):
            run_result.status = 'PARSE_ERROR'

magpie.utils.known.fitness.append(OutputFitness)
