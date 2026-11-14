import ast
import re

import magpie.utils


class Patch:
    @staticmethod
    def from_string(s):
        patch = Patch()
        s = s.strip()
        if not s:
            return patch
        for blob in s.split(' | '):
            m = re.fullmatch(r'\s*(\w+(?:<.*?>)?)\((.+)\)\s*', blob)
            if not m:
                msg = f'Invalid patch edit: {blob!r}'
                raise ValueError(msg)
            try:
                klass = magpie.utils.edit_from_string(m.group(1))
                args = ast.literal_eval(f'[{m.group(2)}]')
                patch.edits.append(klass(*args))
            except (ValueError, SyntaxError, TypeError) as e:
                msg = f'Failed to parse patch edit {blob!r}: {e}'
                raise ValueError(msg) from e
        return patch

    def __init__(self, edits=None):
        self.edits = list(edits or [])

    def __str__(self):
        return ' | '.join(map(str, self.edits))

    def __eq__(self, other):
        try:
            return self.edits == other.edits
        except AttributeError:
            return False

    def __hash__(self):
        return hash(str(self))

    def apply(self, ref, variant):
        for edit in self.edits:
            edit.apply(ref, variant)

    def raw(self):
        return [{
            'type': edit.__class__.__name__,
            'target': edit.target,
            'data': edit.data,
        } for edit in self.edits]
