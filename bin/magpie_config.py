import argparse
import configparser
import pathlib

import magpie

from magpie.bin.shared import ExpProtocol
from magpie.bin.shared import setup_magpie, setup_protocol

# ================================================================================
# Target software specifics
# ================================================================================

class MyProgram(magpie.base.Program):
    def __init__(self, config):
        self.base_init(config['software']['path'])
        self.possible_edits = [
            magpie.params.ParamSetting,
        ]
        self.target_files = config['software']['target_files'].split()
        self.compile_cmd = config['software']['compile_cmd']
        self.test_cmd = config['software']['test_cmd']
        self.run_cmd = config['software']['run_cmd']
        self.reset_timestamp()
        self.reset_logger()
        self.reset_contents()

    def get_engine(self, target_file):
        return magpie.params.ConfigFileParamsEngine

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
    protocol = ExpProtocol()
    protocol.search = magpie.algo.FirstImprovement()
    protocol.program = MyProgram(config)
    setup_protocol(protocol, config)

    # run experiments
    protocol.run()
