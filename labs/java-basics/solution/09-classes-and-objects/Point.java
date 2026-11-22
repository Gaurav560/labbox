// Chapter 9: a point on a map, as a record.
public record Point(int x, int y) {
    /** The straight-line distance to other, rounded to 2 decimals. */
    public double distanceTo(Point other) {
        int dx = other.x() - x;
        int dy = other.y() - y;
        double d = Math.sqrt(dx * dx + dy * dy);
        return Math.round(d * 100) / 100.0;
    }

    public static void main(String[] args) {
        System.out.println(new Point(0, 0).distanceTo(new Point(3, 4)));
        System.out.println(new Point(1, 1).distanceTo(new Point(2, 2)));
    }
}
