import argparse
import configparser
import pathlib

import magpie

from magpie.bin.shared import ExpProtocol, ExampleProgram
from magpie.bin.shared import setup_magpie, setup_protocol

# ================================================================================
# Target software specifics
# ================================================================================

class MyProgram(ExampleProgram):
    def __init__(self, config):
        super(config)
        self.possible_edits = [
            magpie.params.ParamSetting,
        ]

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
