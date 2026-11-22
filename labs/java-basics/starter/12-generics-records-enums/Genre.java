// Chapter 12: the only genres Shelf knows. Typed text becomes one of them, or is refused.
public enum Genre {
    FANTASY, SCIENCE_FICTION, HISTORY, CHILDREN;

    // TODO (task genre_enum): "  science fiction " becomes SCIENCE_FICTION; unknown text throws an IllegalArgumentException.
    public static Genre fromText(String text) {
        return null;
    }

    public static void main(String[] args) {
        System.out.println(fromText("Fantasy"));
        System.out.println(fromText("  science   fiction "));
    }
}
