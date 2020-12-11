import random
from ..base import AbstractEdit
from . import AbstractParamsEngine

class ParamSetting(AbstractEdit):
    def apply(self, program, new_contents, modification_points):
        engine = program.engines[self.target[0]]
        return engine.do_set(program, self.target, self.data[0], new_contents, modification_points)

    @classmethod
    def create(cls, program, target_file=None, method='random'):
        if target_file is None:
            target_file = program.random_file(AbstractParamsEngine)
        param_id = program.random_target(target_file, method)[1]
        engine = program.engines[target_file]
        data = engine.random_value(param_id)
        return cls((target_file, param_id), data)
