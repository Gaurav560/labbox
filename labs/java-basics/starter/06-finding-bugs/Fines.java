// Chapter 6: finding bugs. Both methods compile, run without crashing, and give a wrong answer.
public class Fines {
    // TODO (task fix_total_fines): totalFines(new int[] {10, 20, 30}) should be 60, but it says 50. Find out why.
    public static int totalFines(int[] fines) {
        int total = 0;
        for (int i = 1; i < fines.length; i++) {
            total = total + fines[i];
        }
        return total;
    }

    // TODO (task fix_can_borrow): a member may borrow while they have fewer books than the limit; at the limit, no more.
    public static boolean canBorrow(int borrowed, int limit) {
        int room = limit - borrowed;
        return room >= 0;
    }

    public static void main(String[] args) {
        System.out.println(totalFines(new int[] {10, 20, 30}));
        System.out.println(canBorrow(5, 5));
    }
}
