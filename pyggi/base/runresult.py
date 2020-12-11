class RunResult:
    def __init__(self, status, fitness=None):
        self.status = status
        self.fitness = fitness

    def __str__(self):
        return '<{} {}>'.format(self.__class__.__name__, str(vars(self))[1:-1])
