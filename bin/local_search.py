import argparse
import configparser
import os
import pathlib
import random

import magpie

from magpie.bin import BasicProgram, BasicProtocol
from magpie.bin import setup_magpie

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='MAGPIE local search')
    parser.add_argument('--scenario', type=pathlib.Path, required=True)
    parser.add_argument('--algo', type=str, choices=['ls_first', 'ls_best', 'ls_tabu', 'ls_walk', 'rand'])
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
        args.algo = config['search']['algo'] = 'ls_first'

    # select LS algorithm
    if args.algo == 'ls_first':
        ls = magpie.algo.FirstImprovement
    elif args.algo == 'ls_best':
        ls = magpie.algo.BestImprovement
    elif args.algo == 'ls_tabu':
        ls = magpie.algo.TabuSearch
    elif args.algo == 'ls_walk':
        ls = magpie.algo.RandomWalk
    elif args.algo == 'rand':
        ls = magpie.algo.RandomSearch

    # setup protocol
    protocol = BasicProtocol()
    protocol.search = ls()
    protocol.program = BasicProgram(config)
    protocol.setup(config)

    # run experiments
    protocol.run()
