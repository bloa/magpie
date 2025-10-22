from .nodes import (
    BinaryOp,
    Literal,
    ListLiteral,
    UnaryOp,
    Variable,
)
from .parser import Parser
from .tokenizer import tokenize


class ExprTree:
    @classmethod
    def from_string(cls, s):
        tokens = tokenize(s)
        return cls(Parser(tokens).parse())

    def __init__(self, root):
        self.root = root
        self.variables = self._find_variables(self.root)
        self._check_for_obvious_typing_errors(self.root)

    def __str__(self):
        return str(self.root)

    def evaluate(self, context):
        return self.root.evaluate(context)

    def rename(self, old, new):
        if old not in self.variables:
            return
        def visitor(node):
            if isinstance(node, Variable) and node.name == old:
                node.name = new
        self.root.visit(visitor)
        self.variables = [new if var == old else var for var in self.variables]

    def replace(self, old, new):
        def visitor(node):
            if str(node) == str(old):
                return new
            return node
        self.root = self.root.rewrite(visitor)
        self.variables = self._find_variables(self.root)

    def _find_variables(self, root):
        variables = []
        def visitor(node):
            nonlocal variables
            if isinstance(node, Variable) and node.name not in variables:
                variables.append(node.name)
        root.visit(visitor)
        return variables

    def _is_obvious_math(self, node):
        if isinstance(node, Literal):
            return isinstance(node.value, (int, float)) and not isinstance(node.value, bool)
        if isinstance(node, BinaryOp):
            return node.op in {'+', '-', '*', '/', '**'}
        if isinstance(node, UnaryOp):
            return node.op == '-'
        return False

    def _is_obvious_bool(self, node):
        if isinstance(node, Literal):
            return isinstance(node.value, bool)
        if isinstance(node, BinaryOp):
            return node.op in {'==', '!=', '<=', '>=', '<', '>', 'and', 'or', 'xor', 'if', 'iff', 'in', 'not in'}
        if isinstance(node, UnaryOp):
            return node.op == 'not'
        return False

    BOOL_FOUND_BUT_NUM_EXPECTED = 'Expression appears to be Boolean, but a numeric expression was expected'
    NUM_FOUND_BUT_BOOL_EXPECTED = 'Expression appears to be numeric, but a Boolean expression was expected'

    def _check_for_obvious_typing_errors(self, node):
        def visitor(node):
            if isinstance(node, BinaryOp):
                math_left = self._is_obvious_math(node.left)
                math_right = self._is_obvious_math(node.right)
                bool_left = self._is_obvious_bool(node.left)
                bool_right = self._is_obvious_bool(node.right)
                if node.op in {'+', '-', '*', '**', '/', '<=', '>=', '<', '>'} and (bool_left or bool_right):
                    raise TypeError(self.BOOL_FOUND_BUT_NUM_EXPECTED)
                if node.op in {'and', 'or'} and (math_left or math_right):
                    raise TypeError(self.NUM_FOUND_BUT_BOOL_EXPECTED)
                if node.op in {'in', 'not in'} and not isinstance(node.right, ListLiteral):
                    msg = 'A list literal was expected'
                    raise TypeError(msg)
            elif isinstance(node, UnaryOp):
                math_right = self._is_obvious_math(node.right)
                bool_right = self._is_obvious_bool(node.right)
                if node.op == '-' and bool_right:
                    raise TypeError(self.BOOL_FOUND_BUT_NUM_EXPECTED)
                if node.op == 'not' and math_right:
                    raise TypeError(self.NUM_FOUND_BUT_BOOL_EXPECTED)
        node.visit(visitor)

class MathTree(ExprTree):
    def __init__(self, s):
        super().__init__(s)
        def visitor(node):
            if self._is_obvious_bool(node):
                msg = 'Invalid Boolean operator in numerical expression'
                raise TypeError(msg)
        self.root.visit(visitor)

    def evaluate(self, context):
        result = super().evaluate(context)
        if not isinstance(result, (int, float)):
            msg = f'Expression evaluated to "{result}", but a numeric value was expected'
            raise TypeError(msg)
        return result

class BoolTree(ExprTree):
    def __init__(self, s):
        super().__init__(s)
        if self._is_obvious_math(self.root):
            raise TypeError(self.NUM_FOUND_BUT_BOOL_EXPECTED)

    def evaluate(self, context):
        result = super().evaluate(context)
        if not isinstance(result, bool):
            msg = 'Expression evaluated to a numeric value, but a Boolean value was expected'
            raise TypeError(msg)
        return result
