// Chapter 13: finally runs whatever happens.
public class Finally {
    static int open = 0;

    static void lend(String title) {
        open++;
        System.out.println("desk open for " + title);
        try {
            if (title.isBlank()) {
                throw new IllegalArgumentException("no title");
            }
            System.out.println("lent " + title);
        } finally {
            open--;
            System.out.println("desk closed");
        }
    }

    public static void main(String[] args) {
        lend("Dune");
        try {
            lend(" ");
        } catch (IllegalArgumentException e) {
            System.out.println("refused: " + e.getMessage());
        }
        System.out.println("desks still open: " + open);
    }
}
