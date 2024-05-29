import abc


class AbstractFitness(abc.ABC):
    def __init__(self, software):
        self.software = software
        self.maximize = False

    @abc.abstractmethod
    def process_init_exec(self, run_result, exec_result):
        pass

    @abc.abstractmethod
    def process_setup_exec(self, run_result, exec_result):
        pass

    @abc.abstractmethod
    def process_compile_exec(self, run_result, exec_result):
        pass

    @abc.abstractmethod
    def process_test_exec(self, run_result, exec_result):
        pass

    @abc.abstractmethod
    def process_run_exec(self, run_result, exec_result):
        pass
