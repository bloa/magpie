import abc

import magpie


class AbstractModel(abc.ABC):
    # filename
    # renamed_filename
    # contents
    # locations
    # locations_names
    # indirect_locations
    # cached_dump
    # readonly

    @abc.abstractmethod
    def init_contents(self):
        pass

    @abc.abstractmethod
    def init_other(self):
        pass

    @abc.abstractmethod
    def dump(self):
        pass

    @abc.abstractmethod
    def write_to_file(self):
        pass

    @abc.abstractmethod
    def random_target(self, target_type=None):
        pass

    def update_cli(self, variant, cli, step):
        return cli

    def show_location(self, target_type, target_loc):
        msg = '(unsupported)'
        if magpie.settings.color_output:
            return f'\033[31m{msg}\033[0m'
        return msg
