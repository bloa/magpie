from .nodes import (
    BinaryOp,
    Literal,
    ListLiteral,
    UnaryOp,
    Variable,
)


class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def current(self):
        return self.tokens[self.pos] if self.pos < len(self.tokens) else None

    def accept(self, *patterns):
        if token := self.current():
            for typ, value in patterns:
                if token.type == typ and (value is None or token.value == value):
                    self.pos += 1
                    return token
        return None

    def expect(self, *patterns):
        token = self.accept(*patterns)
        if token:
            return token
        msg = f'Unexpected token: expected {patterns}, got {self.current()}'
        raise SyntaxError(msg)

    def assert_end(self):
        if self.current() is not None:
            msg = f'Unexpected token(s) at end ({self.tokens[self.pos:]})'
            raise SyntaxError(msg)

    def assert_not_end(self):
        if self.current() is None:
            msg = 'Unexpected end of input'
            raise SyntaxError(msg)

    def parse(self):
        if expr := self.parse_logic():
            self.assert_end()
            return expr

        msg = f'Unable to parse expression: {self.tokens}'
        raise SyntaxError(msg)

    def parse_logic(self):
        self.assert_not_end()

        expr_left = self.parse_comparison()
        while token := self.accept(
                    ('OP', 'and'),
                    ('OP', 'or'),
                    ('OP', 'xor'),
                    ('OP', 'if'),
                    ('OP', 'iif'),
                    ('OP', 'in'),
                    ('OP', 'not in'),
        ):
            expr_left = BinaryOp(token.value, expr_left, self.parse_comparison())
        return expr_left

    def parse_comparison(self):
        self.assert_not_end()

        expr_left = self.parse_low()
        while token := self.accept(
                    ('OP', '<='),
                    ('OP', '<'),
                    ('OP', '=='),
                    ('OP', '!='),
                    ('OP', '>'),
                    ('OP', '>='),
        ):
            expr_left = BinaryOp(token.value, expr_left, self.parse_low())
        return expr_left

    def parse_low(self):
        self.assert_not_end()

        expr_left = self.parse_high()
        while token := self.accept(
                    ('OP', '+'),
                    ('OP', '-'),
        ):
            expr_left = BinaryOp(token.value, expr_left, self.parse_high())
        return expr_left

    def parse_high(self):
        self.assert_not_end()

        expr_left = self.parse_atom()
        while token := self.accept(
                ('OP', '*'),
                ('OP', '/'),
                ('OP', '**'),
                ('VAR', None),
        ):
            if token.type == 'OP':
                expr_left = BinaryOp(token.value, expr_left, self.parse_atom())
            elif isinstance(expr_left, Literal):
                expr_left = BinaryOp('*', expr_left, Variable(token.value))
            elif isinstance(expr_left, UnaryOp):
                expr_left = BinaryOp('*', expr_left, Variable(token.value))
            else:
                msg = f'Unexpected token {token} after {expr_left}'
                raise SyntaxError(msg)
        return expr_left

    def parse_atom(self):
        self.assert_not_end()

        if token := self.accept(
                ('OP', 'not'),
                ('OP', '-'),
        ):
            return UnaryOp(token.value, self.parse_atom())
        if token := self.accept(
                ('BOOL', None),
                ('NUMBER', None),
        ):
            return Literal(token.value)
        if token := self.accept(('LBRACK', None)):
            exprs = [self.parse_logic()]
            while self.accept(('COMMA', None)):
                exprs.append(self.parse_logic())
            self.expect(('RBRACK', None))
            return ListLiteral(exprs)
        if token := self.accept(('VAR', None)):
            return Variable(token.value)
        if token := self.accept(('LPAREN', None)):
            expr = self.parse_logic()
            self.expect(('RPAREN', None))
            return expr

        msg = f'Unexpected token {self.current()}'
        raise SyntaxError(msg)
