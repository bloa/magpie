import argparse
import configparser
import os
import pathlib
import random

import magpie

from magpie.bin import BasicProgram, BasicProtocol
from magpie.bin import setup_magpie

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='MAGPIE genetic programming')
    parser.add_argument('--scenario', type=pathlib.Path, required=True)
    parser.add_argument('--algo', type=str, choices=['gp_concat', 'gp_1point', 'gp_2point', 'gp_uconcat', 'gp_uinter'])
    parser.add_argument('--seed', type=int)
    args = parser.parse_args()

    # sets random seed
    if args.seed is not None:
        random.seed(args.seed)

    # read config file
    config = configparser.ConfigParser()
    config.read(args.scenario)
    setup_magpie(config)

    # read from config file if necessary
    if 'search' not in config:
        config['search'] = {}
    if args.algo is not None:
        config['search']['algo'] = args.algo
    elif 'algo' in config['search']:
        args.algo = config['search']['algo']
    else:
        args.algo = config['search']['algo'] = 'gp_concat'

    # select GP algorithm
    if args.algo == 'gp_concat':
        gp = magpie.algo.GeneticProgrammingConcat
    elif args.algo == 'gp_1point':
        gp = magpie.algo.GeneticProgramming1Point
    elif args.algo == 'gp_2point':
        gp = magpie.algo.GeneticProgramming2Point
    elif args.algo == 'gp_uconcat':
        gp = magpie.algo.GeneticProgrammingUniformConcat
    elif args.algo == 'gp_uinter':
        gp = magpie.algo.GeneticProgrammingUniformInter

    # setup protocol
    protocol = BasicProtocol()
    protocol.search = gp()
    protocol.program = BasicProgram(config)
    protocol.setup(config)

    # run experiments
    protocol.run()
