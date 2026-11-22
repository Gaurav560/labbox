// Chapter 4: Shelf decides. Run it, then change daysLate to 0 and run it again.
public class Loan {
    public static void main(String[] args) {
        int daysLate = 3;

        if (daysLate > 0) {
            System.out.println("Late by " + daysLate + " days: fine of " + daysLate * 2 + " rupees.");
        } else {
            System.out.println("Returned on time. Thank you!");
        }

        System.out.println("Shelf checked the loan.");
    }
}
