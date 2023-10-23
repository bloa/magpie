class Edit:
    def __init__(self, target, *args):
        self.target = target
        self.data = list(args)

    def apply(self, software, new_contents, new_locations):
        pass

    def __eq__(self, other):
        return (
            self.__class__ == other.__class__ and
            self.target == other.target and
            self.data == other.data
        )

    def __hash__(self):
        return hash(str(self))

    def __str__(self):
        return '{}({}{})'.format(
            self.__class__.__name__,
            repr(self.target),
            ''.join([', {}'.format(repr(d)) for d in self.data])
        )
