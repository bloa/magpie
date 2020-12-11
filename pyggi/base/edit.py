from abc import ABC, abstractmethod

class AbstractEdit(ABC):
    def __init__(self, target, *args):
        self.target = target
        self.data = list(args)

    def __eq__(self, other):
        return (
            self.__class__ == other.__class__ and
            self.target == other.target and
            self.data == other.data
        )

    def __str__(self):
        return "{}({}{})".format(
            self.__class__.__name__,
            self.target,
            ''.join([', {}'.format(repr(d)) for d in self.data])
        )

    @abstractmethod
    def apply(self, program, new_contents, new_locations):
        pass
