#include "triangle.h"

void classify() {
  // examples taken from test_triangle.py
  // invalid
  classify_triangle(1, 2, 9);
  classify_triangle(1, 9, 2);
  classify_triangle(2, 1, 9);
  classify_triangle(2, 9, 1);
  classify_triangle(9, 1, 2);
  classify_triangle(9, 2, 1);
  classify_triangle(1, 1, -1);
  classify_triangle(1, -1, 1);
  classify_triangle(-1, 1, 1);

  // equilateral
  classify_triangle(1, 1, 1);
  classify_triangle(100, 100, 100);
  classify_triangle(99, 99, 99);

  // isosceles
  classify_triangle(100, 90, 90);
  classify_triangle(90, 100, 90);
  classify_triangle(90, 90, 100);
  classify_triangle(2, 2, 3);

  // scalene
  classify_triangle(5, 4, 3);
  classify_triangle(5, 3, 4);
  classify_triangle(4, 5, 3);
  classify_triangle(4, 3, 5);
  classify_triangle(3, 5, 4);
}

int main(int argc, char * argv[]){
  // we don't really care about the output (we know the function work, from the test suite)
  // we just want to have something on which to measure running time
  for (int i=0; i<3; i++)
    classify();

  return 0;
}
