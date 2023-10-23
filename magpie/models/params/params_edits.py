import random

from magpie.base import Edit
from . import AbstractParamsModel

class ParamSetting(Edit):
    def apply(self, software, new_contents, new_locations):
        model = software.models[self.target[0]]
        return model.do_set(software.contents, software.locations,
                            new_contents, new_locations,
                            self.target, self.data[0])

    @classmethod
    def create(cls, software, target_file=None):
        if target_file is None:
            target_file = software.random_file(AbstractParamsModel)
        _, _, param_id = software.random_target(target_file, 'param')
        model = software.models[target_file]
        data = model.random_value(software.contents[target_file], param_id)
        return cls((target_file, param_id), data)
