from abc import abstractmethod
from ..base import AbstractModel

class AbstractTreeModel(AbstractModel):
    @classmethod
    @abstractmethod
    def do_replace(cls, software, op, new_contents, modification_points):
        pass

    @classmethod
    @abstractmethod
    def do_insert(cls, software, op, new_contents, modification_points):
        pass

    @classmethod
    @abstractmethod
    def do_delete(cls, software, op, new_contents, modification_points):
        pass
