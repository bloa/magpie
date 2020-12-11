from . import AbstractLineEngine

class LineEngine(AbstractLineEngine):
    @classmethod
    def get_contents(cls, file_path):
        with open(file_path, 'r') as target_file:
            return list(map(str.rstrip, target_file.readlines()))

    @classmethod
    def get_modification_points(cls, contents_of_file):
        return list(range(len(contents_of_file)))

    @classmethod
    def get_source(cls, program, file_name, index):
        return program.contents[file_name][index]

    @classmethod
    def dump(cls, contents_of_file):
        return '\n'.join(contents_of_file) + '\n'

    @classmethod
    def do_replace(cls, program, target_dest, target_orig, new_contents, modification_points):
        l_f, l_n = target_dest # line file and line number
        i_f, i_n = target_orig
        new_contents[l_f][modification_points[l_f][l_n]] = program.contents[i_f][i_n]
        return True

    @classmethod
    def do_insert(cls, program, target_dest, target_orig, direction, new_contents, modification_points):
        l_f, l_n = target_dest
        i_f, i_n = target_orig
        if direction == 'before':
            new_contents[l_f].insert(
                modification_points[l_f][l_n],
                program.contents[i_f][i_n]
            )
            for i in range(l_n, len(modification_points[l_f])):
                modification_points[l_f][i] += 1
        elif direction == 'after':
            new_contents[l_f].insert(
                modification_points[l_f][l_n] + 1,
                program.contents[i_f][i_n]
            )
            for i in range(l_n + 1, len(modification_points[l_f])):
                modification_points[l_f][i] += 1
        return True

    @classmethod
    def do_delete(cls, program, target, new_contents, modification_points):
        l_f, l_n = target
        new_contents[l_f][modification_points[l_f][l_n]] = ''
        return True
