import argparse
import configparser
import pathlib
import os
import re

import magpie

from magpie.bin import BasicProgram, BasicProtocol
from magpie.bin import setup_magpie, setup_protocol


# ================================================================================
# Target software specifics
# ================================================================================

class MyProgram(BasicProgram):
    def __init__(self, config):
        super().__init__(config)
        self.possible_edits = [
            magpie.line.LineDeletion,
        ]
        self.run_cmd = None # handled in evaluated_local instead

    def evaluate_local(self):
        # first compile and test as usual
        run_result = super().evaluate_local()
        if run_result.status != 'SUCCESS':
            return run_result

        # if compilation and test are both successful
        cwd = os.getcwd()
        try:
            # go to work directory
            os.chdir(os.path.join(self.work_dir, self.basename))

            # count lines
            run_result.fitness = 0
            for filename in self.target_files:
                with open(filename) as target:
                    run_result.fitness += len(target.readlines())
        finally:
            # make sure to go back to main directory
            os.chdir(cwd)
        return run_result

# ================================================================================
# Main function
# ================================================================================

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='MAGPIE Bloat Reduction Example')
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
