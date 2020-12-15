import random
from ..base import AbstractEdit
from . import AbstractTreeEngine, XmlEngine


class NodeDeletion(AbstractEdit):
    NODE_TYPE = ''

    def apply(self, program, new_contents, new_locations):
        engine = program.engines[self.target[0]]
        return engine.do_delete(program.contents, program.locations,
                                new_contents, new_locations,
                                self.target)

    @classmethod
    def create(cls, program, target_file=None):
        if target_file is None:
            target_file = program.random_file(AbstractTreeEngine)
        return cls(program.random_target(target_file, cls.NODE_TYPE))

class NodeReplacement(AbstractEdit):
    NODE_TYPE = ''

    def apply(self, program, new_contents, new_locations):
        engine = program.engines[self.target[0]]
        return engine.do_replace(program.contents, program.locations,
                                 new_contents, new_locations,
                                 self.target, self.data[0])

    @classmethod
    def create(cls, program, target_file=None, ingr_file=None):
        if target_file is None:
            target_file = program.random_file(AbstractTreeEngine)
        if ingr_file is None:
            ingr_file = program.random_file(engine=program.engines[target_file])
        return cls(program.random_target(target_file, cls.NODE_TYPE),
                   program.random_target(ingr_file, cls.NODE_TYPE))

class NodeInsertion(AbstractEdit):
    NODE_PARENT_TYPE = ''
    NODE_TYPE = ''

    def apply(self, program, new_contents, new_locations):
        engine = program.engines[self.target[0]]
        return engine.do_insert(program.contents, program.locations,
                                new_contents, new_locations,
                                self.target, self.data[0])

    @classmethod
    def create(cls, program, target_file=None, ingr_file=None):
        if target_file is None:
            target_file = program.random_file(AbstractTreeEngine)
        if ingr_file is None:
            ingr_file = program.random_file(engine=program.engines[target_file])
        return cls(program.random_target(target_file, '_inter_{}'.format(cls.NODE_PARENT_TYPE)),
                   program.random_target(ingr_file, cls.NODE_TYPE))

class NodeMoving(AbstractEdit):
    NODE_PARENT_TYPE = ''
    NODE_TYPE = ''

    def apply(self, program, new_contents, new_locations):
        engine = program.engines[self.target[0]]
        return_code = engine.do_insert(program.contents, program.locations,
                                       new_contents, new_locations,
                                       self.target, self.data[0])
        if return_code:
            return_code = engine.do_delete(program, self.data[0], new_contents, new_locations)
        return return_code

    @classmethod
    def create(cls, program, target_file=None, ingr_file=None):
        if target_file is None:
            target_file = program.random_file(AbstractTreeEngine)
        if ingr_file is None:
            ingr_file = program.random_file(engine=program.engines[target_file])
        return cls(program.random_target(target_file, '_inter_{}'.format(cls.NODE_PARENT_TYPE)),
                   program.random_target(ingr_file, cls.NODE_TYPE))

class TextSetting(AbstractEdit):
    NODE_TYPE = ''
    CHOICES = ['']

    def apply(self, program, new_contents, new_locations):
        engine = program.engines[self.target[0]]
        return engine.do_set_text(program.contents, program.locations,
                                  new_contents, new_locations,
                                  self.target, self.data[0])

    @classmethod
    def create(cls, program, target_file=None, choices=None):
        if choices == None:
            choices = cls.CHOICES
        if target_file is None:
            target_file = program.random_file(XmlEngine)
        target = program.random_target(target_file, cls.NODE_TYPE)
        value = random.choice(choices)
        return cls(target, value)

class TextWrapping(AbstractEdit):
    NODE_TYPE = ''
    CHOICES = [('(', ')')]

    def apply(self, program, new_contents, new_locations):
        engine = program.engines[self.target[0]]
        return engine.do_wrap_text(program.contents, program.locations,
                                   new_contents, new_locations,
                                   self.target, self.data[0][0], self.data[0][1])

    @classmethod
    def create(cls, program, target_file=None, choices=None):
        if choices == None:
            choices = cls.CHOICES
        if target_file is None:
            target_file = program.random_file(XmlEngine)
        target = program.random_target(target_file, cls.NODE_TYPE)
        value = random.choice(choices)
        return cls(target, value)


class StmtDeletion(NodeDeletion):
    NODE_TYPE = 'stmt'

class StmtReplacement(NodeReplacement):
    NODE_TYPE = 'stmt'

class StmtInsertion(NodeInsertion):
    NODE_PARENT_TYPE = 'block'
    NODE_TYPE = 'stmt'

class StmtMoving(NodeMoving):
    NODE_PARENT_TYPE = 'block'
    NODE_TYPE = 'stmt'

class ConditionReplacement(NodeReplacement):
    NODE_TYPE = 'condition'

class ExprReplacement(NodeReplacement):
    NODE_TYPE = 'expr'

class ComparisonOperatorSetting(TextSetting):
    NODE_TYPE = 'operator_comp'
    CHOICES = ['==', '!=', '<', '<=', '>', '>=']

class ArithmeticOperatorSetting(TextSetting):
    NODE_TYPE = 'operator_arith'
    CHOICES = ['+', '-', '*', '/', '%']

class NumericSetting(TextSetting):
    NODE_TYPE = 'number'
    CHOICES = ['-1', '0', '1']

class RelativeNumericSetting(TextWrapping):
    NODE_TYPE = 'number'
    CHOICES = [('(', '+1)'), ('(', '-1)'), ('(', '/2)'), ('(', '*2)'), ('(', '*3/2)'), ('(', '*2/3)')]
