from .abstract_fitness import AbstractFitness


class BasicFitness(AbstractFitness):
    def process_init_exec(self, run_result, exec_result):
        # "[software] init_cmd" must yield nonzero return code
        if exec_result.return_code != 0:
            run_result.status = 'CODE_ERROR'

    def process_setup_exec(self, run_result, exec_result):
        # "[software] setup_cmd" must yield nonzero return code
        if exec_result.return_code != 0:
            run_result.status = 'CODE_ERROR'

    def process_compile_exec(self, run_result, exec_result):
        # "[software] compile_cmd" must yield nonzero return code
        if exec_result.return_code != 0:
            run_result.status = 'CODE_ERROR'

    def process_test_exec(self, run_result, exec_result):
        # "[software] test_cmd" must yield nonzero return code
        if exec_result.return_code != 0:
            run_result.status = 'CODE_ERROR'

    def process_run_exec(self, run_result, exec_result):
        # "[software] run_cmd" must yield nonzero return code
        if exec_result.return_code != 0:
            run_result.status = 'CODE_ERROR'
