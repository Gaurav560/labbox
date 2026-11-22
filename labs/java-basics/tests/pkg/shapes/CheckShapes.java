import java.util.List;

public class CheckShapes {
    public static void main(String[] a) {
        try {
            double r = new Rect(3, 4).area(), c = new Circle(2).area();
            if (r != 12) T.fail("areas", "new Rect(3, 4).area() gave " + r + ", but it should be 12.0.", 12.0, r);
            else if (Math.abs(c - 4 * Math.PI) > 1e-9) T.fail("areas", "new Circle(2).area() gave " + c + ", but it should be about 12.566 (use Math.PI).", 4 * Math.PI, c);
            else T.pass("areas");
        } catch (Throwable e) { T.crashed("areas", e); }
        try {
            Object[][] cases = {{List.of(new Rect(3, 4), new Circle(1)), 15.14}, {List.of(new Circle(2), new Circle(2)), 25.13}, {List.<Shape>of(), 0.0}, {List.of(new Rect(2.5, 2)), 5.0}};
            for (Object[] cs : cases) {
                @SuppressWarnings("unchecked") List<Shape> in = (List<Shape>) cs[0];
                double got = Shapes.totalArea(in);
                if (got != (double) cs[1]) {
                    T.fail("total_area", "totalArea of " + in.size() + " shapes gave " + got + ", but it should be " + cs[1] + ".", cs[1], got);
                    return;
                }
            }
            T.pass("total_area");
        } catch (Throwable e) { T.crashed("total_area", e); }
    }
}
