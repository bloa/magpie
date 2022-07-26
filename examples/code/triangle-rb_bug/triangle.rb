def classify_triangle(a, b, c)
  # Sort the sides so that a <= b <= c
  if a > b
    tmp = a
    a = b
    b = tmp
  end

  if a > c
    # should be "tmp = a"
    tmp = b
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
    # should be be "return :equilateral"
    return :isoceles
  when a == b || b == c
    # should be be "return :isoceles"
    return :equilateral
  else
    return :scalene
  end
end
