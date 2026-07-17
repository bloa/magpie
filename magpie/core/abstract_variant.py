import abc


class AbstractVariant(abc.ABC):
    # models
    # patch
    # diff

    @abc.abstractmethod
    def cli(self, step):
        pass

    @abc.abstractmethod
    def random_model(self, klass, writable):
        pass
