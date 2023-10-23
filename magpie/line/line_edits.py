import random

from ..base import Edit
from . import AbstractLineModel


class LineReplacement(Edit):
    def apply(self, program, new_contents, new_locations):
        model = program.models[self.target[0]]
        return model.do_replace(program.contents, program.locations,
                                new_contents, new_locations,
                                self.target, self.data[0])

    @classmethod
    def create(cls, program, target_file=None, ingr_file=None):
        if target_file is None:
            target_file = program.random_file(AbstractLineModel)
        if ingr_file is None:
            ingr_file = program.random_file(model=program.models[target_file].__class__)
        return cls(program.random_target(target_file, 'line'),
                   program.random_target(ingr_file, 'line'))

class LineInsertion(Edit):
    def apply(self, program, new_contents, new_locations):
        model = program.models[self.target[0]]
        return model.do_insert(program.contents, program.locations,
                               new_contents, new_locations,
                               self.target, self.data[0])

    @classmethod
    def create(cls, program, target_file=None, ingr_file=None):
        if target_file is None:
            target_file = program.random_file(AbstractLineModel)
        if ingr_file is None:
            ingr_file = program.random_file(model=program.models[target_file].__class__)
        return cls(program.random_target(target_file, '_inter_line'),
                   program.random_target(ingr_file, 'line'))

class LineDeletion(Edit):
    def apply(self, program, new_contents, new_locations):
        model = program.models[self.target[0]]
        return model.do_delete(program.contents, program.locations,
                               new_contents, new_locations,
                               self.target)

    @classmethod
    def create(cls, program, target_file=None):
        if target_file is None:
            target_file = program.random_file()
        return cls(program.random_target(target_file, 'line'))

class LineMoving(Edit):
    def apply(self, program, new_contents, new_locations):
        model = program.models[self.target[0]]
        return (model.do_insert(program.contents, program.locations,
                                new_contents, new_locations,
                                self.target, self.data[0])
                and
                model.do_delete(program.contents, program.locations,
                                new_contents, new_locations,
                                self.data[0]))

    @classmethod
    def create(cls, program, target_file=None, ingr_file=None):
        if target_file is None:
            target_file = program.random_file()
        if ingr_file is None:
            ingr_file = program.random_file(model=program.models[target_file].__class__)
        return cls(program.random_target(target_file, '_inter_line'),
                   program.random_target(ingr_file, 'line'))
