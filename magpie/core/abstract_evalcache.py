import abc


class AbstractEvalCache(abc.ABC):
    def __init__(self):
        self.config = {}
        self.config['maxsize'] = 0
        self.reset()

    def reset(self):
        self.stats = {}
        self.stats['hits'] = 0
        self.stats['misses'] = 0

    @abc.abstractmethod
    def get(self, diff):
        pass

    @abc.abstractmethod
    def update(self, diff, run):
        pass
