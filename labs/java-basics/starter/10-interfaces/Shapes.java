// Chapter 10: the library floor is made of shapes; add up their areas.

import java.util.List;

public class Shapes {
    // TODO (task total_area): the sum of all the areas, rounded to 2 decimals.
    public static double totalArea(List<Shape> shapes) {
        return 0;
    }

    public static void main(String[] args) {
        List<Shape> floor = List.of(new Rect(8, 5), new Circle(2));
        System.out.println("Library floor: " + totalArea(floor) + " square metres");
    }
}
