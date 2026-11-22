// Chapter 12: a loan that can never hold a bad title or a silly number of days.
public record Loan(String title, int days) {
    public Loan {
        title = title.strip();
        if (title.isEmpty()) {
            throw new IllegalArgumentException("a loan needs a title");
        }
        if (days < 1 || days > 60) {
            throw new IllegalArgumentException("days must be 1 to 60, not " + days);
        }
    }

    public static void main(String[] args) {
        System.out.println(new Loan("  Dune ", 14));
        try {
            new Loan("Dune", 0);
            System.out.println("0 days was accepted");
        } catch (IllegalArgumentException e) {
            System.out.println("refused: " + e.getMessage());
        }
    }
}
