import types


class RunResult(types.SimpleNamespace):
    def __init__(self, variant, status=None):
        self.variant = variant
        self.status = status
        self.fitness = None
        self.cache = {}
        self.log = ''
        self.last_exec = None
        self.cached = False
        self.updated = False
