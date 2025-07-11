from collections import namedtuple


## Node Classes

class Expr:
    def evaluate(self, context):
        raise NotImplementedError

    def visit(self, visitor):
        visitor(self)

class Literal(Expr):
    def __init__(self, value):
        self.value = value

    def evaluate(self, context):
        return self.value

class ListLiteral(Expr):
    def __init__(self, values):
        self.values = values

    def evaluate(self, context):
        return [value.evaluate(context) for value in self.values]

    def visit(self, visitor):
        visitor(self)
        for value in self.values:
            value.visit(visitor)

class Variable(Expr):
    def __init__(self, name):
        self.name = name

    def evaluate(self, context):
        return context[self.name]

class UnaryOp(Expr):
    def __init__(self, op, right):
        self.op = op
        self.right = right

    def evaluate(self, context):
        val = self.right.evaluate(context)
        if self.op == '-': return -val
        if self.op == 'not': return not val
        msg = f'Unknown unary operator: {self.op}'
        raise ValueError(msg)

    def visit(self, visitor):
        visitor(self)
        self.right.visit(visitor)

class BinaryOp(Expr):
    def __init__(self, op, left, right):
        self.op = op
        self.left = left
        self.right = right

    def evaluate(self, context):
        lval = self.left.evaluate(context)
        rval = self.right.evaluate(context)
        if self.op == '+': return lval + rval
        if self.op == '-': return lval - rval
        if self.op == '*': return lval * rval
        if self.op == '<': return lval < rval
        if self.op == '>': return lval > rval
        if self.op == '/': return lval / rval
        if self.op == '==': return lval == rval
        if self.op == '!=': return lval != rval
        if self.op == '<=': return lval <= rval
        if self.op == '>=': return lval >= rval
        if self.op == '**': return lval ** rval
        if self.op == 'and': return lval and rval
        if self.op == 'or': return lval or rval
        if self.op == 'in': return lval in rval
        if self.op == 'not in': return lval not in rval
        msg = f'Unknown binary operator: {self.op}'
        raise ValueError(msg)

    def visit(self, visitor):
        visitor(self)
        self.left.visit(visitor)
        self.right.visit(visitor)


# Tokenizer

Token = namedtuple('Token', ['type', 'value'])

KEYWORDS = {'and', 'or', 'not', 'in'}
MULTI_CHAR_OPS = {'==', '!=', '<=', '>=', '**'}
SINGLE_CHAR_OPS = {'+', '-', '*', '/', '<', '>', '!', '='}
IDENTIFIERS_CHARS = {'_', '$', '@'}

def tokenize(s):
    tokens = []
    i = 0
    while i < len(s):
        c = s[i]

        if c.isspace():
            i += 1
            continue

        # numbers
        if c.isdigit():
            start = i
            has_dot = False
            while i < len(s) and (s[i].isdigit() or (s[i] == '.' and not has_dot)):
                if s[i] == '.':
                    has_dot = True
                i += 1
            num = s[start:i]
            value = float(num) if '.' in num else int(num)
            tokens.append(Token('NUMBER', value))

        # string literals
        elif c in ('"', "'"):
            quote = c
            i += 1
            start = i
            while i < len(s) and s[i] != quote:
                if s[i] == '\\':
                    i += 2  # skip escaped char
                else:
                    i += 1
            if i >= len(s):
                msg = 'Unterminated string literal'
                raise SyntaxError(msg)
            raw = s[start:i]
            tokens.append(Token('STRING', raw))
            i += 1  # skip closing quote

        # identifiers and keywords
        elif c.isidentifier() or c in IDENTIFIERS_CHARS:
            start = i
            while i < len(s) and (s[i].isalnum() or s[i] in IDENTIFIERS_CHARS):
                i += 1
            word = s[start:i]
            if word in KEYWORDS:
                tokens.append(Token('OP', word))
            elif word in {'True', 'False', 'None'}:
                tmp = {'True': True, 'False': False, 'None': None}
                tokens.append(Token('LITERAL', tmp[word]))
            else:
                tokens.append(Token('VAR', word))

        # lists and parentheses
        elif c in {'[', ',', ']', '(', ')'}:
            tmp = {'[': 'LBRACK', ',': 'COMMA', ']': 'RBRACK', '(': 'LPAREN', ')': 'RPAREN'}
            tokens.append(Token(tmp[c], c))
            i += 1

        # operators
        elif c in SINGLE_CHAR_OPS:
            next_two = s[i:i+2]
            if next_two in MULTI_CHAR_OPS:
                tokens.append(Token('OP', next_two))
                i += 2
            elif c == '!':
                tokens.append(Token('OP', 'not'))
                i += 1
            elif c == '=': # only valid through "=="
                msg = f'Invalid assignment operator: {c}'
                raise SyntaxError(msg)
            else:
                tokens.append(Token('OP', c))
                i += 1

        else:
            msg = f'Unexpected character: {c}'
            raise SyntaxError(msg)

    # post-process
    merged = []
    i = 0
    while i < len(tokens):
        if i + 1 < len(tokens) and tokens[i].type == 'OP' and tokens[i].value == 'not' and tokens[i+1].type == 'OP' and tokens[i+1].value == 'in':
            merged.append(Token('OP', 'not in'))
            i += 2
        else:
            merged.append(tokens[i])
            i += 1

    return merged


## Parser

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def current(self):
        return self.tokens[self.pos] if self.pos < len(self.tokens) else None

    def match(self, *types_and_values):
        token = self.current()
        if token and any(token.type == typ and (val is None or token.value == val) for typ, val in types_and_values):
            self.pos += 1
            return token
        return None

    def expect(self, typ, val=None):
        token = self.match((typ, val))
        if token:
            return token
        msg = f'Expected {typ} {val}, got {self.current()}'
        raise SyntaxError(msg)

    def parse(self):
        expr = self.parse_or()
        if self.current() is not None:
            msg = f'Unexpected token(s) at end ({self.tokens[self.pos:]})'
            raise SyntaxError(msg)
        return expr

    def parse_or(self):
        expr = self.parse_and()
        while self.match(('OP', 'or')):
            right = self.parse_and()
            expr = BinaryOp('or', expr, right)
        return expr

    def parse_and(self):
        expr = self.parse_not()
        while self.match(('OP', 'and')):
            right = self.parse_not()
            expr = BinaryOp('and', expr, right)
        return expr

    def parse_not(self):
        if self.match(('OP', 'not')):
            return UnaryOp('not', self.parse_not())
        return self.parse_compare()

    def parse_compare(self):
        expr = self.parse_add()
        while True:
            token = self.match(
                ('OP', '=='), ('OP', '!='), ('OP', '<'), ('OP', '<='),
                ('OP', '>'), ('OP', '>='), ('OP', 'in'), ('OP', 'not in'),
            )
            if not token:
                break
            right = self.parse_add()
            expr = BinaryOp(token.value, expr, right)
        return expr

    def parse_add(self):
        expr = self.parse_mul()
        while True:
            token = self.match(('OP', '+'), ('OP', '-'))
            if not token: break
            right = self.parse_mul()
            expr = BinaryOp(token.value, expr, right)
        return expr

    def parse_mul(self):
        expr = self.parse_unary()
        while True:
            token = self.match(('OP', '*'), ('OP', '/'))
            if not token: break
            right = self.parse_unary()
            expr = BinaryOp(token.value, expr, right)
        return expr

    def parse_unary(self):
        if self.match(('OP', '-')):
            return UnaryOp('-', self.parse_unary())
        return self.parse_power()

    def parse_power(self):
        expr = self.parse_atom()
        while self.match(('OP', '**')):
            right = self.parse_unary()
            expr = BinaryOp('**', expr, right)
        return expr

    def parse_atom(self):
        token = self.current()
        if token is None:
            msg = 'Unexpected end of input'
            raise SyntaxError(msg)

        if token.type in {'NUMBER', 'STRING', 'LITERAL'}:
            self.pos += 1
            return Literal(token.value)
        if token.type == 'VAR':
            self.pos += 1
            return Variable(token.value)
        if token.type == 'LBRACK':
            self.pos += 1
            items = []
            if not self.match(('RBRACK', ']')):
                while True:
                    items.append(self.parse_or())
                    if self.match(('RBRACK', ']')):
                        break
                    self.expect('COMMA')
            return ListLiteral(items)
        if token.type == 'LPAREN':
            self.pos += 1
            expr = self.parse_or()
            self.expect('RPAREN')
            return expr

        msg = f'Unexpected token {token}'
        raise SyntaxError(msg)

def parse(tokens):
    return Parser(tokens).parse()


## API

class ExprTree:
    def __init__(self, s):
        tokens = tokenize(s)
        self.root = parse(tokens)
        self.variables = self._find_variables(self.root)
        self._check_for_obvious_typing_errors(self.root)

    def evaluate(self, context):
        return self.root.evaluate(context)

    def rename(self, old, new):
        if old not in self.variables:
            return
        def visitor(node):
            if isinstance(node, Variable) and node.name == old:
                node.name = new
        self.root.visit(visitor)
        self.variables = {new if var == old else var for var in self.variables}

    def _find_variables(self, tree):
        variables = set()
        def visitor(node):
            nonlocal variables
            if isinstance(node, Variable):
                variables.add(node.name)
        self.root.visit(visitor)
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
            return node.op in {'==', '!=', '<=', '>=', '<', '>', 'and', 'or', 'in', 'not in'}
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
                if node.op in {'+', '-', '*', '/', '<=', '>=', '<', '>'} and (bool_left or bool_right):
                    raise TypeError(self.BOOL_FOUND_BUT_NUM_EXPECTED)
                if node.op in {'and', 'or'} and (math_left or math_right):
                    raise TypeError(self.NUM_FOUND_BUT_BOOL_EXPECTED)
                if node.op in {'in', 'not in'} and not isinstance(node.right, ListLiteral):
                    msg = 'List literal was expected'
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
            msg = f'Expression evaluated to "{result}", but a numeric value was expected.'
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
            msg = 'Expression evaluated to a numeric value, but a Boolean value was expected.'
            raise TypeError(msg)
        return result
