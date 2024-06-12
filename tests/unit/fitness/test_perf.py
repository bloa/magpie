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

@pytest.fixture()
def my_execresult():
    return ExecResult(
        ['(empty)'],
        'SUCCESS',
        0,
        b"""algos  core __init__.py  models   scripts      utils
bin    fitness __main__.py  __pycache__  settings.py """,
        b"""
 Performance counter stats for 'ls magpie':

              1.65 msec task-clock:u                     #    0.513 CPUs utilized             
                 0      context-switches:u               #    0.000 /sec                      
                 0      cpu-migrations:u                 #    0.000 /sec                      
                79      page-faults:u                    #   48.003 K/sec                     
           543,874      cpu_atom/cycles/u                #    0.330 GHz                       
     <not counted>      cpu_core/cycles/u                                                       (0.00%)
           355,765      cpu_atom/instructions/u          #    0.65  insn per cycle            
     <not counted>      cpu_core/instructions/u                                                 (0.00%)
            71,898      cpu_atom/branches/u              #   43.687 M/sec                     
     <not counted>      cpu_core/branches/u                                                     (0.00%)
             4,879      cpu_atom/branch-misses/u         #    6.79% of all branches           
     <not counted>      cpu_core/branch-misses/u                                                (0.00%)
             TopdownL1 (cpu_atom)                 #     55.0 %  tma_bad_speculation    
                                                  #     15.2 %  tma_retiring           
                                                  #      0.0 %  tma_backend_bound      
                                                  #      0.0 %  tma_backend_bound_aux  
                                                  #     29.8 %  tma_frontend_bound     

       0.003210766 seconds time elapsed

       0.000000000 seconds user
       0.003163000 seconds sys


""", 1, 0)

@pytest.mark.parametrize(('name', 'status', 'fitness'), [
    ('perf<page-faults:u>', 'SUCCESS', 79),
    ('perf<cpu_atom/instructions/u>', 'SUCCESS', 355765),
    ('perf<tma_bad_speculation>', 'SUCCESS', 55.0),
    ('perf<time elapsed>', 'SUCCESS', 0.003210766),
    ('perf<foobar>', 'PARSE_ERROR', None),
])
def test_dispatch(my_runresult, my_execresult, name, status, fitness):
    klass = magpie.utils.convert.fitness_from_string(name)
    klass(my_software).process_run_exec(my_runresult, my_execresult)
    assert my_runresult.status == status
    assert my_runresult.fitness == fitness
