import argparse
import pathlib

import magpie


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Magpie search')
    parser.add_argument('--scenario', type=pathlib.Path, required=True)
    parser.add_argument('--algo', type=str, default='FirstImprovement')
    parser.add_argument('--seed', type=int)
    args = parser.parse_args()

    protocol = magpie.core.SearchProtocol(args.scenario)
    protocol.config['search']['algorithm'] = args.algo
    if args.seed:
        protocol.config['magpie']['seed'] = args.seed
    protocol.setup()
    protocol.run()
    protocol.report()
    protocol.cleanup()
