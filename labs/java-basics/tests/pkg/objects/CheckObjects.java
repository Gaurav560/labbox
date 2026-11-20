import objects.BankAccount;
import objects.Point;

public class CheckObjects {
    public static void main(String[] a) {
        try {
            double[][] cases = {{0, 0, 3, 4, 5.0}, {1, 1, 1, 1, 0.0}, {0, 0, 1, 1, 1.41}, {-2, 3, 4, -5, 10.0}};
            boolean ok = true;
            for (double[] c : cases) {
                double got = new Point((int) c[0], (int) c[1]).distanceTo(new Point((int) c[2], (int) c[3]));
                if (got != c[4]) {
                    T.fail("point_distance", "Point(" + (int) c[0] + ", " + (int) c[1] + ").distanceTo(Point(" + (int) c[2] + ", " + (int) c[3] + ")) gave " + got + ", but it should be " + c[4] + ".", c[4], got);
                    ok = false;
                    break;
                }
            }
            if (ok) T.pass("point_distance");
        } catch (Throwable e) { T.crashed("point_distance", e); }
        try {
            BankAccount acc = new BankAccount("Riya");
            acc.deposit(500);
            acc.withdraw(200);
            if (acc.getBalance() != 300) {
                T.fail("bank_account", "after deposit(500) and withdraw(200) the balance is " + acc.getBalance() + ", but it should be 300.", 300, acc.getBalance());
                return;
            }
            for (int bad : new int[] {0, -50}) {
                try {
                    acc.deposit(bad);
                    T.fail("bank_account", "deposit(" + bad + ") was accepted; it should throw an IllegalArgumentException.");
                    return;
                } catch (IllegalArgumentException e) { /* expected */ }
            }
            try {
                acc.withdraw(1000);
                T.fail("bank_account", "withdraw(1000) with only 300 was accepted; it should throw an IllegalArgumentException.");
                return;
            } catch (IllegalArgumentException e) { /* expected */ }
            if (acc.getBalance() != 300) {
                T.fail("bank_account", "a refused withdrawal changed the balance to " + acc.getBalance() + "; check before you subtract.", 300, acc.getBalance());
                return;
            }
            T.pass("bank_account");
        } catch (Throwable e) { T.crashed("bank_account", e); }
    }
}
