import random
from ..base import AbstractEdit
from . import AbstractTreeEngine, XmlEngine


class StmtReplacement(AbstractEdit):
    def apply(self, program, new_contents, modification_points):
        engine = program.engines[self.target[0]]
        return engine.do_replace(program, self.target, self.data[0], new_contents, modification_points)

    @classmethod
    def create(cls, program, target_file=None, ingr_file=None, method='random'):
        if target_file is None:
            target_file = program.random_file(AbstractTreeEngine)
        if ingr_file is None:
            ingr_file = program.random_file(engine=program.engines[target_file])
        assert program.engines[target_file] == program.engines[ingr_file]
        return cls(program.random_target(target_file, method),
                   program.random_target(ingr_file, 'random'))

class StmtInsertion(AbstractEdit):
    def apply(self, program, new_contents, modification_points):
        engine = program.engines[self.target[0]]
        return engine.do_insert(program, self.target, self.data[0], self.data[1], new_contents, modification_points)

    @classmethod
    def create(cls, program, target_file=None, ingr_file=None, direction=None, method='random'):
        if target_file is None:
            target_file = program.random_file(AbstractTreeEngine)
        if ingr_file is None:
            ingr_file = program.random_file(engine=program.engines[target_file])
        assert program.engines[target_file] == program.engines[ingr_file]
        if direction is None:
            direction = random.choice(['before', 'after'])
        return cls(program.random_target(target_file, method),
                   program.random_target(ingr_file, 'random'),
                   direction)

class StmtDeletion(AbstractEdit):
    def apply(self, program, new_contents, modification_points):
        engine = program.engines[self.target[0]]
        return engine.do_delete(program, self.target, new_contents, modification_points)

    @classmethod
    def create(cls, program, target_file=None, method='random'):
        if target_file is None:
            target_file = program.random_file(AbstractTreeEngine)
        return cls(program.random_target(target_file, method))

class StmtMoving(AbstractEdit):
    def apply(self, program, new_contents, modification_points):
        engine = program.engines[self.target[0]]
        engine.do_insert(program, self.target, self.data[0], self.data[1], new_contents, modification_points)
        return_code = engine.do_delete(program, self.data[0], new_contents, modification_points)
        return return_code

    @classmethod
    def create(cls, program, target_file=None, ingr_file=None, direction=None, method='random'):
        if target_file is None:
            target_file = program.random_file(AbstractTreeEngine)
        if ingr_file is None:
            ingr_file = program.random_file(engine=program.engines[target_file])
        assert program.engines[target_file] == program.engines[ingr_file]
        if direction is None:
            direction = random.choice(['before', 'after'])
        return cls(program.random_target(target_file, method),
                   program.random_target(ingr_file, 'random'),
                   direction)

class ExprReplacement(StmtReplacement):
    pass

class ConditionReplacement(StmtReplacement):
    pass

class TextSetting(AbstractEdit):
    CHOICES = ['']

    def apply(self, program, new_contents, modification_points):
        engine = program.engines[self.target[0]]
        return engine.do_set_text(program, self.target, self.data[0], new_contents, modification_points)

    @classmethod
    def create(cls, program, target_file=None, method='random', choices=None):
        if choices == None:
            choices = cls.CHOICES
        if target_file is None:
            target_file = program.random_file(XmlEngine)
        target = program.random_target(target_file, method)
        value = random.choice(choices)
        return cls(target, value)

class TextWrapping(AbstractEdit):
    CHOICES = [('(', ')')]

    def apply(self, program, new_contents, modification_points):
        engine = program.engines[self.target[0]]
        return engine.do_wrap_text(program, self.target, self.data[0][0], self.data[0][1], new_contents, modification_points)

    @classmethod
    def create(cls, program, target_file=None, method='random', choices=None):
        if choices == None:
            choices = cls.CHOICES
        if target_file is None:
            target_file = program.random_file(XmlEngine)
        target = program.random_target(target_file, method)
        value = random.choice(choices)
        return cls(target, value)

class ComparisonOperatorSetting(TextSetting):
    CHOICES = ['==', '!=', '<', '<=', '>', '>=']

class ArithmeticOperatorSetting(TextSetting):
    CHOICES = ['+', '-', '*', '/', '%']

class NumericSetting(TextSetting):
    CHOICES = ['-1', '0', '1']

class RelativeNumericSetting(TextWrapping):
    CHOICES = [('(', '+1)'), ('(', '-1)'), ('(', '/2)'), ('(', '*2)'), ('(', '*3/2)'), ('(', '*2/3)')]
