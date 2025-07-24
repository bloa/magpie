import abc


class AbstractProtocol(abc.ABC):
    @abc.abstractmethod
    def setup(self):
        pass

    @abc.abstractmethod
    def run(self):
        pass

    @abc.abstractmethod
    def report(self):
        pass

    @abc.abstractmethod
    def cleanup(self):
        pass
