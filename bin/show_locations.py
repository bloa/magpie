import argparse
import configparser
import pathlib

import magpie


# ================================================================================
# Main function
# ================================================================================

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Magpie show locations')
    parser.add_argument('--scenario', type=pathlib.Path, required=True)
    parser.add_argument('--filename', type=str)
    parser.add_argument('--type', type=str)
    parser.add_argument('--xml', default=False, action='store_true')
    args = parser.parse_args()

    # read config file
    config = configparser.ConfigParser()
    config.read_dict(magpie.bin.default_config)
    config.read(args.scenario)

    # setup
    magpie.bin.pre_setup(config)
    magpie.bin.setup(config)
    software = magpie.bin.software_from_string(config['software']['software'])(config)
    software.ensure_contents()

    # show locations
    target_files = config['software']['target_files'].split()
    for filename in software.target_files:
        if args.filename is not None and args.filename != filename:
            continue
        print('==== {} ===='.format(filename))
        if software.get_model(filename) is magpie.xml.XmlModel:
            if not args.xml:
                print('The detected model for this file is XmlModel, which may lead to a very large and not-so-useful output')
                print('If you excepted a SrcmlModel instead replace BasicSoftware by your own software class')
                print('To disable this warning and show all XML locations use the --xml argument')
                continue
        for type_ in software.locations[filename].keys():
            if args.type is not None and args.type != type_:
                continue
            print('---- {} ----'.format(type_))
            for loc in software.location_names(filename, type_):
                print(software.show_location(filename, type_, loc))
            print()
    software.clean_work_dir()
