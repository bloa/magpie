import argparse
import configparser
import pathlib

import magpie
import magpie.astor # not by default

from magpie.bin import BasicProgram, BasicProtocol
from magpie.bin import setup_magpie, setup_protocol


# ================================================================================
# Target software specifics
# ================================================================================

class MyProgram(BasicProgram):
    def __init__(self, config):
        super().__init__(config)
        self.possible_edits = [
            magpie.astor.StmtReplacement,
            magpie.astor.StmtInsertion,
            magpie.astor.StmtDeletion,
        ]

    def get_engine(self, target_file):
        return magpie.astor.AstorEngine

    def process_run_exec(self, run_result, exec_result):
        run_result.fitness = round(exec_result.runtime, 4)


# ================================================================================
# Main function
# ================================================================================

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='MAGPIE Astor Runtime Example')
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
