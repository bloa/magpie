import abc
import pathlib
import random

import magpie.settings


class AbstractModel(abc.ABC):
    def __init__(self, filename):
        self.filename = filename
        self.renamed_filename = filename
        self.contents = {}
        self.locations = {}
        self.locations_names = {} # for indirection
        self.indirect_locations = True
        self.weights = {}
        self.trust_local = magpie.settings.trust_local_filesystem
        self.cached_dump = None

    @abc.abstractmethod
    def init_contents(self):
        pass

    @abc.abstractmethod
    def dump(self):
        pass

    def show_location(self, target_type, target_loc):
        msg = '(unsupported)'
        if magpie.settings.color_output:
            return f'\033[31m{msg}\033[0m'
        return msg

    def write_to_file(self):
        # compute dump
        dump = self.dump()
        # skip writing if file is (or should be) untouched
        if not self.cached_dump:
            raise RuntimeError
        if dump == self.cached_dump:
            if self.trust_local:
                return
            with pathlib.Path(self.renamed_filename).open('r') as tmp_file:
                if tmp_file.read() == dump:
                    return
            self.trust_local = True
        # write only if file _really_ changed
        with pathlib.Path(self.renamed_filename).open('w') as tmp_file:
            tmp_file.write(dump)

    def random_target(self, target_type=None):
        if target_type is None:
            target_type = random.choice(list(self.locations.keys()))
        if target_type in self.weights:
            total_weight = sum(self.weights[target_type])
            r = random.uniform(0, total_weight)
            for loc, w in enumerate(self.weights[target_type]):
                if r < w:
                    return (self.filename, target_type, loc)
                r -= w
            raise RuntimeError
        loc = random.choice(self.locations_names[target_type])
        return (self.filename, target_type, loc)

    def update_cli(self, variant, cli, step):
        return cli
