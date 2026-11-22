// Chapter 9: a bank account that refuses bad amounts.
public class BankAccount {
    private final String owner;
    private int balance;

    public BankAccount(String owner) {
        this.owner = owner;
    }

    public String getOwner() {
        return owner;
    }

    public int getBalance() {
        return balance;
    }

    // TODO (task bank_account): add amount; a zero or negative amount throws IllegalArgumentException.
    public void deposit(int amount) {
    }

    // TODO (task bank_account): take amount out; a bad amount, or more than the balance, throws
    // IllegalArgumentException and leaves the balance as it was.
    public void withdraw(int amount) {
    }

    public static void main(String[] args) {
        BankAccount account = new BankAccount("Asha");
        account.deposit(500);
        account.withdraw(200);
        System.out.println(account.getOwner() + " has " + account.getBalance());
        try {
            account.withdraw(1000);
            System.out.println("1000 was taken out");
        } catch (IllegalArgumentException e) {
            System.out.println("refused, still " + account.getBalance());
        }
    }
}
