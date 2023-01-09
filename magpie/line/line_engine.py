from . import AbstractLineEngine


class LineEngine(AbstractLineEngine):
    @classmethod
    def get_contents(cls, file_path):
        with open(file_path, 'r') as target_file:
            return list(map(str.rstrip, target_file.readlines()))

    @classmethod
    def get_locations(cls, file_contents):
        n = len(file_contents)
        return {'line': list(range(n)), '_inter_line': list(range(n+1))}

    @classmethod
    def dump(cls, file_contents):
        return ''.join(s + '\n' for s in file_contents if s is not None)

    @classmethod
    def show_location(cls, contents, locations, target_file, target_type, target_loc):
        out = '(unsupported target_type)'
        if target_type == 'line':
            out = '{}:{}'.format(target_loc, contents[target_file][locations[target_file][target_type][target_loc]])
        elif target_type == '_inter_line':
            if target_loc == 0:
                out = '0=before initial line'
            else:
                out = '{}=after:{}'.format(target_loc, contents[target_file][locations[target_file][target_type][target_loc-1]])
        return out

    @classmethod
    def do_replace(cls, contents, locations, new_contents, new_locations, target_dest, target_orig):
        d_f, d_t, d_i = target_dest # file name, "line", line index
        o_f, o_t, o_i = target_orig # file name, "line", line index
        if not (d_t == o_t == 'line'):
            raise ValueError()
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
        if d_t != '_inter_line' or o_t != 'line':
            raise ValueError()
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
        if d_t != 'line':
            raise ValueError()
        old_line = new_contents[d_f][new_locations[d_f][d_t][d_i]]
        if old_line is None:
            return False
        else:
            new_contents[d_f][new_locations[d_f][d_t][d_i]] = None
            return True
