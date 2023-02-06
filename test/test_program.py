import pytest

from magpie.bin import BasicProgram
from magpie.base import ExecResult, RunResult

class StubProgram(BasicProgram):
    def __init__(self):
        config = {
            'software': {
                'path': 'foo',
                'target_files': 'foo/bar',
                'possible_edits': 'LineDeletion',
                'fitness': 'time',
            }
        }
        super().__init__(config)

    def reset_contents(self):
        self.contents = {}
        self.locations = {}

@pytest.fixture
def my_program():
    return StubProgram()

@pytest.fixture
def my_runresult():
    return RunResult('SUCCESS')


def test_process_setup(my_program, my_runresult):
    # SUCCESS on 0
    return_code = 0
    exec_result = ExecResult('SUCCESS', return_code, b'', b'', 1)
    my_program.process_setup_exec(my_runresult, exec_result)
    assert my_runresult.status == 'SUCCESS', my_runresult

    # CODE_ERROR on everything else
    for return_code in [1, 2, 255]:
        exec_result = ExecResult('SUCCESS', return_code, b'', b'', 1)
        my_program.process_setup_exec(my_runresult, exec_result)
        assert my_runresult.status == 'CODE_ERROR', my_runresult


def test_process_compile(my_program, my_runresult):
    # SUCCESS on 0
    return_code = 0
    exec_result = ExecResult('SUCCESS', return_code, b'', b'', 1)
    my_program.process_compile_exec(my_runresult, exec_result)
    assert my_runresult.status == 'SUCCESS', my_runresult

    # CODE_ERROR on everything else
    for return_code in [1, 2, 255]:
        exec_result = ExecResult('SUCCESS', return_code, b'', b'', 1)
        my_program.process_compile_exec(my_runresult, exec_result)
        assert my_runresult.status == 'CODE_ERROR', my_runresult


def test_process_test(my_program, my_runresult):
    # when fitness is NOT repair
    my_program.fitness_type = 'time'

    # SUCCESS on 0
    return_code = 0
    exec_result = ExecResult('SUCCESS', return_code, b'', b'', 1)
    my_program.process_test_exec(my_runresult, exec_result)
    assert my_runresult.status == 'SUCCESS', my_runresult

    # CODE_ERROR on everything else
    for return_code in [1, 2, 255]:
        exec_result = ExecResult('SUCCESS', return_code, b'', b'', 1)
        my_program.process_test_exec(my_runresult, exec_result)
        assert my_runresult.status == 'CODE_ERROR', [my_runresult, return_code]


def test_process_test_repair(my_program, my_runresult):
    # when fitness is repair
    my_program.fitness_type = 'repair'

    # SUCCESS when failed test on stdout
    for stdout in [
            b'0 fail',
            b'1 failed',
            b'2 fails',
            b'3 errors',
    ]:
        exec_result = ExecResult('SUCCESS', 0, stdout, b'', 1)
        my_program.process_test_exec(my_runresult, exec_result)
        assert my_runresult.status == 'SUCCESS', [my_runresult, stdout]

    # SUCCESS when all/some test pass
    for stdout in [
            b'0 pass',
            b'1 passed',
    ]:
        exec_result = ExecResult('SUCCESS', 0, stdout, b'', 1)
        my_program.process_test_exec(my_runresult, exec_result)
        assert my_runresult.status == 'SUCCESS', [my_runresult, stdout]

    # PARSE_ERROR otherwise
    exec_result = ExecResult('SUCCESS', 0, b'', b'', 1)
    my_program.process_test_exec(my_runresult, exec_result)
    assert my_runresult.status == 'PARSE_ERROR'


def test_process_test_repair_fitness(my_program, my_runresult):
    # when fitness is repair
    my_program.fitness_type = 'repair'

    # SUCCESS when failed test on stdout
    for stdout, fit in [
            [b'0 fail', 0],
            [b'1 failed', 1],
            [b'2 fails', 2],
            [b'3 errors', 3],
            [b'0 pass', 0],
            [b'1 passed', 0],
            [b'1 failed ; 0 passed', 1],
            [b'0 failed ; 2 passed', 0],
    ]:
        exec_result = ExecResult('SUCCESS', 0, stdout, b'', 1)
        my_program.process_test_exec(my_runresult, exec_result)
        assert my_runresult.fitness == fit, [my_runresult, stdout, fit]


def test_process_run(my_program, my_runresult):
    # SUCCESS on 0
    return_code = 0
    exec_result = ExecResult('SUCCESS', return_code, b'', b'', 1)
    my_program.process_run_exec(my_runresult, exec_result)
    assert my_runresult.status == 'SUCCESS', my_runresult

    # CODE_ERROR on everything else
    for return_code in [1, 2, 255]:
        exec_result = ExecResult('SUCCESS', return_code, b'', b'', 1)
        my_program.process_run_exec(my_runresult, exec_result)
        assert my_runresult.status == 'CODE_ERROR', [my_runresult, return_code]


def test_process_run_output(my_program, my_runresult):
    # when fitness is repair
    my_program.fitness_type = 'output'

    # SUCCESS when failed test on stdout
    for stdout in [
            b'MAGPIE_FITNESS: 1',
            b'MAGPIE_FITNESS: -1',
            b'MAGPIE_FITNESS: 0.5',
            b'MAGPIE_FITNESS: 1e-3',
    ]:
        exec_result = ExecResult('SUCCESS', 0, stdout, b'', 1)
        my_program.process_run_exec(my_runresult, exec_result)
        assert my_runresult.status == 'SUCCESS', [my_runresult, stdout]

    # PARSE_ERROR otherwise
    exec_result = ExecResult('SUCCESS', 0, b'', b'', 1)
    my_program.process_run_exec(my_runresult, exec_result)
    assert my_runresult.status == 'PARSE_ERROR'


def test_process_run_output_fitness(my_program, my_runresult):
    # when fitness is repair
    my_program.fitness_type = 'output'

    # SUCCESS when failed test on stdout
    for stdout, fit in [
            [b'MAGPIE_FITNESS: 1', 1],
            [b'MAGPIE_FITNESS: -1', -1],
            [b'MAGPIE_FITNESS: 0.5', 0.5],
            [b'MAGPIE_FITNESS: 1e-3', 0.003],
    ]:
        exec_result = ExecResult('SUCCESS', 0, stdout, b'', 1)
        my_program.process_run_exec(my_runresult, exec_result)
        assert my_runresult.status == 'SUCCESS', [my_runresult, stdout]


def test_process_run_posixtime(my_program, my_runresult):
    # when fitness is repair
    my_program.fitness_type = 'posix_time'

    # SUCCESS when POSIX output
    stderr = b'real 1.01\nuser 0.00\nsys 0.00'
    exec_result = ExecResult('SUCCESS', 0, b'', stderr, 1)
    my_program.process_run_exec(my_runresult, exec_result)
    assert my_runresult.status == 'SUCCESS', my_runresult

    # PARSE_ERROR otherwise
    exec_result = ExecResult('SUCCESS', 0, b'', b'', 1)
    my_program.process_run_exec(my_runresult, exec_result)
    assert my_runresult.status == 'PARSE_ERROR'


def test_process_run_posixtime_fitness(my_program, my_runresult):
    # when fitness is repair
    my_program.fitness_type = 'posix_time'

    # SUCCESS when POSIX output
    stderr = b'real 1.01\nuser 0.00\nsys 0.00'
    exec_result = ExecResult('SUCCESS', 0, b'', stderr, 1)
    my_program.process_run_exec(my_runresult, exec_result)
    assert my_runresult.fitness == 1.01, my_runresult


def test_process_run_perftime(my_program, my_runresult):
    # when fitness is repair
    my_program.fitness_type = 'perf_time'

    # SUCCESS when PERF output
    stderr = b'       1.001619582 seconds time elapsed'
    exec_result = ExecResult('SUCCESS', 0, b'', stderr, 1)
    my_program.process_run_exec(my_runresult, exec_result)
    assert my_runresult.status == 'SUCCESS', my_runresult

    # PARSE_ERROR otherwise
    exec_result = ExecResult('SUCCESS', 0, b'', b'', 1)
    my_program.process_run_exec(my_runresult, exec_result)
    assert my_runresult.status == 'PARSE_ERROR'


def test_process_run_perftime_fitness(my_program, my_runresult):
    # when fitness is repair
    my_program.fitness_type = 'perf_time'

    # SUCCESS when PERF output
    stderr = b'       1.001619582 seconds time elapsed'
    exec_result = ExecResult('SUCCESS', 0, b'', stderr, 1)
    my_program.process_run_exec(my_runresult, exec_result)
    assert my_runresult.fitness == 1.0016, my_runresult


def test_process_run_perfinstructions(my_program, my_runresult):
    # when fitness is repair
    my_program.fitness_type = 'perf_instructions'

    # SUCCESS when PERF output
    stderr = b'           190,479      instructions:u            #    0.49  insn per cycle         '
    exec_result = ExecResult('SUCCESS', 0, b'', stderr, 1)
    my_program.process_run_exec(my_runresult, exec_result)
    assert my_runresult.status == 'SUCCESS', my_runresult

    # PARSE_ERROR otherwise
    exec_result = ExecResult('SUCCESS', 0, b'', b'', 1)
    my_program.process_run_exec(my_runresult, exec_result)
    assert my_runresult.status == 'PARSE_ERROR'


def test_process_run_perfinstructions_fitness(my_program, my_runresult):
    # when fitness is repair
    my_program.fitness_type = 'perf_instructions'

    # SUCCESS when PERF output
    stderr = b'           190,479      instructions:u            #    0.49  insn per cycle         '
    exec_result = ExecResult('SUCCESS', 0, b'', stderr, 1)
    my_program.process_run_exec(my_runresult, exec_result)
    assert my_runresult.fitness == 190479, my_runresult
