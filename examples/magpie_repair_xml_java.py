import argparse
import configparser
import pathlib
import re

import magpie

from magpie.bin.shared import ExpProtocol
from magpie.bin.shared import setup_magpie, setup_protocol


# ================================================================================
# Target software specifics
# ================================================================================

class MyEngine(magpie.xml.SrcmlEngine):
    INTERNODES = ['block']
    TAG_RENAME = {
        'stmt': {'break', 'continue', 'decl_stmt', 'do', 'expr_stmt', 'for', 'goto', 'if', 'return', 'switch', 'while'},
    }
    TAG_FOCUS = {'block', 'stmt', 'operator_comp', 'expr'}


class MyProgram(magpie.base.Program):
    def __init__(self, config):
        self.base_init(config['software']['path'])
        self.possible_edits = [
            magpie.xml.StmtReplacement,
            magpie.xml.StmtInsertion,
            magpie.xml.StmtDeletion,
            magpie.xml.ExprReplacement,
            magpie.xml.ComparisonOperatorSetting,
        ]
        self.target_files = config['software']['target_files'].split()
        self.compile_cmd = config['software']['compile_cmd']
        self.test_cmd = config['software']['test_cmd']
        self.run_cmd = config['software']['run_cmd']
        self.reset_timestamp()
        self.reset_logger()
        self.reset_contents()

    def get_engine(self, target_file):
        return MyEngine

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
    protocol.search.stop['fitness'] = 0
    protocol.program = MyProgram(config)
    setup_protocol(protocol, config)

    # run experiments
    protocol.run()
