import random

import magpie

from .abstract_model import AbstractXmlModel


class XmlNodeDeletionTemplatedEdit(magpie.core.TemplatedEdit):
    @classmethod
    def auto_create(cls, ref):
        target = ref.random_model(AbstractXmlModel).random_target(cls.TEMPLATE[0])
        if not target:
            return None
        return cls(target)

    def apply(self, ref, variant):
        model = variant.models[self.target[0]]
        return model.do_delete(self.target)

magpie.utils.known_edits.append(XmlNodeDeletionTemplatedEdit)


class XmlNodeReplacementTemplatedEdit(magpie.core.TemplatedEdit):
    @classmethod
    def auto_create(cls, ref):
        target, ingredient = ref.random_targets(AbstractXmlModel, cls.TEMPLATE[0], cls.TEMPLATE[0])
        if not (target and ingredient):
            return None
        return cls(target, ingredient)

    def apply(self, ref, variant):
        ingredient = self.data[0]
        ref_model = ref.models[ingredient[0]]
        model = variant.models[self.target[0]]
        return model.do_replace(ref_model, self.target, ingredient)

magpie.utils.known_edits.append(XmlNodeReplacementTemplatedEdit)


class XmlNodeInsertionTemplatedEdit(magpie.core.TemplatedEdit):
    @classmethod
    def auto_create(cls, ref):
        target, ingredient = ref.random_targets(AbstractXmlModel, f'_inter_{cls.TEMPLATE[1]}', cls.TEMPLATE[0])
        if not (target and ingredient):
            return None
        return cls(target, ingredient)

    def apply(self, ref, variant):
        ingredient = self.data[0]
        ref_model = ref.models[ingredient[0]]
        model = variant.models[self.target[0]]
        return model.do_insert(ref_model, self.target, ingredient)

magpie.utils.known_edits.append(XmlNodeInsertionTemplatedEdit)


class XmlTextSettingTemplatedEdit(magpie.core.TemplatedEdit):
    @classmethod
    def auto_create(cls, ref):
        target = ref.random_model(AbstractXmlModel).random_target(cls.TEMPLATE[0])
        ingredient = random.choice(cls.TEMPLATE[1:])
        if not target:
            return None
        return cls(target, ingredient)

    def apply(self, ref, variant):
        ingredient = self.data[0]
        model = variant.models[self.target[0]]
        return model.do_set_text(self.target, ingredient)

magpie.utils.known_edits.append(XmlTextSettingTemplatedEdit)


class XmlTextWrappingTemplatedEdit(magpie.core.TemplatedEdit):
    @classmethod
    def auto_create(cls, ref):
        target = ref.random_model(AbstractXmlModel).random_target(cls.TEMPLATE[0])
        i = random.randrange(1, len(cls.TEMPLATE)//2)
        ingredient = (cls.TEMPLATE[2*i-1], cls.TEMPLATE[2*i])
        if not target:
            return None
        return cls(target, ingredient)

    def apply(self, ref, variant):
        ingredient = self.data[0]
        model = variant.models[self.target[0]]
        return model.do_wrap_text(self.target, *ingredient)

magpie.utils.known_edits.append(XmlTextWrappingTemplatedEdit)
