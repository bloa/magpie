import argparse
import configparser
import pathlib
import re

import magpie

from magpie.bin.shared import ExpProtocol
from magpie.bin.shared import apply_global_config, setup_protocol

# ================================================================================
# Target software specifics
# ================================================================================

class MyProgram(magpie.base.Program):
    def __init__(self, config):
        self.base_init(config['software']['path'])
        self.possible_edits = [
            magpie.line.LineReplacement,
            magpie.line.LineInsertion,
            magpie.line.LineDeletion,
        ]
        self.target_files = config['software']['target_files'].split()
        self.compile_cmd = config['software']['compile_cmd']
        self.test_cmd = config['software']['test_cmd']
        self.run_cmd = config['software']['run_cmd']
        self.reset_timestamp()
        self.reset_logger()
        self.reset_contents()

    def get_engine(self, target_file):
        return magpie.line.LineEngine

    def process_test_exec(self, run_result, exec_result):
        stdout = exec_result.stdout.decode('ascii')
        matches = re.findall(' (\d+) (?:fail|error)', stdout)
        fails = 0
        if matches:
            for m in matches:
                try:
                    fails += float(m)
                except ValueError:
                    run_result.status = 'PARSE_ERROR'
            run_result.fitness = fails
            return
        matches = re.findall(' (\d+) (?:pass)', stdout)
        if matches:
            run_result.fitness = 0
        else:
            run_result.status = 'PARSE_ERROR'


# ================================================================================
# Main function
# ================================================================================

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='MAGPIE Bug Repair Example')
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
    protocol.search.stop['fitness'] = 0 # early stop when no bug left
    protocol.program = MyProgram(config)

    # run experiments
    protocol.run()
