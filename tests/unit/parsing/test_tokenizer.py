import pytest

from magpie.parsing import tokenize


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
    ('x * 2 < 10 and y == 1', [
        ('VAR', 'x'),
        ('OP', '*'),
        ('NUMBER', 2),
        ('OP', '<'),
        ('NUMBER', 10),
        ('OP', 'and'),
        ('VAR', 'y'),
        ('OP', '=='),
        ('NUMBER', 1),
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
    ('!(2 * x < 10 or y == 1)', [
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
        ('NUMBER', 1),
        ('RPAREN', ')'),
    ]),
    ('x > 0 iif y == "foo"', [
        ('VAR', 'x'),
        ('OP', '>'),
        ('NUMBER', 0),
        ('OP', 'iif'),
        ('VAR', 'y'),
        ('OP', '=='),
        ('STRING', 'foo'),
    ]),
    ('1*x + 2y + 3', [
        ('NUMBER', 1),
        ('OP', '*'),
        ('VAR', 'x'),
        ('OP', '+'),
        ('NUMBER', 2),
        ('VAR', 'y'),
        ('OP', '+'),
        ('NUMBER', 3),
    ]),
    ('3.14 * r ** 2', [
        ('NUMBER', 3.14),
        ('OP', '*'),
        ('VAR', 'r'),
        ('OP', '**'),
        ('NUMBER', 2),
    ]),
])
def test_tokenize(expr, expected):
    assert tokens_of(expr) == expected

@pytest.mark.parametrize(('expr', 'expected'), [
    ('-foo', [
        ('OP', '-'),
        ('VAR', 'foo'),
    ]),
    ('foo-1', [
        ('VAR', 'foo-1'),
    ]),
    ('foo - 1', [
        ('VAR', 'foo'),
        ('OP', '-'),
        ('NUMBER', 1),
    ]),
    ('foo--', [
        ('VAR', 'foo--'),
    ]),
    ('foo- - 1', [
        ('VAR', 'foo-'),
        ('OP', '-'),
        ('NUMBER', 1),
    ]),
])
def test_tokenize_hypens(expr, expected):
    assert tokens_of(expr) == expected

