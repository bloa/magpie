import pathlib

import magpie.utils

from .abstract_model import AbstractLineModel


class LineModel(AbstractLineModel):
    def init_contents(self):
        with pathlib.Path(self.filename).open('r') as target_file:
            lines = list(map(str.rstrip, target_file.readlines()))

        n = len(lines)
        self.contents = lines
        self.locations = {
            'line': list(range(n)),
            '_inter_line': list(range(n+1)),
        }

    def dump(self):
        return ''.join(s + '\n' for s in self.contents if s is not None)

    def show_location(self, target_type, target_loc):
        out = '(unsupported target_type)'
        if target_type == 'line':
            out = f'{target_loc}:{self.contents[self.locations[target_type][target_loc]]}'
        elif target_type == '_inter_line':
            if target_loc == 0:
                out = '0=before initial line'
            else:
                out = f'{target_loc}=after:{self.contents[self.locations[target_type][target_loc-1]]}'
        return out

    def do_replace(self, ref_model, target_dest, target_orig):
        d_f, d_t, d_i = target_dest # file name, "line", line index
        o_f, o_t, o_i = target_orig # file name, "line", line index
        if (d_f != self.filename or
            o_f != ref_model.filename or
            d_t != 'line' or
            o_t != 'line'):
            raise ValueError
        old_line = self.contents[self.locations[d_t][d_i]]
        new_line = ref_model.contents[ref_model.locations[o_t][o_i]]
        if (new_line is None or
            new_line == old_line):
            return False
        self.contents[self.locations[d_t][d_i]] = new_line
        return True

    def do_insert(self, ref_model, target_dest, target_orig):
        d_f, d_t, d_i = target_dest # file name, "_inter_line", interline index
        o_f, o_t, o_i = target_orig # file name, "line", line index
        if (d_f != self.filename or
            o_f != ref_model.filename or
            d_t != '_inter_line' or
            o_t != 'line'):
            raise ValueError
        new_line = ref_model.contents[ref_model.locations[o_t][o_i]]
        self.contents.insert(self.locations[d_t][d_i], new_line)
        # fix locations
        for i in range(d_i, len(self.locations['line'])):
            self.locations['line'][i] += 1
        for i in range(d_i, len(self.locations['_inter_line'])):
            self.locations['_inter_line'][i] += 1
        return True

    def do_delete(self, target):
        d_f, d_t, d_i = target # file name, "line", interline index
        if (d_f != self.filename or
            d_t != 'line'):
            raise ValueError
        old_line = self.contents[self.locations[d_t][d_i]]
        if old_line is None:
            return False
        self.contents[self.locations[d_t][d_i]] = None
        return True

magpie.utils.known_models.append(LineModel)
