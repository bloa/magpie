from magpie.core import Edit
from . import AbstractLineModel


class LineDeletion(Edit):
    @classmethod
    def auto_create(cls, ref):
        target = ref.random_model(AbstractLineModel).random_target('line')
        if not target:
            return None
        return cls(target)

    def apply(self, ref, variant):
        model = variant.models[self.target[0]]
        return model.do_delete(self.target)


class LineReplacement(Edit):
    @classmethod
    def auto_create(cls, ref):
        target, ingredient = ref.random_targets(AbstractLineModel, 'line', 'line')
        if not (target and ingredient):
            return None
        return cls(target, ingredient)

    def apply(self, ref, variant):
        ingredient = self.data[0]
        ref_model = ref.models[ingredient[0]]
        model = variant.models[self.target[0]]
        return model.do_replace(ref_model, self.target, ingredient)


class LineInsertion(Edit):
    @classmethod
    def auto_create(cls, ref):
        target, ingredient = ref.random_targets(AbstractLineModel, '_inter_line', 'line')
        if not (target and ingredient):
            return None
        return cls(target, ingredient)

    def apply(self, ref, variant):
        ingredient = self.data[0]
        ref_model = ref.models[ingredient[0]]
        model = variant.models[self.target[0]]
        return model.do_insert(ref_model, self.target, ingredient)
