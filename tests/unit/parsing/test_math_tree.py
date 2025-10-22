import pytest

from magpie.parsing import BoolTree, ExprTree, MathTree


## Syntax errors

@pytest.mark.parametrize(('expr', 'expected'), [
    ('not', SyntaxError),
    ('1 and', SyntaxError),
    ('x y', SyntaxError),
    ('+ 2', SyntaxError),
])
def test_expr_tree_syntax_error(expr, expected):
    with pytest.raises(expected):
        ExprTree.from_string(expr)


## Typing errors

@pytest.mark.parametrize(('expr', 'expected'), [
    ('-True', TypeError),
    ('not 1', TypeError),
    ('1 and 2', TypeError),
    ('1 and (x + y)', TypeError),
    ('1 + (x or y)', TypeError),
    ('1 + (!x)', TypeError),
    ('True ** 2', TypeError),
    ('3 ** False', TypeError),
    ('(x or y) ** (1 + 1)', TypeError),
    ('x in 1', TypeError),
    ('x in y', TypeError),
])
def test_expr_tree_typing_error(expr, expected):
    with pytest.raises(expected):
        ExprTree.from_string(expr)

@pytest.mark.parametrize(('expr', 'expected'), [
    ('True', TypeError),
    ('not x', TypeError),
    ('x < y', TypeError),
    ('x and y', TypeError),
    ('x in [0, 1]', TypeError),
])
def test_math_tree_typing_error(expr, expected):
    with pytest.raises(expected):
        MathTree.from_string(expr)

@pytest.mark.parametrize(('expr', 'expected'), [
    ('1', TypeError),
    ('x + y', TypeError),
])
def test_bool_tree_typing_error(expr, expected):
    with pytest.raises(expected):
        BoolTree.from_string(expr)


## Runtime

@pytest.mark.parametrize(('expr', 'context', 'expected'), [
    ('True', {}, True),
    ('True', {'foo': 0}, True),
    ('1 + 2', {}, 3),
    ('-1 + 2', {}, 1),
    ('-(-1)', {}, 1),
    ('2*x', {'x':3}, 6),
    ('2x', {'x':3}, 6),
    ('2 x1', {'x1':3}, 6),
    ('2x * y', {'x':3, 'y':5}, 30),
    ('-(((-(-(1)))))', {}, -1),
    ('1.2 + 2.5', {}, 3.7),
    ('(2 + x) * y', {'x': 2, 'y': 3}, 12),
    ('2 + x * y', {'x': 2, 'y': 3}, 8),
    ('2 ** -1', {}, 0.5),
    ('2 ** 0', {}, 1),
    ('2 ** 1', {}, 2),
    ('2 ** 3', {}, 8),
    ('foo < 0 or foo >= 10', {'foo': -1}, True),
    ('foo < 0 or foo >= 10', {'foo': 0}, False),
    ('foo < 0 or foo >= 10', {'foo': 4}, False),
    ('foo < 0 or foo >= 10', {'foo': 10}, True),
    ('foo < 0 or foo >= 10', {'foo': 11}, True),
    ('x < y', {'x': 1, 'y': 3}, True),
    ('x < y', {'x': 4, 'y': 3}, False),
    ('x == 1', {'x': 1}, True),
    ('x == 2', {'x': 1}, False),
    ('x in [1, 2]', {'x': 1}, True),
    ('x in [1, 2]', {'x': 0}, False),
    ('x not in [1, 2]', {'x': 0}, True),
    ('not (x in [1, 2])', {'x': 0}, True),
    ('True in [x, y]', {'x': True, 'y': False}, True),
    ('True in [x, y]', {'x': None, 'y': False}, False),
])
def test_expr_tree_runtime(expr, context, expected):
    print(ExprTree.from_string(expr))
    assert ExprTree.from_string(expr).evaluate(context) == expected


## Runtime errors

@pytest.mark.parametrize(('expr', 'context', 'expected'), [
    ('x < y', {'x': 1}, KeyError),
    ('x < y', {'x': 1, 'y': 'foo'}, TypeError),
    ('x < y', {'x': 1, 'y': None}, TypeError),
    ('x + y', {'x': 1, 'y': None}, TypeError),
])
def test_expr_tree_runtime_error(expr, context, expected):
    with pytest.raises(expected):
        ExprTree.from_string(expr).evaluate(context)
