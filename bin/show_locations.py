import argparse
import ast
import configparser
import pathlib
import re
import sys

import magpie

from magpie.bin.shared import ExpProtocol, ExampleProgram
from magpie.bin.shared import setup_magpie, setup_protocol

from .magpie_runtime import MyProgram as MyRuntimeProgram
from .magpie_repair import MyProgram as MyRepairProgram
from .magpie_bloat import MyProgram as MyBloatProgram
from .magpie_config import MyProgram as MyConfigProgram


# ================================================================================

from magpie.line import LineReplacement
from magpie.line import LineInsertion
from magpie.line import LineDeletion
from magpie.params import ParamSetting


# ================================================================================
# Main function
# ================================================================================

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='MAGPIE Patch Minifier Example')
    parser.add_argument('--config', type=pathlib.Path, required=True)
    parser.add_argument('--filename', type=str)
    parser.add_argument('--type', type=str)
    parser.add_argument('--xml', default=False, action='store_true')
    args = parser.parse_args()

    # read config file
    config = configparser.ConfigParser()
    config.read(args.config)
    setup_magpie(config)

    # show locations
    program = ExampleProgram(config)
    target_files = config['software']['target_files'].split()
    for filename in program.target_files:
        if args.filename is not None and args.filename != filename:
            continue
        print('==== {} ===='.format(filename))
        if program.get_engine(filename) is magpie.xml.XmlEngine:
            if not args.xml:
                print('The detected engine for this file is XmlEngine, which may lead to a very large and not-so-useful output')
                print('If you excepted a SrcmlEngine instead replace ExampleProgram by your own program class')
                print('To disable this warning and show all XML locations use the --xml argument')
                continue
        for type_ in program.locations[filename].keys():
            if args.type is not None and args.type != type_:
                continue
            print('---- {} ----'.format(type_))
            # for loc in range(len(program.locations[filename][type_])):
            for loc in program.location_names(filename, type_):
                print(program.show_location(filename, type_, loc))
            print()
    program.clean_work_dir()
