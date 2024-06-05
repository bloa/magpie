import pytest

from magpie.core import BasicSoftware, ExecResult, RunResult, default_scenario


class StubSoftware(BasicSoftware):
    def __init__(self):
        config = default_scenario.copy()
        config['software'].update({
            'path': 'foo',
            'target_files': 'foo/bar',
            'possible_edits': 'LineDeletion',
            'fitness': 'output',
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

@pytest.mark.parametrize(('stdout', 'status', 'fitness'), [
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
def test_process_run(my_software, my_runresult, stdout, status, fitness):
    exec_result = ExecResult(['(empty)'], 'SUCCESS', 0, stdout, b'', 1, 0)
    my_software.fitness[0].process_run_exec(my_runresult, exec_result)
    assert my_runresult.status == status
    assert my_runresult.fitness == fitness
