from ..base import AbstractProgram
from . import LineEngine

class LineProgram(AbstractProgram):
    @classmethod
    def get_engine(cls, file_name):
        return LineEngine
