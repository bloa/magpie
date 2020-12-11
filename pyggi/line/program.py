from ..base import AbstractProgram
from . import LineEngine

class LineProgram(AbstractProgram):
    def get_engine(self, file_name):
        return LineEngine
