import magpie.core
import magpie.utils

from .astor_model import AstorModel


class AstorStmtReplacementEdit(magpie.core.AbstractEdit):
    @classmethod
    def auto_create(cls, ref):
        target, ingredient = ref.random_targets(AstorModel, 'stmt', 'stmt')
        if not (target and ingredient):
            return None
        return cls(target, ingredient)

    def apply(self, ref, variant):
        ingredient = self.data[0]
        ref_model = ref.models[ingredient[0]]
        model = variant.models[self.target[0]]
        return model.do_replace(ref_model, self.target, ingredient)

magpie.utils.known_edits.append(AstorStmtReplacementEdit)


class AstorStmtInsertionEdit(magpie.core.AbstractEdit):
    @classmethod
    def auto_create(cls, ref):
        target, ingredient = ref.random_targets(AstorModel, '_inter_block', 'stmt')
        if not (target and ingredient):
            return None
        return cls(target, ingredient)

    def apply(self, ref, variant):
        ingredient = self.data[0]
        ref_model = ref.models[ingredient[0]]
        model = variant.models[self.target[0]]
        return model.do_insert(ref_model, self.target, ingredient)

magpie.utils.known_edits.append(AstorStmtInsertionEdit)


class AstorStmtDeletionEdit(magpie.core.AbstractEdit):
    @classmethod
    def auto_create(cls, ref):
        target = ref.random_model(AstorModel).random_target('stmt')
        if not target:
            return None
        return cls(target)

    def apply(self, ref, variant):
        model = variant.models[self.target[0]]
        return model.do_delete(self.target)

magpie.utils.known_edits.append(AstorStmtDeletionEdit)


class AstorStmtMovingEdit(magpie.core.AbstractEdit):
    @classmethod
    def auto_create(cls, ref):
        target, ingredient = ref.random_targets(AstorModel, 'stmt', 'stmt')
        if not (target and ingredient):
            return None
        return cls(target, ingredient)

    def apply(self, ref, variant):
        ingredient = self.data[0]
        ref_model = ref.models[ingredient[0]]
        model = variant.models[self.target[0]]
        model.do_insert(ref_model, self.target, ingredient)
        return model.do_delete(ref_model, self.target)

magpie.utils.known_edits.append(AstorStmtMovingEdit)
