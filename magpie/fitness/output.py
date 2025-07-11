import re

import magpie.utils.known
from magpie.core import TemplatedFitness


class OutputTemplatedFitness(TemplatedFitness):
    def __init__(self, software):
        super().__init__(software)
        assert len(self.TEMPLATE) == 1
        self.key = self.TEMPLATE[0]

    def process_run_exec(self, run_result, exec_result):
        super().process_run_exec(run_result, exec_result)
        # check STDOUT for the key
        stdout = exec_result.stdout.decode(magpie.settings.output_encoding)
        m = re.search(f'{self.key} (.*)', stdout)
        try:
            run_result.fitness = float(m.group(1))
        except (AttributeError, ValueError):
            run_result.status = 'PARSE_ERROR'

class OutputFitness(OutputTemplatedFitness):
    TEMPLATE = ['MAGPIE_FITNESS:']

magpie.utils.known.fitness.append(OutputTemplatedFitness)
magpie.utils.known.fitness.append(OutputFitness)
