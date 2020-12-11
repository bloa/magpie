import argparse
import random

from pyggi.base import Patch, AbstractProgram
from pyggi.tree import TreeProgram, SrcmlEngine
from pyggi.tree import StmtReplacement, StmtInsertion, StmtDeletion
from pyggi.tree import ComparisonOperatorSetting
from pyggi.algo import FirstImprovement

# ================================================================================
# Experimental protocol
# ================================================================================

from improve_java import ExpProtocol


# ================================================================================
# Target software specifics
# ================================================================================

class MySrcmlEngine(SrcmlEngine):
    TAG_RENAME = {
        'stmt': {'break', 'continue', 'decl_stmt', 'do', 'expr_stmt', 'for', 'goto', 'if', 'return', 'switch', 'while'},
        'operator_comp': {'operator_comp'},
    }
    TAG_FOCUS = { t for tl in TAG_RENAME.values() for t in tl }
    PROCESS_LITERALS = False
    PROCESS_OPERATORS = True

class MyProgram(TreeProgram):
    def setup(self, config):
        self.target_files = ["Triangle.java.xml"]
        self.test_command = "./run.sh"
        self.possible_edits = [StmtReplacement, StmtInsertion, StmtDeletion, ComparisonOperatorSetting]

    def create_edit(self, patch=None):
        if len(self.possible_edits) == 0:
            raise AssertionError('Impossible to create new edits')
        operator = random.choice(self.possible_edits)
        for _ in range(1000):
            edit = operator.create(self)
            if self.would_edit_be_valid(edit):
                return edit
        raise AssertionError('Failed to create a valid edit of type {}'.format(operator))

    def would_edit_be_valid(self, edit):
        if isinstance(edit, ComparisonOperatorSetting):
            target_file, target_point = edit.target
            target_tag = self.contents[target_file].find(self.modification_points[target_file][target_point]).tag
            return target_tag == 'operator_comp'
        elif isinstance(edit, StmtDeletion):
            target_file, target_point = edit.target
            target_tag = self.contents[target_file].find(self.modification_points[target_file][target_point]).tag
            return target_tag == 'stmt'
        elif any(isinstance(edit, c) for c in [StmtReplacement, StmtInsertion, StmtDeletion]):
            target_file, target_point = edit.target
            ingredient_file, ingredient_point = edit.ingredient
            target_tag = self.contents[target_file].find(self.modification_points[target_file][target_point]).tag
            ingredient_tag = self.contents[ingredient_file].find(self.modification_points[ingredient_file][ingredient_point]).tag
            return target_tag == ingredient_tag == 'stmt'
        return True

    @classmethod
    def get_engine(cls, file_name):
        return MySrcmlEngine


# ================================================================================
# Main function
# ================================================================================

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='PYGGI Bug Repair Example')
    parser.add_argument('--epoch', type=int, default=30,
        help='total epoch(default: 30)')
    parser.add_argument('--iter', type=int, default=10000,
        help='total iterations per epoch(default: 10000)')
    args = parser.parse_args()

    # setup protocol
    protocol = ExpProtocol()
    protocol.nb_epoch = args.epoch
    protocol.search = FirstImprovement()
    protocol.search.stop['fitness'] = 0
    protocol.search.stop['steps'] = args.iter
    protocol.program = MyProgram('../sample/Triangle_bug2_java')

    # run experiments
    protocol.run()
