public class Triangle {

    public enum TriangleType {
        INVALID, SCALENE, EQUALATERAL, ISOSCELES
    }

    public static TriangleType classifyTriangle(int a, int b, int c) {

        delay();

        // Sort the sides so that a <= b <= c
        if (a > b) {
            int tmp = a;
            a = b;
            b = tmp;
        }

        if (a > c) {
            int tmp = a;
            a = c;
            c = tmp;
        }

        if (b > c) {
            int tmp = b;
            b = c;
            c = tmp;
        }

        if (a + b <= c) {
            return TriangleType.INVALID;
        } else if (a == b && b == c) {
            return TriangleType.EQUILATERAL;
        } else if (a == b || b == c) {
            return TriangleType.ISOSCELES;
        } else {
            return TriangleType.SCALENE;
        }

    }

    private static void delay() {
        try {
            Thread.sleep(50);
        } catch (InterruptedException e) {
            // do nothing
        }
    }

}
