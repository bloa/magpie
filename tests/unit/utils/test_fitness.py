import pytest

from magpie.utils import (
    dominates,
    dominates_or_equal,
    pareto,
)

@pytest.mark.parametrize(('fit1', 'fit2', 'res'), [
    (0, 1, True),
    (1, 0, False),
    (1, 1, False),
    (None, 1, False),
    (1, None, True),
    (None, None, False),
])
def test_dominates(fit1, fit2, res):
    assert dominates(fit1, fit2) == res

@pytest.mark.parametrize(('fit1', 'fit2', 'res'), [
    (0, 1, True),
    (1, 0, False),
    (1, 1, True),
    (None, 1, False),
    (1, None, True),
    (None, None, True),
])
def test_dominates_or_equal(fit1, fit2, res):
    assert dominates_or_equal(fit1, fit2) == res

def test_pareto_dominated():
    pop = [
        {'patch': '1', 'fitness': [1, 5]},
        {'patch': '2', 'fitness': [5, 1]},
        {'patch': '3', 'fitness': [3, 3]},
        {'patch': '4', 'fitness': [1, 2]},
        {'patch': '5', 'fitness': [2, 1]},
    ]
    front = pareto(pop)
    assert sorted(sol['patch'] for sol in front) == ['4', '5']

def test_pareto_repeated():
    pop = [
        {'patch': 'foo1', 'fitness': [1, 2]},
        {'patch': 'foo2', 'fitness': [2, 1]},
        {'patch': 'foo3', 'fitness': [3, 3]},
        {'patch': 'bar1', 'fitness': [2, 1]},
        {'patch': 'bar2', 'fitness': [3, 3]},
        {'patch': 'bar1', 'fitness': [2, 1]},
        {'patch': 'bar2', 'fitness': [3, 3]},
    ]
    front = pareto(pop)
    assert sorted(sol['patch'] for sol in front) == ['bar1', 'foo1', 'foo2']
