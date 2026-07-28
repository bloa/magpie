import abc


class AbstractExecManager(abc.ABC):
    # software
    # unix_timestamp
    # work_dir
    # env_counter
    # env_patch

    @abc.abstractmethod
    def setup(self):
        pass

    @abc.abstractmethod
    def reset(self):
        pass

    @abc.abstractmethod
    def write_variant(self, variant):
        pass

    @abc.abstractmethod
    def sync_folder(self, target, original):
        pass
