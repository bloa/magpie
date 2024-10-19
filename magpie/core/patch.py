import ast
import re

import magpie.utils


class Patch:
    @staticmethod
    def from_string(s):
        patch = Patch()
        if s == '':
            return patch
        for blob in s.split(' | '):
            m = re.search(r'^(\w+(?:<.*?>)?)\((.+)\)$', blob)
            klass = magpie.utils.edit_from_string(m.group(1))
            args = ast.literal_eval(f'[{m.group(2)}]')
            patch.edits.append(klass(*args))
        if str(patch) != s:
            raise AssertionError
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

    def raw(self):
        return [{
            'type': edit.__class__.__name__,
            'target': edit.target,
            'data': edit.data,
        } for edit in self.edits]
