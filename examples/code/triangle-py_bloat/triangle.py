import time
from enum import Enum


class TriangleType(Enum):
    INVALID, EQUILATERAL, ISOSCELES, SCALENE = 0, 1, 2, 3


# never used
def delay():
    time.sleep(0.001)


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
        return TriangleType.EQUILATERAL
    elif a == b or b == c:
        return TriangleType.ISOSCELES
    else:
        return TriangleType.SCALENE

    # never executed
    return TriangleType.INVALID
