import argparse
import configparser
import pathlib

import magpie

# ================================================================================
# Main function
# ================================================================================

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Magpie show patch')
    parser.add_argument('--scenario', type=pathlib.Path, required=True)
    parser.add_argument('--patch', type=str, required=True)
    parser.add_argument('--keep', action='store_true')
    args = parser.parse_args()

    # read scenario file
    config = configparser.ConfigParser()
    config.read_dict(magpie.core.default_scenario)
    config.read(args.scenario)
    magpie.core.pre_setup(config)

    # recreate patch
    if args.patch.endswith('.patch'):
        with pathlib.Path(args.patch).open('r') as f:
            args.patch = f.read().strip()
    patch = magpie.core.Patch.from_string(args.patch)

    # setup
    magpie.core.setup(config)
    software = magpie.utils.software_from_string(config['software']['software'])(config)
    variant = magpie.core.Variant(software, patch)

    # show patch
    fancy = magpie.settings.color_output
    header = magpie.utils.format_header('PATCH', fancy)
    software.logger.info('%s\n%s', header, patch)
    if args.keep:
        software.logger.info('')
        header = magpie.utils.format_header('ARTEFACT', fancy)
        software.logger.info('%s\n%s', header, software.work_dir)
        software.write_variant(variant)
    software.logger.info('')
    header = magpie.utils.format_header('DIFF', fancy)
    diff = magpie.utils.format_diff(variant.diff, fancy)
    software.logger.info('%s\n%s', header, diff)
    if not args.keep:
        software.clean_work_dir()
