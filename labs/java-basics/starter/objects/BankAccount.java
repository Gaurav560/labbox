package objects;

/** Chapter 7: a bank account that refuses bad amounts. */
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
}
