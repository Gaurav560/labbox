// Chapter 6: this program crashes on the second day. Run it and read the stack trace.
public class Report {
    static int average(int[] fines) {
        int total = 0;
        for (int fine : fines) {
            total += fine;
        }
        return total / fines.length;
    }

    static String summary(String day, int[] fines) {
        return day + ": average fine " + average(fines) + " rupees";
    }

    public static void main(String[] args) {
        System.out.println(summary("Monday", new int[] {10, 20, 30}));
        System.out.println(summary("Tuesday", new int[] {}));
    }
}
