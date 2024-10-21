import re

import magpie.utils.known
from magpie.core import BasicFitness


class RepairFitness(BasicFitness):
    def process_test_exec(self, run_result, exec_result):
        # NO call to super() here, due to fitness on failure
        # we check STDOUT for the number of failed test cases
        stdout = exec_result.stdout.decode(magpie.settings.output_encoding)
        for fail_regexp, total_regexp in [
            (r'Failures: (\d+)\b', r'^(?:Tests run: |OK \()(\d+)\b'), # junit
            (r'\b(\d+) (?:failed|error)', r'^collected (\d+) items'), # pytest
            (r' (\d+) (?:failures|errors)', r'^(\d+) runs,'), # minitest
        ]:
            fail_matches = re.findall(fail_regexp, stdout, re.MULTILINE)
            total_matches = re.findall(total_regexp, stdout, re.MULTILINE)
            n_fail = 0
            n_total = 0
            try:
                for m in fail_matches:
                    n_fail += float(m)
                for m in total_matches:
                    n_total += float(m)
            except ValueError:
                run_result.status = 'PARSE_ERROR'
            if n_total > 0:
                run_result.fitness = round(100*n_fail/n_total, 2)
                break
        else:
            run_result.status = 'PARSE_ERROR'

magpie.utils.known.fitness.append(RepairFitness)
