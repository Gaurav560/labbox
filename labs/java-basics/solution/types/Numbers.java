package types;

/** Chapter 2: variables and types. */
public class Numbers {
    /** scored out of total as a percentage, rounded to one decimal; 0 when total is 0. */
    public static double percent(int scored, int total) {
        if (total == 0) {
            return 0;
        }
        double p = (double) scored / total * 100;
        return Math.round(p * 10) / 10.0;
    }

    /** paise as rupees, like "₹12.50". */
    public static String formatRupees(int paise) {
        return String.format("₹%d.%02d", paise / 100, paise % 100);
    }
}
