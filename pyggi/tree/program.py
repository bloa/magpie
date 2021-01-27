import os

from .. import config as pyggi_config
from ..base import AbstractProgram
if pyggi_config.enable_astor:
    from . import AstorEngine
from . import XmlEngine

class TreeProgram(AbstractProgram):
    def get_engine(self, file_name):
        _, extension = os.path.splitext(file_name)
        if pyggi_config.enable_astor and extension in ['.py']:
            return AstorEngine
        if extension in ['.xml']:
            return XmlEngine
        raise Exception('{} file is not supported'.format(extension))
