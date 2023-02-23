import argparse
import configparser
import pathlib
import random

import magpie

from magpie.bin import BasicProgram, BasicProtocol
from magpie.bin import setup_magpie, algo_from_string


# ================================================================================
# Main function
# ================================================================================

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Magpie genetic programming')
    parser.add_argument('--scenario', type=pathlib.Path, required=True)
    parser.add_argument('--algo', type=str)
    parser.add_argument('--seed', type=int)
    args = parser.parse_args()

    # sets random seed
    if args.seed is not None:
        random.seed(args.seed)

    # read config file
    config = configparser.ConfigParser()
    config.read(args.scenario)
    setup_magpie(config)

    # select GP algorithm
    if 'search' not in config:
        config['search'] = {}
    if args.algo is not None:
        config['search']['algo'] = args.algo
        algo = algo_from_string(config['search']['algo'])
        if not issubclass(algo, magpie.algo.GeneticProgramming):
            raise RuntimeError('{} is not a GP algorithm'.format(args.algo))
    if 'algo' in config['search']:
        algo = algo_from_string(config['search']['algo'])
        if not issubclass(algo, magpie.algo.GeneticProgramming):
            algo = magpie.algo.GeneticProgrammingUniformConcat
    else:
        algo = magpie.algo.GeneticProgrammingUniformConcat

    # setup protocol
    protocol = BasicProtocol()
    protocol.search = algo()
    protocol.program = BasicProgram(config)
    protocol.setup(config)

    # run experiments
    protocol.run()
