import pytest

from magpie.utils import BoolTree, ExprTree, MathTree


## Typing errors

@pytest.mark.parametrize(('expr', 'expected'), [
    ('-True', TypeError),
    ('not 1', TypeError),
    ('1 and 2', TypeError),
    ('1 and (x + y)', TypeError),
    ('1 + (x or y)', TypeError),
    ('1 + (!x)', TypeError),
    ('x in 1', TypeError),
    ('x in y', TypeError),
])
def test_expr_tree_typing_error(expr, expected):
    with pytest.raises(expected):
        ExprTree(expr)

@pytest.mark.parametrize(('expr', 'expected'), [
    ('True', TypeError),
    ('not x', TypeError),
    ('x < y', TypeError),
    ('x and y', TypeError),
    ('x in [0, 1]', TypeError),
])
def test_math_tree_typing_error(expr, expected):
    with pytest.raises(expected):
        MathTree(expr)

@pytest.mark.parametrize(('expr', 'expected'), [
    ('1', TypeError),
    ('x + y', TypeError),
])
def test_bool_tree_typing_error(expr, expected):
    with pytest.raises(expected):
        BoolTree(expr)

## Runtime

@pytest.mark.parametrize(('expr', 'context', 'expected'), [
    ('True', {}, True),
    ('True', {'foo': 0}, True),
    ('1 + 2', {}, 3),
    ('-1 + 2', {}, 1),
    ('-(-1)', {}, 1),
    ('-(((-(-(1)))))', {}, -1),
    ('1.2 + 2.5', {}, 3.7),
    ('(2 + x) * y', {'x': 2, 'y': 3}, 12),
    ('2 + x * y', {'x': 2, 'y': 3}, 8),
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
    assert ExprTree(expr).evaluate(context) == expected


## Runtime errors

@pytest.mark.parametrize(('expr', 'context', 'expected'), [
    ('x < y', {'x': 1}, KeyError),
    ('x < y', {'x': 1, 'y': 'foo'}, TypeError),
    ('x < y', {'x': 1, 'y': None}, TypeError),
    ('x + y', {'x': 1, 'y': None}, TypeError),
])
def test_expr_tree_runtime_error(expr, context, expected):
    with pytest.raises(expected):
        ExprTree(expr).evaluate(context)
