import random

from ..base import Edit
from . import AstorModel


class StmtReplacement(Edit):
    def apply(self, program, new_contents, new_locations):
        model = program.models[self.target[0]]
        return model.do_replace(program.contents, program.locations,
                                new_contents, new_locations,
                                self.target, self.data[0])

    @classmethod
    def create(cls, program, target_file=None, ingr_file=None):
        if target_file is None:
            target_file = program.random_file(AstorModel)
        if ingr_file is None:
            ingr_file = program.random_file(model=program.models[target_file])
        assert program.models[target_file] == program.models[ingr_file]
        return cls(program.random_target(target_file, 'stmt'),
                   program.random_target(ingr_file, 'stmt'))

class StmtInsertion(Edit):
    def apply(self, program, new_contents, new_locations):
        model = program.models[self.target[0]]
        return model.do_insert(program.contents, program.locations,
                               new_contents, new_locations,
                               self.target, self.data[0])

    @classmethod
    def create(cls, program, target_file=None, ingr_file=None):
        if target_file is None:
            target_file = program.random_file(AstorModel)
        if ingr_file is None:
            ingr_file = program.random_file(model=program.models[target_file])
        assert program.models[target_file] == program.models[ingr_file]
        return cls(program.random_target(target_file, '_inter_block'),
                   program.random_target(ingr_file, 'stmt'))

class StmtDeletion(Edit):
    def apply(self, program, new_contents, new_locations):
        model = program.models[self.target[0]]
        return model.do_delete(program.contents, program.locations,
                               new_contents, new_locations,
                               self.target)

    @classmethod
    def create(cls, program, target_file=None):
        if target_file is None:
            target_file = program.random_file(AstorModel)
        return cls(program.random_target(target_file, 'stmt'))

class StmtMoving(Edit):
    def apply(self, program, new_contents, new_locations):
        model = program.models[self.target[0]]
        model.do_insert(program.contents, program.locations,
                        new_contents, new_locations,
                        self.target, self.data[0])
        return model.do_delete(program.contents, program.locations,
                               new_contents, new_locations,
                               self.target)

    @classmethod
    def create(cls, program, target_file=None, ingr_file=None, direction=None):
        if target_file is None:
            target_file = program.random_file(AstorModel)
        if ingr_file is None:
            ingr_file = program.random_file(model=program.models[target_file])
        assert program.models[target_file] == program.models[ingr_file]
        if direction is None:
            direction = random.choice(['before', 'after'])
        return cls(program.random_target(target_file, 'stmt'),
                   program.random_target(ingr_file, 'stmt'),
                   direction)
