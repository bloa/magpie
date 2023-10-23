from abc import ABC, abstractmethod
import os
import random

import magpie

class AbstractModel(ABC):
    def renamed_contents_file(self, target_file):
        return target_file

    def write_contents_file(self, dump_cache, trust_local, new_contents, work_path, target_file):
        # compute dump
        filename = os.path.join(work_path, self.renamed_contents_file(target_file))
        dump = self.dump(new_contents[target_file])
        # skip writing if file is (or should be) untouched
        if dump_cache[target_file] == dump:
            if trust_local[target_file]:
                return
            else:
                with open(filename, 'r') as tmp_file:
                    if tmp_file.read() == dump:
                        return
                trust_local[target_file] = True
        # write only if file _really_ changed
        with open(filename, 'w') as tmp_file:
            tmp_file.write(dump)

    def random_target(self, locations, weights, target_file, target_type=None):
        if target_type is None:
            target_type = random.choice(locations[target_file])
        if weights and target_file in weights and target_type in weights[target_file]:
            total_weight = sum(weights[target_file][target_type])
            r = random.uniform(0, total_weight)
            for loc, w in enumerate(weights[target_file][target_type]):
                if r < w:
                    return (target_file, target_type, loc)
                r -= w
            return None
        else:
            try:
                loc = random.randrange(len(locations[target_file][target_type]))
                return (target_file, target_type, loc)
            except (KeyError, ValueError):
                return None

    @abstractmethod
    def get_contents(self, file_path):
        pass

    @abstractmethod
    def get_locations(self, contents):
        pass

    @abstractmethod
    def location_names(self, locations, target_file, target_type):
        pass

    @abstractmethod
    def dump(self, file_contents):
        pass

    def show_location(self, contents, locations, target_file, target_type, target_loc):
        return '(unsupported)'

