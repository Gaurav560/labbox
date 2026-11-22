// Chapter 3: one day at the library, in variables. Run it, then change the numbers and run it again.
public class Today {
    public static void main(String[] args) {
        int borrowed = 7;
        int returned = 4;
        double fineRupees = 12.5;

        int stillOut = borrowed - returned;
        System.out.println("Books still out: " + stillOut);
        System.out.println("Fines today: " + fineRupees + " rupees");
        System.out.println("7 / 2 = " + 7 / 2 + ", but 7 / 2.0 = " + 7 / 2.0);
    }
}
