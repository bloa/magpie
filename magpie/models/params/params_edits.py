import magpie.core
import magpie.utils

from .abstract_model import AbstractParamsModel


class ParamSetting(magpie.core.Edit):
    @classmethod
    def auto_create(cls, ref):
        model = ref.random_model(AbstractParamsModel)
        target = model.random_target('param')
        if not target:
            return None
        value = model.random_value(target[2])
        return cls(target, value)

    def apply(self, ref, variant):
        model = variant.models[self.target[0]]
        return model.do_set(self.target, self.data[0])

magpie.utils.known_edits += [ParamSetting]
