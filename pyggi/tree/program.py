from ..base import AbstractProgram
from ..utils import get_file_extension
from . import AstorEngine, XmlEngine

class TreeProgram(AbstractProgram):
    @classmethod
    def get_engine(cls, file_name):
        extension = get_file_extension(file_name)
        if extension in ['.py']:
            return AstorEngine
        elif extension in ['.xml']:
            return XmlEngine
        raise Exception('{} file is not supported'.format(extension))
