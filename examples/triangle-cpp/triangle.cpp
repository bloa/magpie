#include "triangle.hpp"

int classify_triangle(double a, double b, double c) {
  double tmp;

  // sort the sides so that a <= b <= c
  if(a > b) {
    tmp = a;
    a = b;
    b = tmp;
  }

  if(a > c) {
    tmp = a;
    a = c;
    c = tmp;
  }

  if(b > c) {
    tmp = b;
    b = c;
    c = tmp;
  }

  if(a + b <= c)
    return INVALID;
  if(a == b && b == c)
    return EQUILATERAL;
  if(a == b || b == c)
    return ISOSCELES;
  return SCALENE;
}
