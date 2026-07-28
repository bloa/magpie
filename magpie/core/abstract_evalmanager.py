import abc


class AbstractEvalManager(abc.ABC):
    # software
    # exec_manager
    # config
    # report

    @abc.abstractmethod
    def setup(self):
        pass

    @abc.abstractmethod
    def reset(self):
        pass

    @abc.abstractmethod
    def evaluate_variant(self, variant, force=False):
        pass

    @abc.abstractmethod
    def cache_get(self, diff):
        pass

    @abc.abstractmethod
    def cache_update(self, diff, run):
        pass

