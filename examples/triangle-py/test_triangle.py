import pytest
from triangle import TriangleType, classify_triangle


@pytest.mark.parametrize('triangle', [
    (1, 2, 9),
    (1, 9, 2),
    (2, 1, 9),
    (2, 9, 1),
    (9, 1, 2),
    (9, 2, 1),
    (1, 1, -1),
    (1, -1, 1),
    (-1, 1, 1),
])
def test_invalid_triangles(triangle):
    assert classify_triangle(*triangle) == TriangleType.INVALID

@pytest.mark.parametrize('triangle', [
    (1, 1, 1),
    (99, 99, 99),
    (100, 100, 100),
])
def test_equilateral_triangles(triangle):
    assert classify_triangle(*triangle) == TriangleType.EQUILATERAL


@pytest.mark.parametrize('triangle', [
    (100, 90, 90),
    (90, 100, 90),
    (90, 90, 100),
    (2, 2, 3),
])
def test_isosceles_triangles(triangle):
    assert classify_triangle(*triangle) == TriangleType.ISOSCELES


@pytest.mark.parametrize('triangle', [
    (5, 4, 3),
    (5, 3, 4),
    (4, 5, 3),
    (4, 3, 5),
    (3, 5, 4)
])
def test_scalene_triangles(triangle):
    assert classify_triangle(*triangle) == TriangleType.SCALENE
