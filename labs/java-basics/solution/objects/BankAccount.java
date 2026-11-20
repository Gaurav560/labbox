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

    public void deposit(int amount) {
        if (amount <= 0) {
            throw new IllegalArgumentException("amount must be positive: " + amount);
        }
        balance += amount;
    }

    public void withdraw(int amount) {
        if (amount <= 0) {
            throw new IllegalArgumentException("amount must be positive: " + amount);
        }
        if (amount > balance) {
            throw new IllegalArgumentException("not enough money: balance " + balance + ", asked " + amount);
        }
        balance -= amount;
    }
}
