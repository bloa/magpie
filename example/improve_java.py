import argparse
import copy
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

class ExpProtocol:
    def __init__(self):
        self.nb_epoch = 10
        self.search = None
        self.program = None

    def run(self):
        if self.program is None:
            raise AssertionError('Program not specified')
        if self.search is None:
            raise AssertionError('Search not specified')

        self.search.config['warmup'] = 3
        self.search.program = self.program

        logger = self.program.logger
        result = []
        try:
            for epoch in range(self.nb_epoch):
                logger.info('========== EPOCH {} =========='.format(epoch+1))
                self.search.reset()
                self.search.run()
                r = copy.deepcopy(self.search.report)
                r['diff'] = self.program.diff(r['best_patch'])
                result.append(r)
                logger.info('')
        except KeyboardInterrupt:
            pass

        logger.info('========== REPORT ==========')
        for epoch in range(len(result)):
            logger.info('==== Epoch {} ===='.format(epoch+1))
            logger.info('Termination: {}'.format(result[epoch]['stop']))
            if result[epoch]['best_patch']:
                logger.info('Best fitness: {}'.format(result[epoch]['best_fitness']))
                logger.info('Best patch: {}'.format(result[epoch]['best_patch']))
                logger.info('Diff:\n{}'.format(result[epoch]['diff']))
        self.program.remove_tmp_variant()


# ================================================================================
# Target software specifics
# ================================================================================

class MyProgram(AbstractProgram):
    def create_edit(self, patch=None):
        operator = random.choice(self.possible_edits)
        return operator.create(self)

    def compute_fitness(self, result, return_code, stdout, stderr, elapsed_time):
        try:
            runtime, pass_all = stdout.strip().split(',')
            runtime = float(runtime)
            if not pass_all == 'true':
                result.status = 'PARSE_ERROR'
            else:
                result.fitness = runtime
        except:
            result.status = 'PARSE_ERROR'

class MyLineProgram(LineProgram, MyProgram):
    def setup(self):
        self.possible_edits = [LineReplacement, LineInsertion, LineDeletion]

    def load_config(self, path, config):
        self.target_files = ["Triangle.java"]
        self.test_command = "./run.sh"

class MySrcmlEngine(SrcmlEngine):
    TAG_RENAME = {
        'stmt': {'break', 'continue', 'decl_stmt', 'do', 'expr_stmt', 'for', 'goto', 'if', 'return', 'switch', 'while'},
    }
    TAG_FOCUS = { t for tl in TAG_RENAME.values() for t in tl }
    PROCESS_LITERALS = False
    PROCESS_OPERATORS = False

class MyTreeProgram(MyProgram):
    def setup(self):
        self.possible_edits = [StmtReplacement, StmtInsertion, StmtDeletion]

    def load_config(self, path, config):
        self.target_files = ["Triangle.java.xml"]
        self.test_command = "./run.sh"

    @classmethod
    def get_engine(cls, file_name):
        return MySrcmlEngine


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
    protocol.search.stop['fitness'] = 100
    protocol.search.stop['steps'] = args.iter
    protocol.program = program_klass('../sample/Triangle_fast_java')

    # run experiments
    protocol.run()
