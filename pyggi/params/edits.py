import random
from ..base import AbstractEdit
from . import AbstractParamsEngine

class ParamSetting(AbstractEdit):
    def apply(self, program, new_contents, new_locations):
        engine = program.engines[self.target[0]]
        return engine.do_set(program.contents, program.locations,
                             new_contents, new_locations,
                             self.target, self.data[0])

    @classmethod
    def create(cls, program, target_file=None):
        if target_file is None:
            target_file = program.random_file(AbstractParamsEngine)
        _, _, param_id = program.random_target(target_file, 'param')
        engine = program.engines[target_file]
        data = engine.random_value(param_id)
        return cls((target_file, param_id), data)
