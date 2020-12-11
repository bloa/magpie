import os

from ..base import AbstractProgram

class ParamsProgram(AbstractProgram):
    @classmethod
    def get_engine(cls, file_name):
        _, extension = os.path.splitext(file_name)
        # TODO ParamsFileEngine
        raise Exception('{} file is not supported'.format(extension))
