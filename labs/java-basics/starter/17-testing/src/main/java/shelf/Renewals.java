// Chapter 17: may a member renew a loan? RenewalsTest says something is wrong here.
package shelf;

public class Renewals {
    /** A loan may be renewed at most twice, and never while another member has reserved the book. */
    public static boolean canRenew(int renewalsSoFar, boolean reserved) {
        // TODO (task fix_renewal): one test in RenewalsTest fails. Read its message, then fix this line.
        return !reserved && renewalsSoFar <= 2;
    }
}
