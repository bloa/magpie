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

@pytest.fixture
def my_execresult():
    return ExecResult(
        ['(empty)'],
        'SUCCESS',
        0,
        b"""algos  core __init__.py  models   scripts      utils
bin    fitness __main__.py  __pycache__  settings.py """,
        b"""	Command being timed: "ls magpie"
	User time (seconds): 0.00
	System time (seconds): 0.00
	Percent of CPU this job got: 100%
	Elapsed (wall clock) time (h:mm:ss or m:ss): 0:00.00
	Average shared text size (kbytes): 0
	Average unshared data size (kbytes): 0
	Average stack size (kbytes): 0
	Average total size (kbytes): 0
	Maximum resident set size (kbytes): 2048
	Average resident set size (kbytes): 0
	Major (requiring I/O) page faults: 0
	Minor (reclaiming a frame) page faults: 102
	Voluntary context switches: 1
	Involuntary context switches: 0
	Swaps: 0
	File system inputs: 0
	File system outputs: 0
	Socket messages sent: 0
	Socket messages received: 0
	Signals delivered: 0
	Page size (bytes): 4096
	Exit status: 0""", 1, 0)

@pytest.mark.parametrize(('name', 'status', 'fitness'), [
    ('gnutime<stacksize>', 'SUCCESS', 0),
    ('gnutime<Voluntary context switches>', 'SUCCESS', 1),
    ('gnutime<foobar>', 'PARSE_ERROR', None),
])
def test_dispatch(my_runresult, my_execresult, name, status, fitness):
    klass = magpie.utils.convert.fitness_from_string(name)
    klass(my_software).process_run_exec(my_runresult, my_execresult)
    assert my_runresult.status == status
    assert my_runresult.fitness == fitness
