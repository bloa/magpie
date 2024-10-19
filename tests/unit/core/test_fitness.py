import pytest

from magpie.core import BasicFitness, ExecResult, RunResult


@pytest.fixture
def my_runresult():
    return RunResult(None, 'SUCCESS')

@pytest.mark.parametrize(('return_code', 'status'), [
    # SUCCESS on 0
    (0, 'SUCCESS'),
    # CODE_ERROR on everything else
    (1, 'CODE_ERROR'),
    (2, 'CODE_ERROR'),
    (255, 'CODE_ERROR'),
    (-1, 'CODE_ERROR'),
])
def test_process_init(my_runresult, return_code, status):
    exec_result = ExecResult(['(empty)'], 'SUCCESS', return_code, b'', b'', 1, 0)
    BasicFitness.process_init_exec(None, my_runresult, exec_result)
    assert my_runresult.status == status, my_runresult
