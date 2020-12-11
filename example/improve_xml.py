import argparse
import random

from pyggi.base import Patch, AbstractProgram
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

from improve_java import MyProgram

class MyTreeProgram(TreeProgram, MyProgram):
    def setup(self, config):
        self.target_files = ["Triangle.java.xml"]
        self.test_command = "./run.sh"
        self.possible_edits = [StmtReplacement, StmtInsertion, StmtDeletion]


# ================================================================================
# Main function
# ================================================================================

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='PYGGI Improvement Example')
    parser.add_argument('--epoch', type=int, default=30,
        help='total epoch(default: 30)')
    parser.add_argument('--iter', type=int, default=100,
        help='total iterations per epoch(default: 100)')
    args = parser.parse_args()

    # setup protocol
    protocol = ExpProtocol()
    protocol.nb_epoch = args.epoch
    protocol.search = FirstImprovement()
    protocol.search.stop['fitness'] = 100
    protocol.search.stop['steps'] = args.iter
    protocol.program = MyTreeProgram('../sample/Triangle_fast_xml')

    # run experiments
    protocol.run()
