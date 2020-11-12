import argparse
import random

from pyggi.base import Patch, AbstractProgram
from pyggi.line import LineProgram
from pyggi.line import LineReplacement, LineInsertion, LineDeletion
from pyggi.tree import TreeProgram
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
    def load_config(self, path, config):
        self.target_files = ["triangle.py"]
        self.test_command = "pytest -s test_triangle.py"

    def create_edit(self, patch=None):
        operator = random.choice(self.possible_edits)
        return operator.create(self)

    def compute_fitness(self, result, return_code, stdout, stderr, elapsed_time):
        import re
        m = re.findall("runtime: ([0-9.]+)", stdout)
        if len(m) > 0:
            runtime = m[0]
            failed = re.findall("([0-9]+) failed", stdout)
            pass_all = len(failed) == 0
            failed = int(failed[0]) if not pass_all else 0
            result.fitness = failed
        else:
            result.status = 'PARSE_ERROR'

class MyLineProgram(LineProgram, MyProgram):
    def setup(self):
        self.possible_edits = [LineReplacement, LineInsertion, LineDeletion]

class MyTreeProgram(TreeProgram, MyProgram):
    def setup(self):
        self.possible_edits = [StmtReplacement, StmtInsertion, StmtDeletion]

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
    protocol.program = program_klass('../sample/Triangle_bug_python')

    # run experiments
    protocol.run()
