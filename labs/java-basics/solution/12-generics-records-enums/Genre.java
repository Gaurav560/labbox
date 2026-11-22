// Chapter 12: the only genres Shelf knows. Typed text becomes one of them, or is refused.
public enum Genre {
    FANTASY, SCIENCE_FICTION, HISTORY, CHILDREN;

    public static Genre fromText(String text) {
        String name = String.join("_", text.strip().toUpperCase().split("\\s+"));
        return Genre.valueOf(name);
    }

    public static void main(String[] args) {
        System.out.println(fromText("Fantasy"));
        System.out.println(fromText("  science   fiction "));
    }
}
