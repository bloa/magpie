import random

from ..base import Edit
from . import AstorEngine


class StmtReplacement(Edit):
    def apply(self, program, new_contents, new_locations):
        engine = program.engines[self.target[0]]
        return engine.do_replace(program.contents, program.locations,
                                 new_contents, new_locations,
                                 self.target, self.data[0])

    @classmethod
    def create(cls, program, target_file=None, ingr_file=None):
        if target_file is None:
            target_file = program.random_file(AstorEngine)
        if ingr_file is None:
            ingr_file = program.random_file(engine=program.engines[target_file])
        assert program.engines[target_file] == program.engines[ingr_file]
        return cls(program.random_target(target_file, 'stmt'),
                   program.random_target(ingr_file, 'stmt'))

class StmtInsertion(Edit):
    def apply(self, program, new_contents, new_locations):
        engine = program.engines[self.target[0]]
        return engine.do_insert(program.contents, program.locations,
                                new_contents, new_locations,
                                self.target, self.data[0])

    @classmethod
    def create(cls, program, target_file=None, ingr_file=None):
        if target_file is None:
            target_file = program.random_file(AstorEngine)
        if ingr_file is None:
            ingr_file = program.random_file(engine=program.engines[target_file])
        assert program.engines[target_file] == program.engines[ingr_file]
        return cls(program.random_target(target_file, '_inter_block'),
                   program.random_target(ingr_file, 'stmt'))

class StmtDeletion(Edit):
    def apply(self, program, new_contents, new_locations):
        engine = program.engines[self.target[0]]
        return engine.do_delete(program.contents, program.locations,
                                new_contents, new_locations,
                                self.target)

    @classmethod
    def create(cls, program, target_file=None):
        if target_file is None:
            target_file = program.random_file(AstorEngine)
        return cls(program.random_target(target_file, 'stmt'))

class StmtMoving(Edit):
    def apply(self, program, new_contents, new_locations):
        engine = program.engines[self.target[0]]
        engine.do_insert(program.contents, program.locations,
                         new_contents, new_locations,
                         self.target, self.data[0])
        return engine.do_delete(program.contents, program.locations,
                                new_contents, new_locations,
                                self.target)

    @classmethod
    def create(cls, program, target_file=None, ingr_file=None, direction=None):
        if target_file is None:
            target_file = program.random_file(AstorEngine)
        if ingr_file is None:
            ingr_file = program.random_file(engine=program.engines[target_file])
        assert program.engines[target_file] == program.engines[ingr_file]
        if direction is None:
            direction = random.choice(['before', 'after'])
        return cls(program.random_target(target_file, 'stmt'),
                   program.random_target(ingr_file, 'stmt'),
                   direction)
