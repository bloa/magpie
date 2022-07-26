import os
import copy

class Patch:
    def __init__(self, edits=[]):
        self.edits = [edit for edit in edits]

    def __str__(self):
        return ' | '.join(map(str, self.edits))

    def __eq__(self, other):
        return isinstance(other, Patch) and self.edits == other.edits

    def __hash__(self):
        return hash(str(self))

    def raw(self):
        return [{
            'type': edit.__class__.__name__,
            'target': edit.target,
            'data': edit.data
        } for edit in self.edits]
