import magpie

class PythonStmtDeletion(magpie.xml.StmtDeletion):
    def apply(self, program, new_contents, new_locations):
        engine = program.engines[self.target[0]]
        return (
            engine.do_delete(program.contents, program.locations,
                             new_contents, new_locations,
                             self.target)
            and
            engine.do_set_text(program.contents, program.locations,
                               new_contents, new_locations,
                               self.target, 'pass')
        )

magpie.xml.edits += [PythonStmtDeletion]
