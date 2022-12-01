from abc import ABC, abstractmethod
import os
import random

class AbstractEngine(ABC):
    @classmethod
    def renamed_contents_file(cls, target_file):
        return target_file

    @classmethod
    def write_contents_file(cls, new_contents, work_path, target_file):
        filename = os.path.join(work_path, cls.renamed_contents_file(target_file))
        with open(filename, 'w') as tmp_file:
            tmp_file.write(cls.dump(new_contents[target_file]))

    @classmethod
    def random_target(cls, locations, weights, target_file, target_type=None):
        if target_type is None:
            target_type = random.choice(locations[target_file])
        if weights and target_file in weights and target_type in weights[target_file]:
            total_weight = sum(weights[target_file][target_type])
            r = random.uniform(0, total_weight)
            for loc, w in zip(locations[target_file][target_type], weights[target_file][target_type]):
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

    @classmethod
    @abstractmethod
    def get_contents(cls, file_path):
        pass

    @classmethod
    @abstractmethod
    def get_locations(cls, file_contents):
        pass

    @classmethod
    @abstractmethod
    def dump(cls, file_contents):
        pass
