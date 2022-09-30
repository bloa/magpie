import argparse
import configparser
import pathlib

import magpie

from magpie.bin.shared import ExpProtocol
from magpie.bin.shared import apply_global_config, setup_protocol


# ================================================================================
# Target software specifics
# ================================================================================

class MyProgram(magpie.base.Program):
    def __init__(self, config):
        self.base_init(config['program']['path'])
        self.possible_edits = [
            magpie.line.LineReplacement,
            magpie.line.LineInsertion,
            magpie.line.LineDeletion,
        ]
        self.target_files = config['program']['target_files'].split()
        self.compile_cmd = config['exec']['compile']
        self.test_cmd = config['exec']['test']
        self.run_cmd = config['exec']['run']
        self.reset_timestamp()
        self.reset_logger()
        self.reset_contents()

    def get_engine(self, target_file):
        return magpie.line.LineEngine

    def process_run_exec(self, run_result, exec_result):
        run_result.fitness = round(exec_result.runtime, 4)


# ================================================================================
# Main function
# ================================================================================

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='MAGPIE Running Time Example')
    parser.add_argument('--config', type=pathlib.Path, required=True)
    args = parser.parse_args()

    # read config file
    config = configparser.ConfigParser()
    config.read(args.config)
    apply_global_config(config)

    # setup protocol
    protocol = ExpProtocol()
    protocol.search = magpie.algo.FirstImprovement()
    setup_protocol(protocol, config)
    print(protocol.search.config)
    protocol.program = MyProgram(config)

    # run experiments
    protocol.run()
