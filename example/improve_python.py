import argparse
import random
import re

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
    def create_edit(self, patch=None):
        operator = random.choice(self.possible_edits)
        return operator.create(self)

    def compute_fitness(self, result, return_code, stdout, stderr, elapsed_time):
        m = re.findall("runtime: ([0-9.]+)", stdout)
        if len(m) > 0:
            runtime = m[0]
            failed = re.findall("([0-9]+) failed", stdout)
            pass_all = len(failed) == 0
            if pass_all:
                result.fitness = round(float(runtime), 3)
            else:
                result.status = 'PARSE_ERROR'
        else:
            result.status = 'PARSE_ERROR'

class MyLineProgram(LineProgram, MyProgram):
    def setup(self, config={}):
        self.target_files = ["triangle.py"]
        self.test_command = "pytest -s test_triangle.py"
        self.possible_edits = [LineReplacement, LineInsertion, LineDeletion]

class MyTreeProgram(TreeProgram, MyProgram):
    def setup(self, config={}):
        self.target_files = ["triangle.py"]
        self.test_command = "pytest -s test_triangle.py"
        self.possible_edits = [StmtReplacement, StmtInsertion, StmtDeletion]


# ================================================================================
# Main function
# ================================================================================

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='PYGGI Improvement Example')
    parser.add_argument('--mode', type=str, default='tree')
    parser.add_argument('--epoch', type=int, default=30,
        help='total epoch(default: 30)')
    parser.add_argument('--iter', type=int, default=100,
        help='total iterations per epoch(default: 100)')
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
    protocol.search.stop['fitness'] = 0.05
    protocol.search.stop['steps'] = args.iter
    protocol.program = program_klass('../sample/Triangle_fast_python')

    # run experiments
    protocol.run()
