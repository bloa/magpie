from abc import ABC, abstractmethod

class AbstractEngine(ABC):
    @classmethod
    @abstractmethod
    def get_contents(cls, file_path):
        pass

    @classmethod
    @abstractmethod
    def get_modification_points(cls, contents_of_file):
        pass

    @classmethod
    @abstractmethod
    def get_source(cls, program, file_name, index):
        pass

    @classmethod
    def write_to_tmp_dir(cls, contents_of_file, tmp_path):
        with open(tmp_path, 'w') as tmp_file:
            tmp_file.write(cls.dump(contents_of_file))

    @classmethod
    @abstractmethod
    def dump(cls, contents_of_file):
        pass

