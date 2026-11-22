// Chapter 17: the late fee. This code is correct: your job is to write the tests that prove it.
package shelf;

public class Fines {
    /** Rupees for a book returned daysLate days late: 2 a day for the first week, 5 a day after that, at most 100. */
    public static int lateFee(int daysLate) {
        if (daysLate < 0) {
            return 0;
        }
        int fee;
        if (daysLate <= 7) {
            fee = 2 * daysLate;
        } else {
            fee = 14 + 5 * (daysLate - 7);
        }
        return Math.min(fee, 100);
    }
}
