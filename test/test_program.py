import os
import pytest
import random
import re
import shutil

import pyggi
pyggi.config.enable_astor = True

from pyggi.base import Patch
from pyggi.line import LineProgram, LineInsertion, LineEngine
from pyggi.tree import TreeProgram, StmtInsertion, AstorEngine

class MyLineProgram(LineProgram):
    def compute_fitness(self, result, return_code, stdout, stderr, elapsed_time):
        print(elapsed_time, stdout, stderr)
        m = re.findall("runtime: ([0-9.]+)", stdout)
        if len(m) > 0:
            runtime = m[0]
            failed = re.findall("([0-9]+) failed", stdout)
            pass_all = len(failed) == 0
            failed = int(failed[0]) if not pass_all else 0
            result.fitness = failed
        else:
            result.status = 'PARSE_ERROR'

class MyTreeProgram(TreeProgram):
    def compute_fitness(self, result, return_code, stdout, stderr, elapsed_time):
        print(elapsed_time, stdout, stderr)
        m = re.findall("runtime: ([0-9.]+)", stdout)
        if len(m) > 0:
            runtime = m[0]
            failed = re.findall("([0-9]+) failed", stdout)
            pass_all = len(failed) == 0
            failed = int(failed[0]) if not pass_all else 0
            result.fitness = failed
        else:
            result.status = 'PARSE_ERROR'

@pytest.fixture(scope='session')
def setup_line():
    config = {
        'target_files': ["triangle.py"],
        'test_command': "pytest -s test_triangle.py",
    }
    line_program = MyLineProgram('../sample/Triangle_bug_python', config=config)
    return line_program

@pytest.fixture(scope='session')
def setup_tree():
    config = {
        'target_files': ["triangle.py"],
        'test_command': "pytest -s test_triangle.py",
    }
    tree_program = MyTreeProgram('../sample/Triangle_bug_python', config=config)
    return tree_program

def check_program_validity(program):
    assert not program.path.endswith('/')
    assert program.basename == os.path.basename(program.path)
    assert program.test_command is not None
    assert program.target_files is not None
    assert all([program.engines[target_file] is not None
        for target_file in program.target_files])
    assert all([program.locations[target_file] is not None
        for target_file in program.target_files])

class TestLineProgram(object):

    def test_init(self, setup_line):
        program = setup_line
        check_program_validity(program)

    def test_init_with_dict_type_config(self):
        target_files = ["triangle.py"]
        test_command = "./run.sh"
        config = {
            "target_files": target_files,
            "test_command": test_command
        }

        program = LineProgram('../sample/Triangle_bug_python', config=config)
        check_program_validity(program)
        assert program.test_command == test_command
        assert program.target_files == target_files

    def test_get_engine(self, setup_line):
        program = setup_line
        assert program.get_engine('triangle.py') == LineEngine

    def test_random_target(self, setup_line):
        program = setup_line
        with pytest.raises(KeyError) as e_info:
            program.random_target(target_file="triangle2.py")
        file, _, point = program.random_target(target_type='line')
        assert file in program.target_files
        assert point in range(len(program.locations[file]['line']))

    def test_load_contents(self, setup_line):
        program = setup_line
        assert 'triangle.py' in program.contents
        assert len(program.contents['triangle.py']) > 0

    def test_apply(self, setup_line):
        program = setup_line
        patch = Patch([LineInsertion(('triangle.py', '_inter_line', 1), ('triangle.py', 'line', 10))])
        program.apply(patch)
        file_contents = open(os.path.join(program.work_path, 'triangle.py'), 'r').read()
        assert file_contents == program.dump(program.get_modified_contents(patch), 'triangle.py')

    def test_exec_cmd(self, setup_line):
        program = setup_line
        _, stdout, _, _ = program.exec_cmd(['echo', 'hello'])
        assert stdout.decode('ascii').strip() == "hello"

    def test_evaluate_patch(self, setup_line):
        program = setup_line
        patch = Patch()
        run = program.evaluate_patch(patch)
        assert run.status == 'SUCCESS'
        assert run.fitness is not None

    def test_remove_tmp_variant(self, setup_line):
        program = setup_line
        program.remove_tmp_variant()
        assert not os.path.exists(program.work_path)

class TestTreeProgram(object):

    def test_init(self, setup_tree):
        program = setup_tree
        check_program_validity(program)

    def test_init_with_dict_type_config(self):
        target_files = ["triangle.py"]
        test_command = "./run.sh"
        config = {
            "target_files": target_files,
            "test_command": test_command
        }
        program = MyTreeProgram('../sample/Triangle_bug_python', config=config)
        check_program_validity(program)
        assert program.test_command == test_command
        assert program.target_files == target_files

    def test_get_engine(self, setup_tree):
        program = setup_tree
        with pytest.raises(Exception) as e_info:
            program.get_engine('triangle.html')
        assert program.get_engine('triangle.py') == AstorEngine

    def test_load_contents(self, setup_tree):
        program = setup_tree
        assert 'triangle.py' in program.contents
        assert program.contents['triangle.py'] is not None

    def test_apply(self, setup_tree):
        program = setup_tree
        patch = Patch()
        patch.add(StmtInsertion(('triangle.py', 'stmt', 1), ('triangle.py', 'stmt', 10)))
        program.apply(patch)
        file_contents = open(os.path.join(program.work_path, 'triangle.py'), 'r').read()
        assert file_contents == program.dump(program.get_modified_contents(patch), 'triangle.py')

    def test_diff(self, setup_tree):
        program = setup_tree
        patch = Patch()
        print(patch.raw())
        assert not program.diff(patch).strip()
        patch.add(StmtInsertion(('triangle.py', 'stmt', 1), ('triangle.py', 'stmt', 10)))
        assert program.diff(patch).strip()

    def test_exec_cmd(self, setup_tree):
        program = setup_tree
        _, stdout, _, _ = program.exec_cmd(['echo', 'hello'])
        assert stdout.decode('ascii').strip() == "hello"

    def test_evaluate_patch(self, setup_tree):
        program = setup_tree
        patch = Patch()
        run = program.evaluate_patch(patch)
        assert run.status == 'SUCCESS'
        assert run.fitness is not None

    def test_remove_tmp_variant(self, setup_tree):
        program = setup_tree
        program.remove_tmp_variant()
        assert not os.path.exists(program.work_path)

    def test_clean_work_dir(self, setup_tree):
        program = setup_tree
        program.clean_work_dir()
        assert not os.path.exists(program.work_dir)

@pytest.fixture(scope="session", autouse=True)
def cleanup(request):
    def remove_test_dir():
        shutil.rmtree(pyggi.config.log_dir)
        shutil.rmtree(pyggi.config.work_dir)
    request.addfinalizer(remove_test_dir)
