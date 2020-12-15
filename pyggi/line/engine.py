from . import AbstractLineEngine

class LineEngine(AbstractLineEngine):
    @classmethod
    def get_contents(cls, file_path):
        with open(file_path, 'r') as target_file:
            return list(map(str.rstrip, target_file.readlines()))

    @classmethod
    def get_locations(cls, contents):
        n = len(contents)
        return {'line': list(range(n)), '_inter_line': list(range(n+1))}

    @classmethod
    def dump(cls, contents_of_file):
        return ''.join(s + '\n' for s in contents_of_file if s is not None)

    @classmethod
    def do_replace(cls, contents, locations, new_contents, new_locations, target_dest, target_orig):
        d_f, d_t, d_i = target_dest # file name, "line", line index
        o_f, o_t, o_i = target_orig # file name, "line", line index
        assert d_t == o_t == 'line'
        if new_locations[d_f][d_t][d_i] is None:
            return False
        old_line = new_contents[d_f][new_locations[d_f][d_t][d_i]]
        new_line = contents[o_f][locations[o_f][o_t][o_i]]
        if new_line == old_line:
            return False
        else:
            new_contents[d_f][new_locations[d_f][d_t][d_i]] = new_line
            return True

    @classmethod
    def do_insert(cls, contents, locations, new_contents, new_locations, target_dest, target_orig):
        d_f, d_t, d_i = target_dest # file name, "_inter_line", interline index
        o_f, o_t, o_i = target_orig # file name, "line", line index
        assert d_t == '_inter_line'
        assert o_t == 'line'
        new_contents[d_f].insert(new_locations[d_f][d_t][d_i],
                                 contents[o_f][locations[o_f][o_t][o_i]])
        # fix locations
        n = len(contents[d_f])
        for i in range(d_i, n+1):
            new_locations[d_f][d_t][i] += 1
        for i in range(d_i, n):
            new_locations[o_f][o_t][i] += 1
        return True

    @classmethod
    def do_delete(cls, contents, locations, new_contents, new_locations, target):
        d_f, d_t, d_i = target # file name, "line", interline index
        assert d_t == 'line'
        old_line = new_contents[d_f][new_locations[d_f][d_t][d_i]]
        if old_line is None:
            return False
        else:
            new_contents[d_f][new_locations[d_f][d_t][d_i]] = None
            return True
