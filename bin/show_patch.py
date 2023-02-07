import argparse
import ast
import configparser
import pathlib
import re
import sys

import magpie

from magpie.bin import BasicProgram


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
    parser = argparse.ArgumentParser(description='MAGPIE Show Patch')
    parser.add_argument('--scenario', type=pathlib.Path, required=True)
    parser.add_argument('--patch', type=str, required=True)
    parser.add_argument('--keep', action='store_true')
    args = parser.parse_args()

    # read config file
    config = configparser.ConfigParser()
    config.read(args.scenario)

    # recreate patch
    if args.patch.endswith('.patch'):
        with open(args.patch) as f:
            args.patch = f.read().strip()
    patch = patch_from_string(args.patch)

    # setup program
    program = BasicProgram(config)

    # apply patch
    new_contents = program.apply_patch(patch)

    # show patch
    program.logger.info('==== REPORT ====')
    program.logger.info('Patch: {}'.format(patch))
    program.logger.info('Diff:\n{}'.format(program.diff_contents(new_contents)))
    if args.keep:
        program.logger.info('==== PATH ====')
        program.logger.info(program.work_dir)
        program.write_contents(new_contents)
    else:
        program.clean_work_dir()
