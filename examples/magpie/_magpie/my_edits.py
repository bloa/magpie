import magpie


class PythonStmtDeletion(magpie.models.xml.SrcmlStmtDeletion):
    def apply(self, ref, variant):
        model = variant.models[self.target[0]]
        return all([
            model.do_delete(self.target),
            model.do_set_text(self.target, 'pass'),
        ])

magpie.utils.known_edits += [PythonStmtDeletion]
