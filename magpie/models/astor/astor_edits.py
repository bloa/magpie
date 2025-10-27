from magpie.core import AbstractEdit
import magpie.utils

from .astor_model import AstorModel


class AstorStmtReplacementEdit(AbstractEdit):
    @classmethod
    def auto_create(cls, ref):
        target = ref.random_model(AstorModel, writable=True).random_target('stmt')
        ingredient = ref.random_model(AstorModel, writable=False).random_target('stmt')
        if not (target and ingredient):
            return None
        return cls(target, ingredient)

    def apply(self, ref, variant):
        ingredient = self.data[0]
        ref_model = ref.models[ingredient[0]]
        model = variant.models[self.target[0]]
        return model.do_replace(ref_model, self.target, ingredient)

magpie.utils.known_edits.append(AstorStmtReplacementEdit)


class AstorStmtInsertionEdit(AbstractEdit):
    @classmethod
    def auto_create(cls, ref):
        target = ref.random_model(AstorModel, writable=True).random_target('_inter_block')
        ingredient = ref.random_model(AstorModel, writable=False).random_target('stmt')
        if not (target and ingredient):
            return None
        return cls(target, ingredient)

    def apply(self, ref, variant):
        ingredient = self.data[0]
        ref_model = ref.models[ingredient[0]]
        model = variant.models[self.target[0]]
        return model.do_insert(ref_model, self.target, ingredient)

magpie.utils.known_edits.append(AstorStmtInsertionEdit)


class AstorStmtDeletionEdit(AbstractEdit):
    @classmethod
    def auto_create(cls, ref):
        target = ref.random_model(AstorModel, writable=True).random_target('stmt')
        if not target:
            return None
        return cls(target)

    def apply(self, ref, variant):
        model = variant.models[self.target[0]]
        return model.do_delete(self.target)

magpie.utils.known_edits.append(AstorStmtDeletionEdit)


class AstorStmtMoveReplacementEdit(AbstractEdit):
    @classmethod
    def auto_create(cls, ref):
        target = ref.random_model(AstorModel, writable=True).random_target('stmt')
        ingredient = ref.random_model(AstorModel, writable=False).random_target('stmt')
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

magpie.utils.known_edits.append(AstorStmtMoveReplacementEdit)


class AstorStmtMoveInsertionEdit(AbstractEdit):
    @classmethod
    def auto_create(cls, ref):
        target = ref.random_model(AstorModel, writable=True).random_target('stmt')
        ingredient = ref.random_model(AstorModel, writable=False).random_target('stmt')
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

magpie.utils.known_edits.append(AstorStmtMoveInsertionEdit)


class AstorStmtSwapEdit(AbstractEdit):
    @classmethod
    def auto_create(cls, ref):
        target = ref.random_model(AstorModel, writable=True).random_target('stmt')
        ingredient = ref.random_model(AstorModel, writable=True).random_target('stmt')
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

magpie.utils.known_edits.append(AstorStmtSwapEdit)
