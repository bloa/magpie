import pytest

from magpie.core import BasicAlgorithm


@pytest.mark.parametrize(('values', 'strategy', 'ref'), [
    # single objective
    ([1, 2, 3], 'last', 3),
    ([3, 1, 2], 'min', 1),
    ([0, 0, 0], 'min', 0),
    ([3, 1, 2], 'max', 3),
    ([-5, -2, -10], 'max', -2),
    ([1, 2, 3], 'mean', 2),
    ([5, 5, 5, 5], 'mean', 5),
    ([1, 2], 'mean', 1.5),
    ([3, 1, 2], 'median', 2),
    ([5, 1, 2, 3, 4], 'median', 3),
    ([1, 2, 3, 4], 'median', 2.5),
    ([4, 1, 3, 2], 'median', 2.5),
    # multi objective
    ([[1, 1], [2, 2], [3, 3]], 'last', [3, 3]),
    ([[3, 3], [1, 1], [2, 2]], 'min', [1, 1]),
    ([[3, 1], [1, 3], [2, 2]], 'min', [1, 1]),
])
def test_aggregate_warmup(values, strategy, ref):
    assert BasicAlgorithm._aggregate_warmup(values, strategy) == ref

@pytest.mark.parametrize(('values', 'strategy'), [
    ([1, 2, 3], 'foo'),
])
def test_aggregate_warmup_unknown(values, strategy):
    with pytest.raises(ValueError):
        BasicAlgorithm._aggregate_warmup(values, strategy)

