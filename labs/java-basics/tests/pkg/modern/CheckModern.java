public class CheckModern {
    public static void main(String[] a) {
        checkLoan();
        checkGenre();
    }

    static boolean refuses(String title, int days) {
        try {
            new Loan(title, days);
            return false;
        } catch (IllegalArgumentException e) {
            return true;
        }
    }

    static void checkLoan() {
        try {
            Loan dune = new Loan("  Dune ", 14);
            if (!"Dune".equals(dune.title())) {
                T.fail("loan_record", "new Loan(\"  Dune \", 14).title() gave " + T.show(dune.title()) + ", but it should be \"Dune\": strip the title inside the compact constructor (title = title.strip();).", "Dune", dune.title());
            } else if (!refuses("   ", 14)) {
                T.fail("loan_record", "new Loan(\"   \", 14) was accepted, but a blank title should throw an IllegalArgumentException.");
            } else if (!refuses("Dune", 0)) {
                T.fail("loan_record", "new Loan(\"Dune\", 0) was accepted, but days below 1 should throw an IllegalArgumentException.");
            } else if (!refuses("Dune", 61)) {
                T.fail("loan_record", "new Loan(\"Dune\", 61) was accepted, but more than 60 days should throw an IllegalArgumentException.");
            } else if (refuses("Emma", 1) || refuses("Emma", 60)) {
                T.fail("loan_record", "1 day and 60 days are both allowed, but one of them was refused. Check the edges: < 1 and > 60.");
            } else if (!new Loan("Emma", 7).equals(new Loan(" Emma", 7))) {
                T.fail("loan_record", "two loans for the same stripped title and days should be equal.");
            } else {
                T.pass("loan_record");
            }
        } catch (Throwable e) { T.crashed("loan_record", e); }
    }

    static void checkGenre() {
        try {
            Object[][] cases = {{"Fantasy", Genre.FANTASY}, {"  science   fiction ", Genre.SCIENCE_FICTION}, {"HISTORY", Genre.HISTORY}, {"children", Genre.CHILDREN}};
            for (Object[] c : cases) {
                Genre got = Genre.fromText((String) c[0]);
                if (got != c[1]) {
                    T.fail("genre_enum", "fromText(" + T.show((String) c[0]) + ") gave " + got + ", but it should be " + c[1] + ".", c[1], got);
                    return;
                }
            }
            for (String bad : new String[] {"Fantsy", "", "   "}) {
                try {
                    Genre got = Genre.fromText(bad);
                    T.fail("genre_enum", "fromText(" + T.show(bad) + ") gave " + got + ", but text that is not a genre should throw an IllegalArgumentException.");
                    return;
                } catch (IllegalArgumentException e) {
                    // refused, as it should be
                }
            }
            T.pass("genre_enum");
        } catch (Throwable e) { T.crashed("genre_enum", e); }
    }
}
