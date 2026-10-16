import pytest

import magpie
from magpie.utils import (
    dominates,
    dominates_or_equal,
    pareto,
    update_archive,
    update_global_best,
)

def create_solution(s, fit):
    patch = magpie.core.Patch([list(s)])
    return {'patch': patch, 'fitness': fit, 'diff': s}

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

def test_update_archive():
    pop = [
        create_solution('foo1', [1, 2]),
        create_solution('foo2', [2, 1]),
        create_solution('bar1', [2, 1]),
    ]
    # already in: no change
    candidate = create_solution('foo1', [1, 2])
    update_archive(pop, candidate)
    assert sorted(sol['diff'] for sol in pop) == ['bar1', 'foo1', 'foo2']
    # dominated: no change
    candidate = create_solution('baz1', [4, 4])
    update_archive(pop, candidate)
    assert sorted(sol['diff'] for sol in pop) == ['bar1', 'foo1', 'foo2']
    # dominates foo2 and bar1
    candidate = create_solution('baz2', [1.5, 1])
    update_archive(pop, candidate)
    assert sorted(sol['diff'] for sol in pop) == ['baz2', 'foo1']
    # dominates foo2 and bar1
    candidate = create_solution('baz3', [1, 1])
    update_archive(pop, candidate)
    assert sorted(sol['diff'] for sol in pop) == ['baz3']

def test_update_incumbent():
    incumbent = create_solution('ab', [1, 2])
    # same: no change
    candidate = create_solution('ab', [1, 2])
    update_global_best(incumbent, candidate)
    assert incumbent['diff'] == 'ab'
    # dominated: no change
    candidate = create_solution('a', [4, 4])
    update_global_best(incumbent, candidate)
    assert incumbent['diff'] == 'ab'
    # larger: no change
    candidate = create_solution('abc', [1, 2])
    update_global_best(incumbent, candidate)
    assert incumbent['diff'] == 'ab'
    # same size: no change
    candidate = create_solution('bc', [1, 2])
    update_global_best(incumbent, candidate)
    assert incumbent['diff'] == 'ab'
    # smaller: accepted
    candidate = create_solution('a', [1, 2])
    update_global_best(incumbent, candidate)
    assert incumbent['diff'] == 'a'
    # better: accepted
    candidate = create_solution('bc', [1, 1])
    update_global_best(incumbent, candidate)
    assert incumbent['diff'] == 'bc'
