package objects;

/** Chapter 7: a point on a map, as a record. */
public record Point(int x, int y) {
    // TODO (task point_distance): the straight-line distance to other, rounded to 2 decimals.
    public double distanceTo(Point other) {
        return 0;
    }
}
