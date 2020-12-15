import pytest
import copy
from pyggi.line import LineProgram
from pyggi.line import LineReplacement, LineInsertion, LineDeletion
from pyggi.tree import TreeProgram
from pyggi.tree import StmtReplacement, StmtInsertion, StmtDeletion

@pytest.fixture(scope='session')
def setup_lineprogram():
    config = {
        'target_files': ["Triangle.java"],
        'test_command': "./run.sh",
    }
    return LineProgram('../sample/Triangle_bug_java', config=config)

@pytest.fixture(scope='session')
def setup_treeprogram():
    config = {
        'target_files': ["triangle.py"],
        'test_command': "pytest -s test_triangle.py",
    }
    return TreeProgram('../sample/Triangle_bug_python', config=config)

@pytest.fixture(scope='session')
def setup_line_replacement():
    target_file = 'Triangle.java'
    ingr_file = 'Triangle.java'
    target = (target_file, 'line', 1)
    ingredient = (ingr_file, 'line', 2)
    return LineReplacement(target, ingredient), target, ingredient

@pytest.fixture(scope='session')
def setup_line_insertion():
    target_file = 'Triangle.java'
    ingr_file = 'Triangle.java'
    target = (target_file, '_inter_line', 1)
    ingredient = (ingr_file, 'line', 2)
    return LineInsertion(target, ingredient), target, ingredient

@pytest.fixture(scope='session')
def setup_line_deletion():
    target_file = 'Triangle.java'
    target = (target_file, 'line', 2)
    return LineDeletion(target), target

@pytest.fixture(scope='session')
def setup_stmt_replacement():
    target = ('triangle.py', 'stmt', 1)
    ingredient = ('triangle.py', 'stmt', 2)
    return StmtReplacement(target, ingredient), target, ingredient

@pytest.fixture(scope='session')
def setup_stmt_insertion():
    target = ('triangle.py', '_inter_block', 1)
    ingredient = ('triangle.py', 'stmt', 2)
    return StmtInsertion(target, ingredient), target, ingredient

@pytest.fixture(scope='session')
def setup_stmt_deletion():
    target_file = 'triangle.py'
    target = (target_file, 'stmt', 1)
    return StmtDeletion(target), target

class TestEdit(object):
    def test_equal(self):
        target_file = 'Triangle.java'
        ingr_file = 'Triangle.java'
        target = (target_file, 'line', 1)
        ingredient = (ingr_file, 'line', 2)
        ingredient2 = (ingr_file, 'interline', 2)
        line_replacement = LineReplacement(target, ingredient)
        line_replacement2 = LineReplacement(target, ingredient)
        line_replacement3 = LineReplacement(target, target)
        line_insertion = LineInsertion(target, ingredient2)
        assert line_replacement is not line_replacement2
        assert line_replacement == line_replacement2
        assert line_replacement != line_replacement3
        assert line_insertion != line_replacement

class TestLineReplacement(object):
    def test_create(self, setup_lineprogram):
        program = setup_lineprogram
        random_line_replacement = LineReplacement.create(
            program,
            target_file='Triangle.java',
            ingr_file='Triangle.java')

        assert isinstance(random_line_replacement, LineReplacement)
        assert random_line_replacement.data is not None

    def test_apply(self, setup_line_replacement, setup_lineprogram):
        line_replacement, target, ingredient = setup_line_replacement
        program = setup_lineprogram
        new_locations = copy.deepcopy(program.locations)
        new_contents = copy.deepcopy(program.contents)
        line_replacement.apply(program, new_contents, new_locations)
        assert new_contents[target[0]][target[2]] == program.contents[ingredient[0]][ingredient[2]]
        assert program.locations[target[0]][target[1]] == new_locations[target[0]][target[1]]
        assert program.contents != new_contents

class TestLineInsertion(object):
    def test_create(self, setup_lineprogram):
        program = setup_lineprogram
        random_line_insertion = LineInsertion.create(
            program, target_file='Triangle.java', ingr_file='Triangle.java')

        assert isinstance(random_line_insertion, LineInsertion)

    def test_apply(self, setup_line_insertion, setup_lineprogram):
        line_insertion, target, ingredient = setup_line_insertion
        program = setup_lineprogram
        new_locations = copy.deepcopy(program.locations)
        new_contents = copy.deepcopy(program.contents)
        line_insertion.apply(program, new_contents, new_locations)
        assert new_contents[target[0]][target[2]] == program.contents[ingredient[0]][ingredient[2]]
        assert program.locations[target[0]][target[1]] != new_locations[target[0]][target[1]]
        assert program.contents != new_contents

class TestLineDeletion(object):
    def test_create(self, setup_lineprogram):
        program = setup_lineprogram
        random_line_deletion = LineDeletion.create(
            program, target_file='Triangle.java')

        assert isinstance(random_line_deletion, LineDeletion)

    def test_apply(self, setup_line_deletion, setup_lineprogram):
        line_deletion, target = setup_line_deletion
        program = setup_lineprogram
        new_locations = copy.deepcopy(program.locations)
        new_contents = copy.deepcopy(program.contents)
        line_deletion.apply(program, new_contents, new_locations)
        assert new_contents[target[0]][target[2]] is None
        assert program.locations[target[0]] == new_locations[target[0]]

class TestStmtReplacement(object):
    def test_create(self, setup_treeprogram):
        program = setup_treeprogram
        random_stmt_replacement = StmtReplacement.create(
            program,
            target_file='triangle.py',
            ingr_file='triangle.py')

        assert isinstance(random_stmt_replacement, StmtReplacement)
        assert random_stmt_replacement.data is not None

    def test_apply(self, setup_stmt_replacement, setup_treeprogram):
        stmt_replacement, target, ingredient = setup_stmt_replacement
        program = setup_treeprogram
        new_locations = copy.deepcopy(program.locations)
        new_contents = copy.deepcopy(program.contents)
        stmt_replacement.apply(program, new_contents, new_locations)
        assert program.locations[target[0]] != len(new_locations[target[0]])
        assert program.contents != new_contents

class TestStmtInsertion(object):
    def test_create(self, setup_treeprogram):
        program = setup_treeprogram
        random_stmt_insertion = StmtInsertion.create(
            program, target_file='triangle.py', ingr_file='triangle.py')

        assert isinstance(random_stmt_insertion, StmtInsertion)

    def test_apply(self, setup_stmt_insertion, setup_treeprogram):
        stmt_insertion, target, ingredient = setup_stmt_insertion
        program = setup_treeprogram
        new_locations = copy.deepcopy(program.locations)
        new_contents = copy.deepcopy(program.contents)
        stmt_insertion.apply(program, new_contents, new_locations)
        assert program.locations[target[0]] != new_locations[target[0]]
        assert program.contents != new_contents

class TestStmtDeletion(object):
    def test_create(self, setup_treeprogram):
        program = setup_treeprogram
        random_stmt_deletion = StmtDeletion.create(
            program, target_file='triangle.py')

        assert isinstance(random_stmt_deletion, StmtDeletion)

    def test_apply(self, setup_stmt_deletion, setup_treeprogram):
        stmt_deletion, target = setup_stmt_deletion
        program = setup_treeprogram
        new_locations = copy.deepcopy(program.locations)
        new_contents = copy.deepcopy(program.contents)
        stmt_deletion.apply(program, new_contents, new_locations)
        assert program.locations[target[0]] == new_locations[target[0]]
