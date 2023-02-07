import argparse
import ast
import configparser
import pathlib
import re
import sys

import magpie

from magpie.bin import BasicProgram, BasicProtocol
from magpie.bin import setup_magpie


# ================================================================================

from magpie.xml import xml_edits
from magpie.line import line_edits
from magpie.params import params_edits

def patch_from_string(s):
    patch = magpie.base.Patch()
    for blob in s.split(' | '):
        match = re.search(r"^(\w+)\((.+)\)$", blob)
        for klass in [*xml_edits, *line_edits, *params_edits]:
            if klass.__name__ == match.group(1):
                args = ast.literal_eval("[{}]".format(match.group(2)))
                patch.edits.append(klass(*args))
                break
        else:
            raise RuntimeError('Unknown edit type "{}" in patch'.format(edit))
    assert str(patch) == s
    return patch


# ================================================================================
# Main function
# ================================================================================

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='MAGPIE revalidate')
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
    protocol.search = magpie.algo.ValidTest()
    protocol.search.debug_patch = patch
    protocol.program = BasicProgram(config)
    protocol.setup(config)

    # run experiments
    protocol.run()
