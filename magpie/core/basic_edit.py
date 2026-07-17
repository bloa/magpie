from .abstract_edit import AbstractEdit

class BasicEdit(AbstractEdit):
    def __init__(self, target, *args):
        self.target = target
        self.data = list(args)
