import random

from magpie.core import Edit
from . import XmlModel


class NodeDeletion(Edit):
    NODE_TYPE = ''

    def apply(self, software, new_contents, new_locations):
        model = software.models[self.target[0]]
        return model.do_delete(software.contents, software.locations,
                               new_contents, new_locations,
                               self.target)

    @classmethod
    def create(cls, software, target_file=None):
        if target_file is None:
            target_file = software.random_file(XmlModel)
        target = software.random_target(target_file, cls.NODE_TYPE)
        if target is None:
            return None
        return cls(target)

class NodeReplacement(Edit):
    NODE_TYPE = ''

    def apply(self, software, new_contents, new_locations):
        model = software.models[self.target[0]]
        return model.do_replace(software.contents, software.locations,
                                new_contents, new_locations,
                                self.target, self.data[0])

    @classmethod
    def create(cls, software, target_file=None, ingr_file=None):
        if target_file is None:
            target_file = software.random_file(XmlModel)
        if ingr_file is None:
            ingr_file = software.random_file(model=software.models[target_file].__class__)
        target = software.random_target(target_file, cls.NODE_TYPE)
        if target is None:
            return None
        value = software.random_target(ingr_file, cls.NODE_TYPE)
        if value is None:
            return None
        return cls(target, value)

class NodeInsertion(Edit):
    NODE_PARENT_TYPE = ''
    NODE_TYPE = ''

    def apply(self, software, new_contents, new_locations):
        model = software.models[self.target[0]]
        return model.do_insert(software.contents, software.locations,
                               new_contents, new_locations,
                               self.target, self.data[0])

    @classmethod
    def create(cls, software, target_file=None, ingr_file=None):
        if target_file is None:
            target_file = software.random_file(XmlModel)
        if ingr_file is None:
            ingr_file = software.random_file(model=software.models[target_file].__class__)
        target = software.random_target(target_file, '_inter_{}'.format(cls.NODE_PARENT_TYPE))
        if target is None:
            return None
        value = software.random_target(ingr_file, cls.NODE_TYPE)
        if value is None:
            return None
        return cls(target, value)

class NodeMoving(Edit):
    NODE_PARENT_TYPE = ''
    NODE_TYPE = ''

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
            target_file = software.random_file(XmlModel)
        if ingr_file is None:
            ingr_file = software.random_file(model=software.models[target_file].__class__)
        target = software.random_target(target_file, '_inter_{}'.format(cls.NODE_PARENT_TYPE))
        if target is None:
            return None
        value = software.random_target(ingr_file, cls.NODE_TYPE)
        if value is None:
            return None
        return cls(target, value)

class NodeSwap(Edit):
    NODE_PARENT_TYPE = ''
    NODE_TYPE = ''

    def apply(self, software, new_contents, new_locations):
        model = software.models[self.target[0]]
        return (model.do_replace(software.contents, software.locations,
                                 new_contents, new_locations,
                                 self.target, self.data[0])
                and
                model.do_replace(software.contents, software.locations,
                                 new_contents, new_locations,
                                 self.data[0], self.target))

    @classmethod
    def create(cls, software, target_file=None, ingr_file=None):
        if target_file is None:
            target_file = software.random_file(XmlModel)
        if ingr_file is None:
            ingr_file = software.random_file(model=software.models[target_file].__class__)
        target = software.random_target(target_file, cls.NODE_TYPE)
        if target is None:
            return None
        value = software.random_target(ingr_file, cls.NODE_TYPE)
        if value is None:
            return None
        return cls(target, value)

class TextSetting(Edit):
    NODE_TYPE = ''
    CHOICES = ['']

    def apply(self, software, new_contents, new_locations):
        model = software.models[self.target[0]]
        return model.do_set_text(software.contents, software.locations,
                                 new_contents, new_locations,
                                 self.target, self.data[0])

    @classmethod
    def create(cls, software, target_file=None, choices=None):
        if choices == None:
            choices = cls.CHOICES
        if target_file is None:
            target_file = software.random_file(XmlModel)
        target = software.random_target(target_file, cls.NODE_TYPE)
        if target is None:
            return None
        value = random.choice(choices)
        return cls(target, value)

class TextWrapping(Edit):
    NODE_TYPE = ''
    CHOICES = [('(', ')')]

    def apply(self, software, new_contents, new_locations):
        model = software.models[self.target[0]]
        return model.do_wrap_text(software.contents, software.locations,
                                  new_contents, new_locations,
                                  self.target, self.data[0][0], self.data[0][1])

    @classmethod
    def create(cls, software, target_file=None, choices=None):
        if choices == None:
            choices = cls.CHOICES
        if target_file is None:
            target_file = software.random_file(XmlModel)
        target = software.random_target(target_file, cls.NODE_TYPE)
        if target is None:
            return None
        value = random.choice(choices)
        return cls(target, value)
