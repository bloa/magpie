#include <stdio.h>
#include <stdlib.h>

#include "triangle.hpp"

int main(int argc, char * argv[]){
  const double a = (argc>1)? atof(argv[1]) : 0;
  const double b = (argc>2)? atof(argv[2]) : 0;
  const double c = (argc>3)? atof(argv[3]) : 0;

  const int ans = classify_triangle(a,b,c);
  printf("classify_triangle(%g, %g, %g) = %d\n", a, b, c, ans);

  return 0;
}
