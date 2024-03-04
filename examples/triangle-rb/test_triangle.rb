require 'minitest/autorun'

require_relative 'triangle'

class TestTriangle < Minitest::Test
  data = {
    invalid: [
      [1, 2, 9], [1, 9, 2], [2, 1, 9], [2, 9, 1], [9, 1, 2], [9, 2, 1],
      [1, 1, -1], [1, -1, 1], [-1, 1, 1],
    ],
    equilateral: [
      [1, 1, 1], [99, 99, 99], [100, 100, 100],
    ],
    isosceles: [
      [100, 90, 90], [90, 100, 90], [90, 90, 100], [2, 2, 3],
    ],
    scalene: [
      [5, 4, 3], [5, 3, 4], [4, 5, 3], [4, 3, 5], [3, 5, 4],
    ],
  }

  data.each do |type, cases|
    cases.each.with_index do |triangle, k|
      define_method("test_#{type}_triangle_#{k}") do
        assert_equal(classify_triangle(*triangle), type)
      end
    end
  end
end
