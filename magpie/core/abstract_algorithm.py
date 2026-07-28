import abc


class AbstractAlgorithm(abc.ABC):
    # software
    # eval_manager
    # report

    @abc.abstractmethod
    def setup(self):
        pass

    @abc.abstractmethod
    def reset(self):
        pass

    @abc.abstractmethod
    def run(self):
        pass

