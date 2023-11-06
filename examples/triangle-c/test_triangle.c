#include <stdio.h>

#include "triangle.h"

int passed = 0;
int failed = 0;

void check_classification(double a, double b, double c, double expected_result) {
  if (classify_triangle(a, b, c) == expected_result)
    passed++;
  else
    failed++;
}

void test_invalid_triangles() {
  check_classification(1, 2, 9, INVALID);
  check_classification(1, 9, 2, INVALID);
  check_classification(2, 1, 9, INVALID);
  check_classification(2, 9, 1, INVALID);
  check_classification(9, 1, 2, INVALID);
  check_classification(9, 2, 1, INVALID);
  check_classification(1, 1, -1, INVALID);
  check_classification(1, -1, 1, INVALID);
  check_classification(-1, 1, 1, INVALID);
}

void test_equilateral_triangles() {
  check_classification(1, 1, 1, EQUILATERAL);
  check_classification(100, 100, 100, EQUILATERAL);
  check_classification(99, 99, 99, EQUILATERAL);
}

void test_isosceles_triangles() {
  check_classification(100, 90, 90, ISOSCELES);
  check_classification(90, 100, 90, ISOSCELES);
  check_classification(90, 90, 100, ISOSCELES);
  check_classification(2, 2, 3, ISOSCELES);
}

void test_scalene_triangles() {
  check_classification(5, 4, 3, SCALENE);
  check_classification(5, 3, 4, SCALENE);
  check_classification(4, 5, 3, SCALENE);
  check_classification(4, 3, 5, SCALENE);
  check_classification(3, 5, 4, SCALENE);
}

int main(int argc, char * argv[]){
  test_invalid_triangles();
  test_equilateral_triangles();
  test_isosceles_triangles();
  test_scalene_triangles();

  // Somehow mimic junit output
  printf("Tests run: %d\n", passed+failed);
  printf("Failures: %d\n", failed);

  return failed > 0;
}
