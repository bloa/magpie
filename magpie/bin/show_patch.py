import argparse
import pathlib

import magpie

class ShowPatchProtocol(magpie.core.BasicProtocol):
    def setup(self, patch, keep):
        super().setup()

        # recreate patch
        if patch.endswith('.patch'):
            with pathlib.Path(patch).open('r') as f:
                patch = f.read().strip()
        self.patch = magpie.core.Patch.from_string(patch)

        # compute variant (which includes diff)
        self.software = magpie.utils.software_from_string(self.config['software']['software'])(self.config)
        self.variant = magpie.core.Variant(self.software, self.patch)

        # to write artefact on disk
        self.keep = args.keep

    def run(self):
        pass

    def report(self):
        fancy = magpie.settings.color_output
        header = magpie.utils.format_header('PATCH', fancy)
        self.software.logger.info('%s\n%s', header, self.patch)
        if self.keep:
            self.software.logger.info('')
            header = magpie.utils.format_header('ARTEFACT', fancy)
            self.software.logger.info('%s\n%s', self.software.work_dir)
            self.software.write_variant(self.variant)
        self.software.logger.info('')
        header = magpie.utils.format_header('DIFF', fancy)
        diff = magpie.utils.format_diff(self.variant.diff[:], fancy)
        self.software.logger.info('%s\n%s', header, diff)

    def cleanup(self):
        if not self.keep:
            self.software.clean_work_dir()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Magpie show patch')
    parser.add_argument('--scenario', type=pathlib.Path, required=True)
    parser.add_argument('--patch', type=str, required=True)
    parser.add_argument('--keep', action='store_true')
    args = parser.parse_args()

    protocol = ShowPatchProtocol(args.scenario)
    protocol.setup(patch=args.patch, keep=args.keep)
    protocol.run()
    protocol.report()
    protocol.cleanup()
