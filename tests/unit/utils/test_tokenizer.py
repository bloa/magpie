import pytest

from magpie.utils.expr_tree import tokenize


def tokens_of(s):
    return [(t.type, t.value) for t in tokenize(s)]

@pytest.mark.parametrize(('expr', 'expected'), [
    ('2 + x * 3', [
        ('NUMBER', 2),
        ('OP', '+'),
        ('VAR', 'x'),
        ('OP', '*'),
        ('NUMBER', 3),
    ]),
    ('x * 2 < 10 and y == "foo"', [
        ('VAR', 'x'),
        ('OP', '*'),
        ('NUMBER', 2),
        ('OP', '<'),
        ('NUMBER', 10),
        ('OP', 'and'),
        ('VAR', 'y'),
        ('OP', '=='),
        ('STRING', 'foo'),
    ]),
    ('x not in [1, 2]', [
        ('VAR', 'x'),
        ('OP', 'not in'),
        ('LBRACK', '['),
        ('NUMBER', 1),
        ('COMMA', ','),
        ('NUMBER', 2),
        ('RBRACK', ']'),
    ]),
    ('!x', [
        ('OP', 'not'),
        ('VAR', 'x'),
    ]),
    ('-(-x)', [
        ('OP', '-'),
        ('LPAREN', '('),
        ('OP', '-'),
        ('VAR', 'x'),
        ('RPAREN', ')'),
    ]),
    ('!(2 * x < 10 or y == "foo")', [
        ('OP', 'not'),
        ('LPAREN', '('),
        ('NUMBER', 2),
        ('OP', '*'),
        ('VAR', 'x'),
        ('OP', '<'),
        ('NUMBER', 10),
        ('OP', 'or'),
        ('VAR', 'y'),
        ('OP', '=='),
        ('STRING', 'foo'),
        ('RPAREN', ')'),
    ]),
    ('x in ["a", "b"]', [
        ('VAR', 'x'),
        ('OP', 'in'),
        ('LBRACK', '['),
        ('STRING', 'a'),
        ('COMMA', ','),
        ('STRING', 'b'),
        ('RBRACK', ']'),
    ]),
    ('3.14 * r ** 2', [
        ('NUMBER', 3.14),
        ('OP', '*'),
        ('VAR', 'r'),
        ('OP', '**'),
        ('NUMBER', 2),
    ]),
    ('x == 1 or (y not in [2, 3] and z == "hello")', [
        ('VAR', 'x'),
        ('OP', '=='),
        ('NUMBER', 1),
        ('OP', 'or'),
        ('LPAREN', '('),
        ('VAR', 'y'),
        ('OP', 'not in'),
        ('LBRACK', '['),
        ('NUMBER', 2),
        ('COMMA', ','),
        ('NUMBER', 3),
        ('RBRACK', ']'),
        ('OP', 'and'),
        ('VAR', 'z'),
        ('OP', '=='),
        ('STRING', 'hello'),
        ('RPAREN', ')'),
    ]),
])
def test_tokenize(expr, expected):
    assert tokens_of(expr) == expected
