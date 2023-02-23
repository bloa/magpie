import argparse
import configparser
import pathlib
import random

import magpie

from magpie.bin import BasicProgram, BasicProtocol
from magpie.bin import setup_magpie, algo_from_string, patch_from_string


# ================================================================================
# Main function
# ================================================================================

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Magpie patch minifier')
    parser.add_argument('--scenario', type=pathlib.Path, required=True)
    parser.add_argument('--algo', type=str)
    parser.add_argument('--patch', type=str, required=True)
    parser.add_argument('--seed', type=int)
    args = parser.parse_args()

    # sets random seed
    if args.seed is not None:
        random.seed(args.seed)

    # read config file
    config = configparser.ConfigParser()
    config.read(args.scenario)
    setup_magpie(config)

    # recreate patch
    if args.patch.endswith('.patch'):
        with open(args.patch) as f:
            args.patch = f.read().strip()
    patch = patch_from_string(args.patch)

    # select algorithm
    if args.algo is not None:
        algo = algo_from_string(args.algo)
        if not issubclass(algo, magpie.algo.ValidSearch):
            raise RuntimeError('{} is not a valid algorithm'.format(args.algo))
    else:
        algo = magpie.algo.ValidRankingSimplify

    # setup protocol
    protocol = BasicProtocol()
    protocol.search = algo()
    protocol.search.debug_patch = patch
    protocol.program = BasicProgram(config)
    protocol.setup(config)

    # run experiments
    protocol.run()
