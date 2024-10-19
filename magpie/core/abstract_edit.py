import abc
import re


class AbstractEdit:
    def __init__(self, target, *args):
        self.target = target
        self.data = list(args)

    @classmethod
    @abc.abstractmethod
    def auto_create(cls, ref):
        pass

    @abc.abstractmethod
    def apply(self, ref, variant):
        pass

    def __eq__(self, other):
        return (
            self.__class__ == other.__class__ and
            self.target == other.target and
            self.data == other.data
        )

    def __hash__(self):
        return hash(str(self))

    def __str__(self):
        base = re.sub(r'Edit(<.*>)?$', '\\1', self.__class__.__name__)
        if self.data:
            tmp = ', '.join([repr(d) for d in self.data])
            return f'{base}({self.target!r}, {tmp})'
        return f'{base}({self.target!r})'
