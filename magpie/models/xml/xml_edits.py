import random

from magpie.core import TemplatedEdit
import magpie.utils

from .abstract_model import AbstractXmlModel


class XmlNodeDeletionTemplatedEdit(TemplatedEdit):
    @classmethod
    def auto_create(cls, ref):
        target = ref.random_model(AbstractXmlModel, writable=True).random_target(cls.TEMPLATE[0])
        if not target:
            return None
        return cls(target)

    def apply(self, ref, variant):
        model = variant.models[self.target[0]]
        return model.do_delete(self.target)

magpie.utils.known_edits.append(XmlNodeDeletionTemplatedEdit)


class XmlNodeReplacementTemplatedEdit(TemplatedEdit):
    @classmethod
    def auto_create(cls, ref):
        target = ref.random_model(AbstractXmlModel, writable=True).random_target(cls.TEMPLATE[0])
        ingredient = ref.random_model(AbstractXmlModel, writable=False).random_target(cls.TEMPLATE[0])
        if not (target and ingredient):
            return None
        return cls(target, ingredient)

    def apply(self, ref, variant):
        ingredient = self.data[0]
        ref_model = ref.models[ingredient[0]]
        model = variant.models[self.target[0]]
        return model.do_replace(ref_model, self.target, ingredient)

magpie.utils.known_edits.append(XmlNodeReplacementTemplatedEdit)


class XmlNodeInsertionTemplatedEdit(TemplatedEdit):
    @classmethod
    def auto_create(cls, ref):
        target = ref.random_model(AbstractXmlModel, writable=True).random_target(f'_inter_{cls.TEMPLATE[1]}')
        ingredient = ref.random_model(AbstractXmlModel, writable=False).random_target(cls.TEMPLATE[0])
        if not (target and ingredient):
            return None
        return cls(target, ingredient)

    def apply(self, ref, variant):
        ingredient = self.data[0]
        ref_model = ref.models[ingredient[0]]
        model = variant.models[self.target[0]]
        return model.do_insert(ref_model, self.target, ingredient)

magpie.utils.known_edits.append(XmlNodeInsertionTemplatedEdit)


class XmlNodeMoveReplacementTemplatedEdit(TemplatedEdit):
    @classmethod
    def auto_create(cls, ref):
        target = ref.random_model(AbstractXmlModel, writable=True).random_target(cls.TEMPLATE[0])
        ingredient = ref.random_model(AbstractXmlModel, writable=False).random_target(cls.TEMPLATE[0])
        if not (target and ingredient):
            return None
        return cls(target, ingredient)

    def apply(self, ref, variant):
        ingredient = self.data[0]
        ref_model = ref.models[ingredient[0]]
        model = variant.models[self.target[0]]
        b1 = model.do_replace(ref_model, self.target, ingredient)
        b2 = model.do_delete(ingredient)
        return b1 or b2

magpie.utils.known_edits.append(XmlNodeMoveReplacementTemplatedEdit)


class XmlNodeMoveInsertionTemplatedEdit(TemplatedEdit):
    @classmethod
    def auto_create(cls, ref):
        target = ref.random_model(AbstractXmlModel, writable=True).random_target(f'_inter_{cls.TEMPLATE[1]}')
        ingredient = ref.random_model(AbstractXmlModel, writable=False).random_target(cls.TEMPLATE[0])
        if not (target and ingredient):
            return None
        return cls(target, ingredient)

    def apply(self, ref, variant):
        ingredient = self.data[0]
        ref_model = ref.models[ingredient[0]]
        model = variant.models[self.target[0]]
        b1 = model.do_insert(ref_model, self.target, ingredient)
        b2 = model.do_delete(ingredient)
        return b1 or b2

magpie.utils.known_edits.append(XmlNodeMoveInsertionTemplatedEdit)


class XmlNodeSwapTemplatedEdit(TemplatedEdit):
    @classmethod
    def auto_create(cls, ref):
        target = ref.random_model(AbstractXmlModel, writable=True).random_target(cls.TEMPLATE[0])
        ingredient = ref.random_model(AbstractXmlModel, writable=False).random_target(cls.TEMPLATE[0])
        if not (target and ingredient):
            return None
        return cls(target, ingredient)

    def apply(self, ref, variant):
        ingredient = self.data[0]
        ref_model = ref.models[ingredient[0]]
        model = variant.models[self.target[0]]
        b1 = model.do_replace(ref_model, self.target, ingredient)
        b2 = model.do_replace(ref_model, ingredient, self.target)
        return b1 or b2


class XmlTextSettingTemplatedEdit(TemplatedEdit):
    @classmethod
    def auto_create(cls, ref):
        target = ref.random_model(AbstractXmlModel, writable=True).random_target(cls.TEMPLATE[0])
        ingredient = random.choice(cls.TEMPLATE[1:])
        if not target:
            return None
        return cls(target, ingredient)

    def apply(self, ref, variant):
        ingredient = self.data[0]
        model = variant.models[self.target[0]]
        return model.do_set_text(self.target, ingredient)

magpie.utils.known_edits.append(XmlTextSettingTemplatedEdit)


class XmlTextSwapTemplatedEdit(TemplatedEdit):
    @classmethod
    def auto_create(cls, ref):
        target = ref.random_model(AbstractXmlModel, writable=True).random_target(cls.TEMPLATE[0])
        ingredient = ref.random_model(AbstractXmlModel, writable=True).random_target(cls.TEMPLATE[0])
        if not target:
            return None
        return cls(target, ingredient)

    def apply(self, ref, variant):
        ingredient = self.data[0]
        model = variant.models[self.target[0]]
        text_target = model.do_get_text(self.target)
        text_ingredient = model.do_get_text(ingredient)
        b1 = model.do_set_text(self.target, text_ingredient)
        b2 = model.do_set_text(ingredient, text_target)
        return b1 or b2

magpie.utils.known_edits.append(XmlTextSwapTemplatedEdit)


class XmlTextWrappingTemplatedEdit(TemplatedEdit):
    @classmethod
    def auto_create(cls, ref):
        target = ref.random_model(AbstractXmlModel, writable=True).random_target(cls.TEMPLATE[0])
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
