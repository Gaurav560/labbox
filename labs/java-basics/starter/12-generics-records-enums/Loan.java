// Chapter 12: a loan that can never hold a bad title or a silly number of days.
public record Loan(String title, int days) {
    // TODO (task loan_record): strip the title; a blank title, or days outside 1 to 60, throws an IllegalArgumentException.
    public Loan {
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
