import random
from ..base import Edit
from . import AbstractParamsModel

class ParamSetting(Edit):
    def apply(self, program, new_contents, new_locations):
        model = program.models[self.target[0]]
        return model.do_set(program.contents, program.locations,
                            new_contents, new_locations,
                            self.target, self.data[0])

    @classmethod
    def create(cls, program, target_file=None):
        if target_file is None:
            target_file = program.random_file(AbstractParamsModel)
        _, _, param_id = program.random_target(target_file, 'param')
        model = program.models[target_file]
        data = model.random_value(program.contents[target_file], param_id)
        return cls((target_file, param_id), data)
