import magpie
from magpie.models.xml import StmtDeletion


class PythonStmtDeletion(StmtDeletion):
    def apply(self, program, new_contents, new_locations):
        model = program.models[self.target[0]]
        return (
            model.do_delete(program.contents, program.locations,
                            new_contents, new_locations,
                            self.target)
            and
            model.do_set_text(program.contents, program.locations,
                              new_contents, new_locations,
                              self.target, 'pass')
        )

magpie.models.known_edits += [PythonStmtDeletion]
