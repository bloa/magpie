import argparse
import configparser
import pathlib

import magpie

from magpie.bin import BasicProgram, BasicProtocol
from magpie.bin import setup_magpie, setup_protocol


# ================================================================================
# Target software specifics
# ================================================================================

class MyEngine(magpie.params.ConfigFileParamsEngine):
    CLI_PREFIX = '-'
    CLI_GLUE = '='
    CLI_BOOLEAN = 'prefix'
    CLI_BOOLEAN_PREFIX_TRUE = ''
    CLI_BOOLEAN_PREFIX_FALSE = 'no-'

    @classmethod
    def resolve_cli_param(cls, all_params, param, value):
        # special parameters
        if param == 'sub-lim-unbounded':
            return ''
        if param == 'sub-lim':
            if all_params['sub-lim-unbounded'] == 'True':
                return '-sub-lim=-1'
        if param == 'cl-lim-unbounded':
            return ''
        if param == 'cl-lim':
            if all_params['cl-lim-unbounded'] == 'True':
                return '-cl-lim=-1'

        # all other parameters
        return super().resolve_cli_param(all_params, param, value)


class MyProgram(BasicProgram):
    def __init__(self, config):
        super().__init__(config)
        self.possible_edits = [
            magpie.params.ParamSetting,
        ]

    def get_engine(self, target_file):
        return MyEngine

    def process_run_exec(self, run_result, exec_result):
        run_result.fitness = round(exec_result.runtime, 4)


# ================================================================================
# Main function
# ================================================================================

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='MAGPIE Runtime Example')
    parser.add_argument('--config', type=pathlib.Path, required=True)
    args = parser.parse_args()

    # read config file
    config = configparser.ConfigParser()
    config.read(args.config)
    setup_magpie(config)

    # setup protocol
    protocol = BasicProtocol()
    protocol.search = magpie.algo.FirstImprovement()
    protocol.program = MyProgram(config)
    setup_protocol(protocol, config)

    # run experiments
    protocol.run()
