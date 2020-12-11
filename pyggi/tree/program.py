import os

from ..base import AbstractProgram
from . import AstorEngine, XmlEngine

class TreeProgram(AbstractProgram):
    def get_engine(self, file_name):
        _, extension = os.path.splitext(file_name)
        if extension in ['.py']:
            return AstorEngine
        elif extension in ['.xml']:
            return XmlEngine
        raise Exception('{} file is not supported'.format(extension))
