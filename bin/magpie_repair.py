import argparse
import configparser
import pathlib
import re

import magpie

from magpie.bin.shared import ExpProtocol
from magpie.bin.shared import apply_global_config

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
    protocol.search.stop['fitness'] = 0
    if 'max_iter' in config['search']:
        protocol.search.stop['steps'] = int(config['search']['max_iter'])
    if 'max_time' in config['search']:
        protocol.search.stop['wall'] = int(config['search']['max_time'])
    protocol.program = MyProgram(config)

    # run experiments
    protocol.run()
