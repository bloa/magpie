from magpie.core import AbstractEdit
import magpie.utils

from .abstract_model import AbstractLineModel


class LineDeletionEdit(AbstractEdit):
    @classmethod
    def auto_create(cls, ref):
        target = ref.random_model(AbstractLineModel, writable=True).random_target('line')
        if not target:
            return None
        return cls(target)

    def apply(self, ref, variant):
        model = variant.models[self.target[0]]
        return model.do_delete(self.target)

magpie.utils.known_edits.append(LineDeletionEdit)


class LineReplacementEdit(AbstractEdit):
    @classmethod
    def auto_create(cls, ref):
        target = ref.random_model(AbstractLineModel, writable=True).random_target('line')
        ingredient = ref.random_model(AbstractLineModel, writable=False).random_target('line')
        if not (target and ingredient):
            return None
        return cls(target, ingredient)

    def apply(self, ref, variant):
        ingredient = self.data[0]
        ref_model = ref.models[ingredient[0]]
        model = variant.models[self.target[0]]
        return model.do_replace(ref_model, self.target, ingredient)

magpie.utils.known_edits.append(LineReplacementEdit)


class LineInsertionEdit(AbstractEdit):
    @classmethod
    def auto_create(cls, ref):
        target = ref.random_model(AbstractLineModel, writable=True).random_target('_inter_line')
        ingredient = ref.random_model(AbstractLineModel, writable=False).random_target('line')
        if not (target and ingredient):
            return None
        return cls(target, ingredient)

    def apply(self, ref, variant):
        ingredient = self.data[0]
        ref_model = ref.models[ingredient[0]]
        model = variant.models[self.target[0]]
        return model.do_insert(ref_model, self.target, ingredient)

magpie.utils.known_edits.append(LineInsertionEdit)


class LineMoveReplacementEdit(AbstractEdit):
    @classmethod
    def auto_create(cls, ref):
        target = ref.random_model(AbstractLineModel, writable=True).random_target('line')
        ingredient = ref.random_model(AbstractLineModel, writable=False).random_target('line')
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

magpie.utils.known_edits.append(LineMoveReplacementEdit)


class LineMoveInsertionEdit(AbstractEdit):
    @classmethod
    def auto_create(cls, ref):
        target = ref.random_model(AbstractLineModel, writable=True).random_target('_inter_line')
        ingredient = ref.random_model(AbstractLineModel, writable=False).random_target('line')
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

magpie.utils.known_edits.append(LineMoveInsertionEdit)


class LineSwapEdit(AbstractEdit):
    @classmethod
    def auto_create(cls, ref):
        target = ref.random_model(AbstractLineModel, writable=True).random_target('line')
        ingredient = ref.random_model(AbstractLineModel, writable=True).random_target('line')
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

magpie.utils.known_edits.append(LineSwapEdit)
