require_relative 'triangle'

# examples taken from test_triangle.rb
triangles = [
    # invalid
    [1, 2, 9], [1, 9, 2], [2, 1, 9], [2, 9, 1], [9, 1, 2], [9, 2, 1],
    [1, 1, -1], [1, -1, 1], [-1, 1, 1],
    # equilateral
    [1, 1, 1], [100, 100, 100], [99, 99, 99],
    # isoceles
    [100, 90, 90], [90, 100, 90], [90, 90, 100], [2, 2, 3],
    # scalene
    [5, 4, 3], [5, 3, 4], [4, 5, 3], [4, 3, 5], [3, 5, 4],
]


if __FILE__ == $0
    # we don't really care about the output (we know the function work, from the test suite)
    # we just want to have something on which to measure running time

  3.times do
    for triangle in triangles
      classify_triangle(*triangle)
    end
  end
end
