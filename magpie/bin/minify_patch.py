import argparse
import configparser
import pathlib

import magpie


# ================================================================================
# Main function
# ================================================================================

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Magpie patch minifier')
    parser.add_argument('--scenario', type=pathlib.Path, required=True)
    parser.add_argument('--patch', type=str, required=True)
    parser.add_argument('--seed', type=int)
    args = parser.parse_args()

    # read scenario file
    config = configparser.ConfigParser()
    config.read_dict(magpie.core.default_scenario)
    config.read(args.scenario)
    magpie.core.pre_setup(config)

    # recreate patch
    if args.patch.endswith('.patch'):
        with open(args.patch) as f:
            args.patch = f.read().strip()
    patch = magpie.core.Patch.from_string(args.patch)

    # setup
    config['search']['algorithm'] = 'ValidMinify'
    magpie.core.setup(config)
    protocol = magpie.utils.protocol_from_string(config['search']['protocol'])()
    protocol.search = magpie.utils.algo_from_string(config['search']['algorithm'])()
    protocol.search.debug_patch = patch
    protocol.software = magpie.utils.software_from_string(config['software']['software'])(config)

    # run experiments
    protocol.run(config)
