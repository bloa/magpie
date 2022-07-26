import types

class RunResult(types.SimpleNamespace):
    def __init__(self, status):
        self.status = status
        self.fitness = None
        self.log = ''
