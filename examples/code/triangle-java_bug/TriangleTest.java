import static org.junit.Assert.*;

public class TriangleTest {

    private void checkClassification(int[][] triangles, Triangle.TriangleType expectedResult) {
        for (int[] triangle: triangles) {
            Triangle.TriangleType triangleType = Triangle.classifyTriangle(triangle[0], triangle[1], triangle[2]);
            assertEquals(expectedResult, triangleType);
        }
    }

    @org.junit.Test
    public void testInvalidTriangles() throws Exception {
        int[][] invalidTriangles = {
          {1, 2, 9}, {1, 9, 2}, {2, 1, 9}, {2, 9, 1}, {9, 1, 2}, {9, 2, 1},
          {1, 2, 1}, {1, 1, 2}, {2, 1, 1},
          {1, 1, -1}, {1, -1, 1}, {-1, 1, 1},
          {0, 0, 0}
        };
        checkClassification(invalidTriangles, Triangle.TriangleType.INVALID);
    }

    @org.junit.Test
    public void testEquilateralTriangles() throws Exception {
        int[][] equilateralTriangles = {{1, 1, 1}, {100, 100, 100}, {99, 99, 99}};
        checkClassification(equilateralTriangles, Triangle.TriangleType.EQUILATERAL);
    }

    @org.junit.Test
    public void testIsoscelesTriangles() throws Exception {
        int[][] isoscelesTriangles = {
          {2, 2, 3}, {2, 3, 2}, {3, 2, 2},
          {1, 2, 2}, {2, 1, 2}, {2, 2, 1}
        };
        checkClassification(isoscelesTriangles, Triangle.TriangleType.ISOSCELES);
    }

    @org.junit.Test
    public void testScaleneTriangles() throws Exception {
        int[][] scaleneTriangles = {
          {3, 4, 2}, {3, 2, 4}, {4, 3, 2}, {4, 2, 3}, {2, 3, 4}, {2, 4, 3}
        };
        checkClassification(scaleneTriangles, Triangle.TriangleType.SCALENE);
    }

}
