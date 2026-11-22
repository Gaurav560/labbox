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
