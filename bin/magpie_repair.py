import argparse
import configparser
import pathlib
import re

import magpie

from magpie.bin.shared import ExpProtocol, ExampleProgram
from magpie.bin.shared import setup_magpie, setup_protocol

# ================================================================================
# Target software specifics
# ================================================================================

class MyProgram(ExampleProgram):
    def process_test_exec(self, run_result, exec_result):
        stdout = exec_result.stdout.decode(magpie.config.output_encoding)
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
    setup_magpie(config)

    # setup protocol
    protocol = ExpProtocol()
    protocol.search = magpie.algo.FirstImprovement()
    protocol.search.stop['fitness'] = 0 # early stop when no bug left
    protocol.program = MyProgram(config)
    setup_protocol(protocol, config)

    # run experiments
    protocol.run()
