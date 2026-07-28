import abc


class AbstractSoftware(abc.ABC):
    # config
    # logger
    # path
    # basename
    # target_files
    # ingredient_files
    # noop_variant
    # model_config
    # model_rules
    # fitness_trees
    # noop_variant
    # init_...
    # setup_...
    # compile_...
    # test_...
    # run_...
    # batch_...

    @abc.abstractmethod
    def setup(self):
        pass
