import pytest

import magpie.utils
from magpie.core import ExecResult, RunResult

from .stub import StubSoftware


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
    klass = magpie.utils.convert.fitness_from_string('repair')
    klass(my_software).process_init_exec(my_runresult, exec_result)
    assert my_runresult.status == status, my_runresult

@pytest.mark.parametrize(('stdout', 'status', 'fitness'), [
    # SUCCESS when both failed/passed on stdout
    (b'collected 3 items\n 3 failed ; 0 passed', 'SUCCESS', 100.0),
    (b'collected 3 items\n 2 failed ; 1 passed', 'SUCCESS', 66.67),
    (b'collected 3 items\n 1 failed ; 2 passed', 'SUCCESS', 33.33),
    (b'collected 3 items\n 3 passed', 'SUCCESS', 0.0),
    (b'4 runs, 7 assertions, 4 failures, 0 errors, 0 skips', 'SUCCESS', 100.0),
    (b'There were 4 failures:\nFAILURES!!!\nTests run: 4,  Failures: 4', 'SUCCESS', 100.0),
    (b'Tests run: 10,  Failures: 5', 'SUCCESS', 50.0),
    (b'OK (13 tests)', 'SUCCESS', 0.0),
    # PARSE_ERROR on everything else
    (b'', 'PARSE_ERROR', None),
    (b'0 fail', 'PARSE_ERROR', None),
    (b'1 failed', 'PARSE_ERROR', None),
    (b'2 fails', 'PARSE_ERROR', None),
    (b'3 errors', 'PARSE_ERROR', None),
])
def test_process_test_repair_stdout(my_software, my_runresult, stdout, status, fitness):
    exec_result = ExecResult(['(empty)'], 'SUCCESS', 0, stdout, b'', 1, 0)
    klass = magpie.utils.convert.fitness_from_string('repair')
    klass(my_software).process_test_exec(my_runresult, exec_result)
    assert my_runresult.status == status
    assert my_runresult.fitness == fitness

@pytest.mark.parametrize(('stderr', 'status', 'fitness'), [
    # SUCCESS when both failed/passed on stderr
    (b'10 tests completed, 6 failed', 'SUCCESS', 60.0),
    # PARSE_ERROR on everything else
    (b'', 'PARSE_ERROR', None),
    (b'0 fail', 'PARSE_ERROR', None),
    (b'1 failed', 'PARSE_ERROR', None),
    (b'2 fails', 'PARSE_ERROR', None),
    (b'3 errors', 'PARSE_ERROR', None),
])
def test_process_test_repair_stderr(my_software, my_runresult, stderr, status, fitness):
    exec_result = ExecResult(['(empty)'], 'SUCCESS', 0, b'', stderr, 1, 0)
    klass = magpie.utils.convert.fitness_from_string('repair')
    klass(my_software).process_test_exec(my_runresult, exec_result)
    assert my_runresult.status == status
    assert my_runresult.fitness == fitness

@pytest.mark.parametrize(('stdout', 'return_code', 'status', 'fitness'), [
    # SUCCESS when good return code and known key phrase on stdout
    (b'BUILD SUCCESSFUL', 0, 'SUCCESS', 0.0),
    # PARSE_ERROR on everything else
    (b'', 0, 'PARSE_ERROR', None),
    (b'foo', 0, 'PARSE_ERROR', None),
    (b'', 1, 'PARSE_ERROR', None),
    (b'BUILD SUCCESSFUL', 1, 'PARSE_ERROR', None),
])
def test_process_test_badoutput(my_software, my_runresult, stdout, return_code, status, fitness):
    exec_result = ExecResult(['(empty)'], 'SUCCESS', return_code, stdout, b'', 1, 0)
    klass = magpie.utils.convert.fitness_from_string('repair')
    klass(my_software).process_test_exec(my_runresult, exec_result)
    assert my_runresult.status == status
    assert my_runresult.fitness == fitness
