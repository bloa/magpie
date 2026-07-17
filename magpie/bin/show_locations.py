import argparse
import pathlib

import magpie

class ShowLocationsProtocol(magpie.core.BasicProtocol):
    def setup(self, filename, tag):
        super().setup()

        self.filename = filename
        self.tag = tag
        self.software = magpie.utils.software_from_string(self.config['software']['software'])(self.config)

    def run(self):
        fancy = magpie.settings.color_output
        for filename in [*self.software.target_files, *self.software.ingredient_files]:
            if self.filename is not None and self.filename != filename:
                continue
            header = magpie.utils.format_header(filename, fancy)
            self.software.logger.info(header)
            model = self.software.noop_variant.models[filename]
            for tag in model.locations:
                if self.tag is not None and self.tag != tag:
                    continue
                header = magpie.utils.format_subheader(tag, fancy)
                self.software.logger.info(header)
                for loc in model.locations_names[tag]:
                    self.software.logger.info(model.show_location(tag, loc))
                self.software.logger.info('')

    def report(self):
        pass

    def cleanup(self):
        self.software.clean_work_dir()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Magpie show locations')
    parser.add_argument('--scenario', type=pathlib.Path, required=True)
    parser.add_argument('--filename', type=str)
    parser.add_argument('--tag', type=str)
    args = parser.parse_args()

    protocol = ShowLocationsProtocol(args.scenario)
    protocol.setup(filename=args.filename, tag=args.tag)
    protocol.run()
    protocol.cleanup()
