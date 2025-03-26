import re

import pytest

from magpie import settings
from magpie.core import BasicFitness, BasicSoftware, ExecResult, RunResult, default_scenario


class CustomFitness(BasicFitness):
    def process_test_exec(self, run_result, exec_result):
        # NO call to super() here, due to fitness on failure
        # we check STDOUT for the number of failed test cases
        stdout = exec_result.stdout.decode(settings.output_encoding)
        for fail_regexp, total_regexp in [
            (r'Failures: (\d+)\b', r'^(?:Tests run: |OK \()(\d+)\b'), # custom
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


class StubSoftware(BasicSoftware):
    def __init__(self):
        config = default_scenario.copy()
        config['software'].update({
            'path': 'foo',
            'target_files': 'foo/bar',
            'possible_edits': 'LineDeletion',
            'fitness': 'repair', # replaced
        })
        super().__init__(config)
        self.fitness = [CustomFitness(self)]

    def reset_workdir(self):
        pass

    def reset_contents(self):
        self.contents = {}
        self.locations = {}

@pytest.fixture
def my_software():
    return StubSoftware()

@pytest.fixture
def my_runresult(my_software):
    return RunResult(my_software, 'SUCCESS')

@pytest.mark.parametrize(('return_code', 'status'), [
    # SUCCESS on 0
    (0, 'SUCCESS'),
    # CODE_ERROR on everything else
    (1, 'CODE_ERROR'),
    (2, 'CODE_ERROR'),
    (255, 'CODE_ERROR'),
    (-1, 'CODE_ERROR'),
])
def test_process_inherit(my_software, my_runresult, return_code, status):
    exec_result = ExecResult(['(empty)'], 'SUCCESS', return_code, b'', b'', 1, 0)
    my_software.fitness[0].process_init_exec(my_runresult, exec_result)
    assert my_runresult.status == status, my_runresult

@pytest.mark.parametrize(('stdout', 'status', 'fitness'), [
    # SUCCESS when both failed/passed on stdout
    (b'Tests run: 13,  Failures: 13', 'SUCCESS', 100.0),
    (b'Tests run: 10,  Failures: 5', 'SUCCESS', 50.0),
    (b'OK (13 tests)', 'SUCCESS', 0.0),
    # PARSE_ERROR on everything else
    (b'', 'PARSE_ERROR', None),
])
def test_process_test_repair(my_software, my_runresult, stdout, status, fitness):
    exec_result = ExecResult(['(empty)'], 'SUCCESS', 0, stdout, b'', 1, 0)
    my_software.fitness[0].process_test_exec(my_runresult, exec_result)
    assert my_runresult.status == status
    assert my_runresult.fitness == fitness
