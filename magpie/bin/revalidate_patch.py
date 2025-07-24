import argparse
import pathlib

import magpie


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Magpie patch revalidator')
    parser.add_argument('--scenario', type=pathlib.Path, required=True)
    parser.add_argument('--patch', type=str, required=True)
    args = parser.parse_args()

    protocol = magpie.core.SearchPatchProtocol(args.scenario)
    protocol.config['search']['algorithm'] = 'ValidTest'
    protocol.setup(args.patch)
    protocol.run()
    protocol.report()
    protocol.cleanup()
