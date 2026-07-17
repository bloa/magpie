import abc


class AbstractEvalCache(abc.ABC):
    # config

    @abc.abstractmethod
    def reset(self):
        pass

    @abc.abstractmethod
    def setup(self, config):
        pass

    @abc.abstractmethod
    def get(self, diff):
        pass

    @abc.abstractmethod
    def update(self, diff, run):
        pass
