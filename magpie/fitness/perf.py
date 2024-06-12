import re

import magpie.utils.known
from magpie.core import TemplatedFitness


class PerfTemplatedFitness(TemplatedFitness):
    KEY = None

    @classmethod
    def template(cls, *args):
        super().template(*args)
        assert len(cls.TEMPLATE) == 1
        cls.KEY = cls.TEMPLATE[0].lower().replace(' ', '')

    def process_run_exec(self, run_result, exec_result):
        super().process_run_exec(run_result, exec_result)
        # assume perf stat
        stderr = exec_result.stderr.decode(magpie.settings.output_encoding)
        try:
            for line in stderr.splitlines():
                tmp = line.lower().replace(' ', '')
                if m := re.search(rf'(\d+\.\d+).*{self.KEY}', tmp):
                    run_result.fitness = float(m.group(1))
                    break
                if m := re.search(rf'(\d+\.\d+)%?.*{self.KEY}', tmp):
                    run_result.fitness = float(m.group(1))
                    break
                if m := re.search(rf'(\d+(?:,\d\d\d)*).*{self.KEY}', tmp):
                    run_result.fitness = int(m.group(1).replace(',', ''))
                    break
            else:
                run_result.status = 'PARSE_ERROR'
        except (AttributeError, ValueError):
            run_result.status = 'PARSE_ERROR'

magpie.utils.known.fitness.append(PerfTemplatedFitness)
