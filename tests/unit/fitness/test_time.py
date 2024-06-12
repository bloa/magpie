import pytest

import magpie.utils
from magpie.core import BasicSoftware, ExecResult, RunResult, default_scenario


class StubSoftware(BasicSoftware):
    def __init__(self):
        config = default_scenario.copy()
        config['software'].update({
            'path': 'foo',
            'target_files': 'foo/bar',
            'possible_edits': 'LineDeletion',
            'fitness': 'time',
        })
        super().__init__(config)

    def reset_workdir(self):
        pass

    def reset_contents(self):
        self.contents = {}
        self.locations = {}

@pytest.fixture()
def my_software():
    return StubSoftware()

@pytest.fixture()
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

@pytest.mark.parametrize(('stderr', 'status', 'fitness'), [
    # SUCCESS on POSIX output
    (b'real 1.01\nuser 0.00\nsys 0.00', 'SUCCESS', 1.01),
    # PARSE_ERROR on everything else
    (b'', 'PARSE_ERROR', None),
])
def test_process_run_posixtime(my_software, my_runresult, stderr, status, fitness):
    exec_result = ExecResult(['(empty)'], 'SUCCESS', 0, b'', stderr, 1, 0)
    klass = magpie.utils.convert.fitness_from_string('posix_time')
    klass(my_software).process_run_exec(my_runresult, exec_result)
    assert my_runresult.status == status
    assert my_runresult.fitness == fitness

@pytest.mark.parametrize(('stderr', 'status', 'fitness'), [
    # SUCCESS on PERF output
    (b'       1.001619582 seconds time elapsed', 'SUCCESS', 1.0016),
    # PARSE_ERROR on everything else
    (b'', 'PARSE_ERROR', None),
])
def test_process_run_perftime(my_software, my_runresult, stderr, status, fitness):
    exec_result = ExecResult(['(empty)'], 'SUCCESS', 0, b'', stderr, 1, 0)
    klass = magpie.utils.convert.fitness_from_string('perf_time')
    klass(my_software).process_run_exec(my_runresult, exec_result)
    assert my_runresult.status == status
    assert my_runresult.fitness == fitness


@pytest.mark.parametrize(('stderr', 'status', 'fitness'), [
    # SUCCESS on PERF output
    (b'           190,479      instructions:u            #    0.49  insn per cycle         ', 'SUCCESS', 190479),
    # PARSE_ERROR on everything else
    (b'', 'PARSE_ERROR', None),
])
def test_process_run_perfinstructions(my_software, my_runresult, stderr, status, fitness):
    exec_result = ExecResult(['(empty)'], 'SUCCESS', 0, b'', stderr, 1, 0)
    klass = magpie.utils.convert.fitness_from_string('perf_instructions')
    klass(my_software).process_run_exec(my_runresult, exec_result)
    assert my_runresult.status == status
    assert my_runresult.fitness == fitness
