import argparse
import random

from pyggi.base import Patch, AbstractProgram
from pyggi.line import LineProgram
from pyggi.line import LineReplacement, LineInsertion, LineDeletion
from pyggi.tree import SrcmlEngine
from pyggi.tree import StmtReplacement, StmtInsertion, StmtDeletion
from pyggi.algo import FirstImprovement

# ================================================================================
# Experimental protocol
# ================================================================================

from improve_java import ExpProtocol


# ================================================================================
# Target software specifics
# ================================================================================

class MyProgram(AbstractProgram):
    def create_edit(self, patch=None):
        operator = random.choice(self.possible_edits)
        return operator.create(self)

class MyLineProgram(LineProgram, MyProgram):
    def setup(self, config):
        self.target_files = ["Triangle.java"]
        self.test_command = "./run.sh"
        self.possible_edits = [LineReplacement, LineInsertion, LineDeletion]

class MySrcmlEngine(SrcmlEngine):
    TAG_RENAME = {
        'stmt': {'break', 'continue', 'decl_stmt', 'do', 'expr_stmt', 'for', 'goto', 'if', 'return', 'switch', 'while'},
    }
    TAG_FOCUS = { t for tl in TAG_RENAME.values() for t in tl }
    PROCESS_LITERALS = False
    PROCESS_OPERATORS = False

class MyTreeProgram(MyProgram):
    def setup(self, config):
        self.target_files = ["Triangle.java.xml"]
        self.test_command = "./run.sh"
        self.possible_edits = [StmtReplacement, StmtInsertion, StmtDeletion]

    @classmethod
    def get_engine(cls, file_name):
        return MySrcmlEngine


# ================================================================================
# Main function
# ================================================================================

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='PYGGI Bug Repair Example')
    parser.add_argument('--mode', type=str, default='line')
    parser.add_argument('--epoch', type=int, default=30,
        help='total epoch(default: 30)')
    parser.add_argument('--iter', type=int, default=10000,
        help='total iterations per epoch(default: 10000)')
    args = parser.parse_args()

    if args.mode == 'line':
        program_klass = MyLineProgram
    elif args.mode == 'tree':
        program_klass = MyTreeProgram
    else:
        raise RuntimeError('Invalid mode: {}'.format(args.mode))

    # setup protocol
    protocol = ExpProtocol()
    protocol.nb_epoch = args.epoch
    protocol.search = FirstImprovement()
    protocol.search.stop['fitness'] = 0
    protocol.search.stop['steps'] = args.iter
    protocol.program = program_klass('../sample/Triangle_bug_java')

    # run experiments
    protocol.run()
