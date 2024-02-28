class Patch:
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
            'data': edit.data
        } for edit in self.edits]
