import pytest

from magpie.core import ExecResult, RunResult, BasicSoftware
from magpie.core import default_scenario

class StubSoftware(BasicSoftware):
    def __init__(self):
        config = default_scenario
        config['software'].update({
            'path': 'foo',
            'target_files': 'foo/bar',
            'possible_edits': 'LineDeletion',
            'fitness': 'time',
        })
        super().__init__(config)

    def reset_contents(self):
        self.contents = {}
        self.locations = {}

@pytest.fixture
def my_software():
    return StubSoftware()

@pytest.fixture
def my_runresult(my_software):
    return RunResult(my_software, 'SUCCESS')


@pytest.mark.parametrize('return_code,status', [
    # SUCCESS on 0
    (0, 'SUCCESS'),
    # CODE_ERROR on everything else
    (1, 'CODE_ERROR'),
    (2, 'CODE_ERROR'),
    (255, 'CODE_ERROR'),
    (-1, 'CODE_ERROR'),
])
def test_process_init(my_software, my_runresult, return_code, status):
    exec_result = ExecResult(['(empty)'], 'SUCCESS', return_code, b'', b'', 1, 0)
    my_software.process_init_exec(my_runresult, exec_result)
    assert my_runresult.status == status, my_runresult


@pytest.mark.parametrize('return_code,status', [
    # SUCCESS on 0
    (0, 'SUCCESS'),
    # CODE_ERROR on everything else
    (1, 'CODE_ERROR'),
    (2, 'CODE_ERROR'),
    (255, 'CODE_ERROR'),
    (-1, 'CODE_ERROR'),
])
def test_process_setup(my_software, my_runresult, return_code, status):
    exec_result = ExecResult(['(empty)'], 'SUCCESS', return_code, b'', b'', 1, 0)
    my_software.process_setup_exec(my_runresult, exec_result)
    assert my_runresult.status == status, my_runresult


@pytest.mark.parametrize('return_code,status', [
    # SUCCESS on 0
    (0, 'SUCCESS'),
    # CODE_ERROR on everything else
    (1, 'CODE_ERROR'),
    (2, 'CODE_ERROR'),
    (255, 'CODE_ERROR'),
    (-1, 'CODE_ERROR'),
])
def test_process_compile(my_software, my_runresult, return_code, status):
    exec_result = ExecResult(['(empty)'], 'SUCCESS', return_code, b'', b'', 1, 0)
    my_software.process_setup_exec(my_runresult, exec_result)
    assert my_runresult.status == status, my_runresult


@pytest.mark.parametrize('return_code,status', [
    # SUCCESS on 0
    (0, 'SUCCESS'),
    # CODE_ERROR on everything else
    (1, 'CODE_ERROR'),
    (2, 'CODE_ERROR'),
    (255, 'CODE_ERROR'),
    (-1, 'CODE_ERROR'),
])
def test_process_test_not_repair(my_software, my_runresult, return_code, status):
    my_software.fitness_type = 'time'
    exec_result = ExecResult(['(empty)'], 'SUCCESS', return_code, b'', b'', 1, 0)
    my_software.process_setup_exec(my_runresult, exec_result)
    assert my_runresult.status == status, my_runresult


@pytest.mark.parametrize('stdout,status,fitness', [
    # SUCCESS when both failed/passed on stdout
    (b'collected 3 items\n 3 failed ; 0 passed', 'SUCCESS', 100.0),
    (b'collected 3 items\n 2 failed ; 1 passed', 'SUCCESS', 66.67),
    (b'collected 3 items\n 1 failed ; 2 passed', 'SUCCESS', 33.33),
    (b'collected 3 items\n 3 passed', 'SUCCESS', 0.0),
    (b'4 runs, 7 assertions, 4 failures, 0 errors, 0 skips', 'SUCCESS', 100.0),
    (b'There were 4 failures:\nFAILURES!!!\nTests run: 4,  Failures: 4', 'SUCCESS', 100.0),
    # PARSE_ERROR on everything else
    (b'', 'PARSE_ERROR', None),
    (b'0 fail', 'PARSE_ERROR', None),
    (b'1 failed', 'PARSE_ERROR', None),
    (b'2 fails', 'PARSE_ERROR', None),
    (b'3 errors', 'PARSE_ERROR', None),
])
def test_process_test_repair(my_software, my_runresult, stdout, status, fitness):
    my_software.fitness_type = 'repair'
    exec_result = ExecResult(['(empty)'], 'SUCCESS', 0, stdout, b'', 1, 0)
    my_software.process_test_exec(my_runresult, exec_result)
    assert my_runresult.status == status
    assert my_runresult.fitness == fitness


@pytest.mark.parametrize('return_code,status', [
    # SUCCESS on 0
    (0, 'SUCCESS'),
    # CODE_ERROR on everything else
    (1, 'CODE_ERROR'),
    (2, 'CODE_ERROR'),
    (255, 'CODE_ERROR'),
    (-1, 'CODE_ERROR'),
])
def test_process_run(my_software, my_runresult, return_code, status):
    exec_result = ExecResult(['(empty)'], 'SUCCESS', return_code, b'', b'', 1, 0)
    my_software.process_run_exec(my_runresult, exec_result)
    assert my_runresult.status == status, my_runresult


@pytest.mark.parametrize('stdout,status,fitness', [
    # SUCCESS on 0
    (b'MAGPIE_FITNESS: 1', 'SUCCESS', 1),
    (b'MAGPIE_FITNESS: -1', 'SUCCESS', -1),
    (b'MAGPIE_FITNESS: 0.5', 'SUCCESS', 0.5),
    (b'MAGPIE_FITNESS: 1e-3', 'SUCCESS', 1e-3),
    # PARSE_ERROR on everything else
    (b'MAGPIE_FITNESS: \n', 'PARSE_ERROR', None),
    (b'MAGPIE_FITNESS: xxx', 'PARSE_ERROR', None),
    (b'FITNESS: 1', 'PARSE_ERROR', None),
    (b'', 'PARSE_ERROR', None),
])
def test_process_run_output(my_software, my_runresult, stdout, status, fitness):
    my_software.fitness_type = 'output'
    exec_result = ExecResult(['(empty)'], 'SUCCESS', 0, stdout, b'', 1, 0)
    my_software.process_run_exec(my_runresult, exec_result)
    assert my_runresult.status == status
    assert my_runresult.fitness == fitness


@pytest.mark.parametrize('stderr,status,fitness', [
    # SUCCESS on POSIX output
    (b'real 1.01\nuser 0.00\nsys 0.00', 'SUCCESS', 1.01),
    # PARSE_ERROR on everything else
    (b'', 'PARSE_ERROR', None),
])
def test_process_run_posixtime(my_software, my_runresult, stderr, status, fitness):
    my_software.fitness_type = 'posix_time'
    exec_result = ExecResult(['(empty)'], 'SUCCESS', 0, b'', stderr, 1, 0)
    my_software.process_run_exec(my_runresult, exec_result)
    assert my_runresult.status == status
    assert my_runresult.fitness == fitness


@pytest.mark.parametrize('stderr,status,fitness', [
    # SUCCESS on PERF output
    (b'       1.001619582 seconds time elapsed', 'SUCCESS', 1.0016),
    # PARSE_ERROR on everything else
    (b'', 'PARSE_ERROR', None),
])
def test_process_run_perftime(my_software, my_runresult, stderr, status, fitness):
    my_software.fitness_type = 'perf_time'
    exec_result = ExecResult(['(empty)'], 'SUCCESS', 0, b'', stderr, 1, 0)
    my_software.process_run_exec(my_runresult, exec_result)
    assert my_runresult.status == status
    assert my_runresult.fitness == fitness


@pytest.mark.parametrize('stderr,status,fitness', [
    # SUCCESS on PERF output
    (b'           190,479      instructions:u            #    0.49  insn per cycle         ', 'SUCCESS', 190479),
    # PARSE_ERROR on everything else
    (b'', 'PARSE_ERROR', None),
])
def test_process_run_perfinstructions(my_software, my_runresult, stderr, status, fitness):
    my_software.fitness_type = 'perf_instructions'
    exec_result = ExecResult(['(empty)'], 'SUCCESS', 0, b'', stderr, 1, 0)
    my_software.process_run_exec(my_runresult, exec_result)
    assert my_runresult.status == status
    assert my_runresult.fitness == fitness
