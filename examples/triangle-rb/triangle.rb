def classify_triangle(a, b, c)
  # sort the sides so that a <= b <= c
  if a > b
    tmp = a
    a = b
    b = tmp
  end

  if a > c
    tmp = c
    a = c
    c = tmp
  end

  if b > c
    tmp = b
    b = c
    c = tmp
  end

  case
  when a + b <= c
    return :invalid
  when a == b && b == c
    return :equilateral
  when a == b || b == c
    return :isosceles
  else
    return :scalene
  end
end
