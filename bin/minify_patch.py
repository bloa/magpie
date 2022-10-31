import argparse
import ast
import configparser
import pathlib
import re
import sys

import magpie

from magpie.bin.shared import ExpProtocol
from magpie.bin.shared import apply_global_config

from .magpie_runtime import MyProgram as MyRuntimeProgram
from .magpie_repair import MyProgram as MyRepairProgram
from .magpie_bloat import MyProgram as MyBloatProgram
from .magpie_config import MyProgram as MyConfigProgram

# ================================================================================

from magpie.line import LineReplacement
from magpie.line import LineInsertion
from magpie.line import LineDeletion
from magpie.params import ParamSetting

def patch_from_string(s):
    patch = magpie.base.Patch()
    for blob in s.split(' | '):
        match = re.search(r"^(\w+)\((.+)\)$", blob)
        cls = getattr(sys.modules[__name__], match.group(1))
        args = ast.literal_eval("[{}]".format(match.group(2)))
        patch.edits.append(cls(*args))
    assert str(patch) == s
    return patch


# ================================================================================
# Main function
# ================================================================================

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='MAGPIE Patch Minifier Example')
    parser.add_argument('--mode', type=str, choices=['repair', 'runtime', 'bloat', 'config'], required=True)
    parser.add_argument('--config', type=pathlib.Path, required=True)
    parser.add_argument('--patch', type=str, required=True)
    args = parser.parse_args()

    # read config file
    config = configparser.ConfigParser()
    config.read(args.config)
    apply_global_config(config)

    # recreate patch
    patch = patch_from_string(args.patch)

    # setup protocol
    protocol = ExpProtocol()
    protocol.search = magpie.algo.ValidRankingSimplify()
    protocol.search.debug_patch = patch
    if args.mode == 'repair':
        protocol.program = MyRepairProgram(config)
    elif args.mode == 'runtime':
        protocol.program = MyRuntimeProgram(config)
    elif args.mode == 'bloat':
        protocol.program = MyBloatProgram(config)
    elif args.mode == 'config':
        protocol.program = MyConfigProgram(config)

    # run experiments
    protocol.run()
