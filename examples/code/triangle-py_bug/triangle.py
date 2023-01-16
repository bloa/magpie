from enum import Enum


class TriangleType(Enum):
    INVALID, EQUILATERAL, ISOSCELES, SCALENE = 0, 1, 2, 3


def classify_triangle(a, b, c):

    # Sort the sides so that a <= b <= c
    if a > b:
        tmp = a
        a = b
        b = tmp

    if a > c:
        tmp = a
        a = c
        c = tmp

    if b > c:
        tmp = b
        b = c
        c = tmp

    if a + b <= c:
        return TriangleType.INVALID
    elif a == b and b == c:
        # should be EQUILATERAL
        return TriangleType.ISOSCELES
    elif a == b or b == c:
        # should be ISOSCELES
        return TriangleType.EQUILATERAL
    else:
        return TriangleType.SCALENE
