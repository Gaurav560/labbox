// Chapter 12: an enum, and a switch expression over it.
public class Days {
    enum Genre {
        FANTASY, HISTORY, CHILDREN
    }

    static int loanDays(Genre genre) {
        return switch (genre) {
            case CHILDREN -> 14;
            case FANTASY, HISTORY -> 21;
        };
    }

    public static void main(String[] args) {
        Genre g = Genre.CHILDREN;
        System.out.println(g + " " + loanDays(g) + " " + g.ordinal());
        for (Genre each : Genre.values()) {
            System.out.print(each + " ");
        }
        System.out.println();
        System.out.println(Genre.valueOf("HISTORY") == Genre.HISTORY);
        System.out.println(Genre.valueOf("Fantasy"));
    }
}
