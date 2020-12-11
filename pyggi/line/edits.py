import random
from ..base import AbstractEdit
from . import AbstractLineEngine


class LineReplacement(AbstractEdit):
    def apply(self, program, new_contents, modification_points):
        engine = program.engines[self.target[0]]
        return engine.do_replace(program, self.target, self.data[0], new_contents, modification_points)

    @classmethod
    def create(cls, program, target_file=None, ingr_file=None, method='random'):
        if target_file is None:
            target_file = program.random_file(AbstractLineEngine)
        if ingr_file is None:
            ingr_file = program.random_file(engine=program.engines[target_file])
        assert program.engines[target_file] == program.engines[ingr_file]
        return cls(program.random_target(target_file, method),
                   program.random_target(ingr_file, 'random'))

class LineInsertion(AbstractEdit):
    def apply(self, program, new_contents, modification_points):
        engine = program.engines[self.target[0]]
        return engine.do_insert(program, self.target, self.data[0], self.data[1], new_contents, modification_points)

    @classmethod
    def create(cls, program, target_file=None, ingr_file=None, direction=None, method='random'):
        if target_file is None:
            target_file = program.random_file()
        if ingr_file is None:
            ingr_file = program.random_file(engine=program.engines[target_file])
        assert program.engines[target_file] == program.engines[ingr_file]
        if direction is None:
            direction = random.choice(['before', 'after'])
        return cls(program.random_target(target_file, method),
                   program.random_target(ingr_file, 'random'),
                   direction)

class LineDeletion(AbstractEdit):
    def apply(self, program, new_contents, modification_points):
        engine = program.engines[self.target[0]]
        return engine.do_delete(program, self.target, new_contents, modification_points)

    @classmethod
    def create(cls, program, target_file=None, method='random'):
        if target_file is None:
            target_file = program.random_file()
        return cls(program.random_target(target_file, method))

class LineMoving(AbstractEdit):
    def apply(self, program, new_contents, modification_points):
        engine = program.engines[self.target[0]]
        engine.do_insert(program, self.target, self.data[0], self.data[1], new_contents, modification_points)
        return_code = engine.do_delete(program, self.data[0], new_contents, modification_points)
        return return_code

    @classmethod
    def create(cls, program, target_file=None, ingr_file=None, direction='before', method='random'):
        if target_file is None:
            target_file = program.random_file()
        if ingr_file is None:
            ingr_file = program.random_file(engine=program.engines[target_file])
        assert program.engines[target_file] == program.engines[ingr_file]
        if direction is None:
            direction = random.choice(['before', 'after'])
        return cls(program.random_target(target_file, method),
                   program.random_target(ingr_file, 'random'),
                   direction)
