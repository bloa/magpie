import argparse
import configparser
import pathlib

import magpie

# ================================================================================
# Main function
# ================================================================================

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Magpie genetic programming')
    parser.add_argument('--scenario', type=pathlib.Path, required=True)
    parser.add_argument('--algo', type=str)
    parser.add_argument('--seed', type=int)
    args = parser.parse_args()

    # read scenario file
    config = configparser.ConfigParser()
    config.read_dict(magpie.core.default_scenario)
    config.read(args.scenario)
    magpie.core.pre_setup(config)

    # select GP algorithm
    if args.algo is not None:
        config['search']['algorithm'] = args.algo
    if config['search']['algorithm']:
        algo = magpie.utils.algo_from_string(config['search']['algorithm'])
        if not issubclass(algo, magpie.algos.GeneticProgramming):
            msg = f'Invalid genetic programming algorithm "{algo.__name__}"'
            raise RuntimeError(msg)
    else:
        config['search']['algorithm'] = 'GeneticProgrammingUniformConcat'
        algo = magpie.algos.GeneticProgrammingUniformConcat

    # setup protocol
    magpie.core.setup(config)
    protocol = magpie.utils.protocol_from_string(config['search']['protocol'])()
    protocol.search = algo()
    protocol.software = magpie.utils.software_from_string(config['software']['software'])(config)

    # run experiments
    protocol.run(config)
