// Chapter 10: the library floor is made of shapes; add up their areas.

import java.util.List;

public class Shapes {
    public static double totalArea(List<Shape> shapes) {
        double total = 0;
        for (Shape s : shapes) {
            total += s.area();
        }
        return Math.round(total * 100) / 100.0;
    }

    public static void main(String[] args) {
        List<Shape> floor = List.of(new Rect(8, 5), new Circle(2));
        System.out.println("Library floor: " + totalArea(floor) + " square metres");
    }
}
