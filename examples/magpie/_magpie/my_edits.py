import magpie
from magpie.models.xml import SrcmlStmtDeletion


class PythonStmtDeletion(SrcmlStmtDeletion):
    def apply(self, ref, variant):
        model = variant.models[self.target[0]]
        return all([
            model.do_delete(self.target),
            model.do_set_text(self.target, 'pass'),
        ])

magpie.models.known_edits += [PythonStmtDeletion]
