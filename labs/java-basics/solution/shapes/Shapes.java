package shapes;

import java.util.List;

public class Shapes {
    public static double totalArea(List<Shape> shapes) {
        double total = 0;
        for (Shape s : shapes) {
            total += s.area();
        }
        return Math.round(total * 100) / 100.0;
    }
}
