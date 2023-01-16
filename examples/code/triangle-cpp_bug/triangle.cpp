#include "triangle.hpp"

void delay() {
  const struct timespec ms = {0, (long int) (0.001*1e9)}; //tv_sec=0, tv_nsec (0.001 seconds)
  nanosleep(&ms,NULL); /*ignores possible errors*/
}

int classify_triangle(double a, double b, double c) {
  double tmp;

  delay();

  // Sort the sides so that a <= b <= c
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
    // should be EQUILATERAL
    return ISOSCELES;
  if(a == b || b == c)
    // should be ISOSCELES
    return EQUILATERAL;
  return SCALENE;
}
