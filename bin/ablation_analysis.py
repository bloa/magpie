import argparse
import configparser
import pathlib

import magpie

from magpie.bin import BasicProgram, BasicProtocol
from magpie.bin import setup_magpie, patch_from_string


# ================================================================================
# Main function
# ================================================================================

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Magpie patch ablation analysis')
    parser.add_argument('--scenario', type=pathlib.Path, required=True)
    parser.add_argument('--patch', type=str, required=True)
    args = parser.parse_args()

    # read config file
    config = configparser.ConfigParser()
    config.read(args.scenario)
    setup_magpie(config)

    # recreate patch
    if args.patch.endswith('.patch'):
        with open(args.patch) as f:
            args.patch = f.read().strip()
    patch = patch_from_string(args.patch)

    # setup protocol
    protocol = BasicProtocol()
    protocol.search = magpie.algo.AblationAnalysis()
    protocol.search.debug_patch = patch
    protocol.program = BasicProgram(config)
    protocol.setup(config)

    # run experiments
    protocol.run()
