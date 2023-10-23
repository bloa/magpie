import random

from magpie.base import Edit
from . import AstorModel


class StmtReplacement(Edit):
    def apply(self, software, new_contents, new_locations):
        model = software.models[self.target[0]]
        return model.do_replace(software.contents, software.locations,
                                new_contents, new_locations,
                                self.target, self.data[0])

    @classmethod
    def create(cls, software, target_file=None, ingr_file=None):
        if target_file is None:
            target_file = software.random_file(AstorModel)
        if ingr_file is None:
            ingr_file = software.random_file(model=software.models[target_file])
        assert software.models[target_file] == software.models[ingr_file]
        return cls(software.random_target(target_file, 'stmt'),
                   software.random_target(ingr_file, 'stmt'))

class StmtInsertion(Edit):
    def apply(self, software, new_contents, new_locations):
        model = software.models[self.target[0]]
        return model.do_insert(software.contents, software.locations,
                               new_contents, new_locations,
                               self.target, self.data[0])

    @classmethod
    def create(cls, software, target_file=None, ingr_file=None):
        if target_file is None:
            target_file = software.random_file(AstorModel)
        if ingr_file is None:
            ingr_file = software.random_file(model=software.models[target_file])
        assert software.models[target_file] == software.models[ingr_file]
        return cls(software.random_target(target_file, '_inter_block'),
                   software.random_target(ingr_file, 'stmt'))

class StmtDeletion(Edit):
    def apply(self, software, new_contents, new_locations):
        model = software.models[self.target[0]]
        return model.do_delete(software.contents, software.locations,
                               new_contents, new_locations,
                               self.target)

    @classmethod
    def create(cls, software, target_file=None):
        if target_file is None:
            target_file = software.random_file(AstorModel)
        return cls(software.random_target(target_file, 'stmt'))

class StmtMoving(Edit):
    def apply(self, software, new_contents, new_locations):
        model = software.models[self.target[0]]
        model.do_insert(software.contents, software.locations,
                        new_contents, new_locations,
                        self.target, self.data[0])
        return model.do_delete(software.contents, software.locations,
                               new_contents, new_locations,
                               self.target)

    @classmethod
    def create(cls, software, target_file=None, ingr_file=None, direction=None):
        if target_file is None:
            target_file = software.random_file(AstorModel)
        if ingr_file is None:
            ingr_file = software.random_file(model=software.models[target_file])
        assert software.models[target_file] == software.models[ingr_file]
        if direction is None:
            direction = random.choice(['before', 'after'])
        return cls(software.random_target(target_file, 'stmt'),
                   software.random_target(ingr_file, 'stmt'),
                   direction)
