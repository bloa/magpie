import argparse
import configparser
import pathlib

import magpie


# ================================================================================
# Main function
# ================================================================================

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Magpie show patch')
    parser.add_argument('--scenario', type=pathlib.Path, required=True)
    parser.add_argument('--patch', type=str, required=True)
    parser.add_argument('--keep', action='store_true')
    args = parser.parse_args()

    # read config file
    config = configparser.ConfigParser()
    config.read_dict(magpie.bin.default_config)
    config.read(args.scenario)
    magpie.bin.pre_setup(config)

    # recreate patch
    if args.patch.endswith('.patch'):
        with open(args.patch) as f:
            args.patch = f.read().strip()
    patch = magpie.bin.patch_from_string(args.patch)

    # setup
    magpie.bin.setup(config)
    program = magpie.bin.program_from_string(config['software']['program'])(config)

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
