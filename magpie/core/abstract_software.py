import abc
import contextlib


class AbstractSoftware(abc.ABC):
    # logger
    # path
    # basename
    # target_files
    # ingredient_files
    # noop_variant
    # model_config
    # model_rules
    # work_dir
    # run_label

    @abc.abstractmethod
    def evaluate_variant(self, variant, cached_run=None):
        pass

    @abc.abstractmethod
    def write_variant(self, variant):
        pass

    @abc.abstractmethod
    @contextlib.contextmanager
    def add_to_env(self, counter=None, patch=None):
        pass

    @abc.abstractmethod
    def clean_work_dir(self):
        pass
