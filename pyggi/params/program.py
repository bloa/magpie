from ..base import AbstractProgram
from ..utils import get_file_extension

class ParamsProgram(AbstractProgram):
    @classmethod
    def get_engine(cls, file_name):
        extension = get_file_extension(file_name)
        # TODO ParamsFileEngine
        raise Exception('{} file is not supported'.format(extension))
