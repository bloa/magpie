import pathlib
import random

import magpie

from .abstract_model import AbstractModel


class BasicModel(AbstractModel):
    def __init__(self, filename, software):
        self.filename = filename
        self.renamed_filename = filename
        self.config = {}
        self.contents = {}
        self.locations = {}
        self.locations_names = {} # for indirection
        self.indirect_locations = True
        self.cached_dump = None
        self.readonly = False
        self.trust_local = magpie.settings.trust_local_filesystem
        self.weights = {}

    def init_other(self):
        if self.indirect_locations:
            self.locations_names = {key: list(range(len(value))) for key, value in self.locations.items()}
        else:
            self.locations_names = self.locations
        self.cached_dump = self.dump()

    def write_to_file(self):
        # silently ignore readonly models
        if self.readonly:
            return
        # compute dump
        dump = self.dump()
        # skip writing if file is (or should be) untouched
        if self.cached_dump is None:
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
        if target_type in self.locations_names:
            if tmp := self.locations_names[target_type]:
                loc = random.choice(tmp)
                return (self.filename, target_type, loc)
            return None
        return None

    def _resolve_config_section(self, software, filename):
        for (pattern, section_name) in software.model_config:
            if any([filename == pattern,
                    pattern == '*',
                    pattern.startswith('*') and filename.endswith(pattern[1:]),
            ]):
                return section_name
        return None
