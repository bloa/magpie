require 'minitest/autorun'

require_relative 'triangle'

class TestTriangle < MiniTest::Unit::TestCase

  def check_classification(triangles, expected_result)
    for triangle in triangles
      assert_equal(expected_result, classify_triangle(*triangle))
    end
  end

  def test_invalid_triangles()
    triangles = [[1, 2, 9], [1, 9, 2], [2, 1, 9], [2, 9, 1], [9, 1, 2],
                 [9, 2, 1], [1, 1, -1], [1, -1, 1], [-1, 1, 1]]
    check_classification(triangles, :invalid)
  end

  def test_equalateral_triangles()
    triangles = [[1, 1, 1], [100, 100, 100], [99, 99, 99]]
    check_classification(triangles, :equilateral)
  end

  def test_isoceles_triangles()
    triangles = [[100, 90, 90], [90, 100, 90], [90, 90, 100], [2, 2, 3]]
    check_classification(triangles, :isoceles)
  end

  def test_scalene_triangles()
    triangles = [[5, 4, 3], [5, 3, 4], [4, 5, 3], [4, 3, 5], [3, 5, 4]]
    check_classification(triangles, :scalene)
  end
end
