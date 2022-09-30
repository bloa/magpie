import argparse
import configparser
import pathlib
import os
import re

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
            # magpie.line.LineReplacement,
            # magpie.line.LineInsertion,
            magpie.line.LineDeletion,
        ]
        self.target_files = config['program']['target_files'].split()
        self.compile_cmd = config['exec']['compile']
        self.test_cmd = config['exec']['test']
        self.run_cmd = None # handled in evaluated_local instead
        self.reset_timestamp()
        self.reset_logger()
        self.reset_contents()

    def get_engine(self, target_file):
        return magpie.line.LineEngine

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
    apply_global_config(config)

    # setup protocol
    protocol = ExpProtocol()
    protocol.search = magpie.algo.FirstImprovement()
    setup_protocol(protocol, config)
    protocol.program = MyProgram(config)

    # run experiments
    protocol.run()
