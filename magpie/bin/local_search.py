import argparse
import pathlib

import magpie

class LocalSearchProtocol(magpie.core.SearchProtocol):
    def setup(self):
        super().setup()
        if not issubclass(self.search.__class__, magpie.algos.LocalSearch):
            msg = f'Invalid local search algorithm "{self.search.__name__}"'
            raise RuntimeError(msg)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Magpie local search')
    parser.add_argument('--scenario', type=pathlib.Path, required=True)
    parser.add_argument('--algo', type=str, default='FirstImprovement')
    parser.add_argument('--seed', type=int)
    args = parser.parse_args()

    protocol = LocalSearchProtocol(args.scenario)
    if args.algo:
        protocol.config['search']['algorithm'] = args.algo
    if args.seed:
        protocol.config['magpie']['seed'] = args.seed
    protocol.setup()
    protocol.run()
    protocol.report()
    protocol.cleanup()
