import random

from magpie.base import Edit
from . import AbstractLineModel


class LineReplacement(Edit):
    def apply(self, software, new_contents, new_locations):
        model = software.models[self.target[0]]
        return model.do_replace(software.contents, software.locations,
                                new_contents, new_locations,
                                self.target, self.data[0])

    @classmethod
    def create(cls, software, target_file=None, ingr_file=None):
        if target_file is None:
            target_file = software.random_file(AbstractLineModel)
        if ingr_file is None:
            ingr_file = software.random_file(model=software.models[target_file].__class__)
        return cls(software.random_target(target_file, 'line'),
                   software.random_target(ingr_file, 'line'))

class LineInsertion(Edit):
    def apply(self, software, new_contents, new_locations):
        model = software.models[self.target[0]]
        return model.do_insert(software.contents, software.locations,
                               new_contents, new_locations,
                               self.target, self.data[0])

    @classmethod
    def create(cls, software, target_file=None, ingr_file=None):
        if target_file is None:
            target_file = software.random_file(AbstractLineModel)
        if ingr_file is None:
            ingr_file = software.random_file(model=software.models[target_file].__class__)
        return cls(software.random_target(target_file, '_inter_line'),
                   software.random_target(ingr_file, 'line'))

class LineDeletion(Edit):
    def apply(self, software, new_contents, new_locations):
        model = software.models[self.target[0]]
        return model.do_delete(software.contents, software.locations,
                               new_contents, new_locations,
                               self.target)

    @classmethod
    def create(cls, software, target_file=None):
        if target_file is None:
            target_file = software.random_file()
        return cls(software.random_target(target_file, 'line'))

class LineMoving(Edit):
    def apply(self, software, new_contents, new_locations):
        model = software.models[self.target[0]]
        return (model.do_insert(software.contents, software.locations,
                                new_contents, new_locations,
                                self.target, self.data[0])
                and
                model.do_delete(software.contents, software.locations,
                                new_contents, new_locations,
                                self.data[0]))

    @classmethod
    def create(cls, software, target_file=None, ingr_file=None):
        if target_file is None:
            target_file = software.random_file()
        if ingr_file is None:
            ingr_file = software.random_file(model=software.models[target_file].__class__)
        return cls(software.random_target(target_file, '_inter_line'),
                   software.random_target(ingr_file, 'line'))
