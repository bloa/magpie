import random

from magpie.core import Edit
from .abstract_model import AbstractXmlModel


class AbstractXmlNodeDeletion(Edit):
    NODE_TAG = ''

    @classmethod
    def auto_create(cls, ref):
        target = ref.random_model(AbstractXmlModel).random_target(cls.NODE_TAG)
        if not target:
            return None
        return cls(target)

    def apply(self, ref, variant):
        model = variant.models[self.target[0]]
        return model.do_delete(self.target)


class AbstractXmlNodeReplacement(Edit):
    NODE_TAG = ''

    @classmethod
    def auto_create(cls, ref):
        target, ingredient = ref.random_targets(AbstractXmlModel, cls.NODE_TAG, cls.NODE_TAG)
        if not (target and ingredient):
            return None
        return cls(target, ingredient)

    def apply(self, ref, variant):
        ingredient = self.data[0]
        ref_model = ref.models[ingredient[0]]
        model = variant.models[self.target[0]]
        return model.do_replace(ref_model, self.target, ingredient)


class AbstractXmlNodeInsertion(Edit):
    NODE_PARENT_TAG = ''
    NODE_TAG = ''

    @classmethod
    def auto_create(cls, ref):
        target, ingredient = ref.random_targets(AbstractXmlModel, f'_inter_{cls.NODE_PARENT_TAG}', cls.NODE_TAG)
        if not (target and ingredient):
            return None
        return cls(target, ingredient)

    def apply(self, ref, variant):
        ingredient = self.data[0]
        ref_model = ref.models[ingredient[0]]
        model = variant.models[self.target[0]]
        return model.do_insert(ref_model, self.target, ingredient)


class AbstractXmlTextSetting(Edit):
    NODE_TAG = ''
    CHOICES = ['']

    @classmethod
    def auto_create(cls, ref):
        target = ref.random_model(AbstractXmlModel).random_target(cls.NODE_TAG)
        ingredient = random.choice(cls.CHOICES)
        if not target:
            return None
        return cls(target, ingredient)

    def apply(self, ref, variant):
        ingredient = self.data[0]
        model = variant.models[self.target[0]]
        return model.do_set_text(self.target, ingredient)


class AbstractXmlTextWrapping(Edit):
    NODE_TAG = ''
    CHOICES = [('(', ')')]

    @classmethod
    def auto_create(cls, ref):
        target = ref.random_model(AbstractXmlModel).random_target(cls.NODE_TAG)
        ingredient = random.choice(cls.CHOICES)
        if not target:
            return None
        return cls(target, ingredient)

    def apply(self, ref, variant):
        ingredient = self.data[0]
        model = variant.models[self.target[0]]
        return model.do_wrap_text(self.target, *ingredient)
