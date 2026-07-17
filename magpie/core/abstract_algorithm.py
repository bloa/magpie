import abc


class AbstractAlgorithm(abc.ABC):
    # software
    # report

    @abc.abstractmethod
    def reset(self):
        pass

    @abc.abstractmethod
    def run(self):
        pass

