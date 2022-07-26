from abc import ABC, abstractmethod
import os

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
