#include <time.h>

typedef enum { INVALID, EQUILATERAL, ISOSCELES, SCALENE } triangle_type; // 0, 1, 2, 3

int classify_triangle(double a, double b, double c);
