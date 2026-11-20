:::step{type=story title="Why classes and objects"}
So far your data has been loose values: a number here, a name there. Real things have several parts
that belong together: a bank account has an owner and a balance, and rules about how the balance may
change. Java bundles data and the rules for it into **objects**. This idea is the heart of Java.

:::mission
In `objects/`, give a `Point` record a `distanceTo` method, and finish a `BankAccount` class that refuses
bad amounts.
:::
:::

:::step{type=concept title="A class is a blueprint, an object is a house"}
Picture an architect's **blueprint** for a house. The blueprint is not a house; it says what every
house built from it will have: rooms, doors, a kitchen. From one blueprint you can build many houses,
each with its own paint and furniture.

In Java, a **class** is the blueprint and an **object** is one house built from it:

```java
BankAccount riya = new BankAccount("Riya");
BankAccount arjun = new BankAccount("Arjun");
```

`new` builds an object from the class. `riya` and `arjun` are two separate accounts, each with its own
balance.
:::

:::step{type=concept title="Fields and methods"}
A class lists what each object **has** (fields) and what it **can do** (methods):

```java
public class BankAccount {
    private int balance;              // a field: each account has its own

    public int getBalance() {         // a method: ask for the balance
        return balance;
    }

    public void deposit(int amount) { // a method: change the balance
        balance += amount;
    }
}
```

`private` means only the class's own methods can touch `balance`. Code outside must go through
`deposit`, so the class can enforce its rules. That protection is called **encapsulation**.
:::

:::step{type=concept title="Constructors and this"}
A **constructor** runs when an object is built with `new`, to set up its fields. It has the class's
name and no return type:

```java
public BankAccount(String owner) {
    this.owner = owner;
}
```

`this.owner` means "the owner field of **this** object", and plain `owner` is the parameter. The line
copies the name you passed into the new object's field.
:::

:::step{type=concept title="Records: small classes for plain data"}
For simple data like a point on a map, Java 16 added **records**. One line gives you a class with
fields, a constructor, read methods, `equals` and `toString`:

```java
public record Point(int x, int y) { }

Point p = new Point(3, 4);
p.x()            // 3
p.y()            // 4
```

You can still add your own methods inside the braces, as your first task does.
:::

:::step{type=example title="Worked example: a method on a record"}
A record with a method that uses its own fields:

```java
public record Rect(int width, int height) {
    public int area() {
        return width * height;
    }
}

new Rect(3, 4).area()    // 12
```

Inside the record, `width` and `height` are this object's own values. To read another object's values,
call its methods: `other.width()`.
:::

:::step{type=predict title="Guess first"}
:::question
What does the last line print?

```java
BankAccount a = new BankAccount("Riya");
BankAccount b = a;
b.deposit(100);
System.out.println(a.getBalance());
```
:::
- [ ] `0`
- [x] `100`
- [ ] `200`
- [ ] It does not compile
:::explain
`b = a` does not copy the account: both variables now point to the **same** object, like two people
holding the same house address. Depositing through `b` changes the one account `a` also sees.
:::
:::

:::step{type=try title="One object, two names"}
:::diagram{name="object-reference"}
`a` and `b` are two names for one account object; `new` makes a second, separate object.
:::

```bash run
cat > /tmp/Acct.java <<'JAVA'
public class Acct {
    static class Account { int balance; }
    public static void main(String[] args) {
        Account a = new Account();
        Account b = a;
        Account c = new Account();
        b.balance += 100;
        System.out.println(a.balance + " " + b.balance + " " + c.balance);
    }
}
JAVA
java /tmp/Acct.java
```
:::

:::step{type=task task=point_distance title="Warm-up: distance between points"}
In `objects/Point.java`, make `distanceTo(other)` return the straight-line distance, **rounded to 2
decimals**.

- `new Point(0, 0).distanceTo(new Point(3, 4))` returns `5.0`
- `new Point(0, 0).distanceTo(new Point(1, 1))` returns `1.41`

The distance is `Math.sqrt(dx * dx + dy * dy)`, where `dx` and `dy` are the differences in x and y.
:::

:::step{type=task task=bank_account title="An account that protects itself"}
In `objects/BankAccount.java`, finish `deposit` and `withdraw`:

- `deposit(amount)` adds to the balance; a zero or negative amount throws an `IllegalArgumentException`
- `withdraw(amount)` takes money out; a bad amount, **or more than the balance**, throws an
  `IllegalArgumentException` and leaves the balance exactly as it was

After `deposit(500)` and `withdraw(200)`, `getBalance()` is `300`.

:::why
Because `balance` is private, these two methods are the only way in. Checking every amount here means
no other code in the program can ever create a negative balance.
:::
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
What does `new` do?
:::
- [ ] Makes a new class
- [x] Builds a new object from a class
- [ ] Copies an existing object
- [ ] Makes a new variable type
:::explain
`new BankAccount("Riya")` builds one object from the `BankAccount` blueprint and runs its constructor.
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
Why is `balance` declared `private`?
:::
- [ ] To make the program faster
- [x] So only the class's own methods can change it
- [ ] So it is saved to disk
- [ ] Because ints must be private
:::explain
Private fields can only be changed through the class's methods, which can check every change. That is
encapsulation.
:::
:::

:::step{type=deep-dive title="References, the heap and the garbage collector"}
Objects live in an area of memory called the **heap**. A variable like `a` does not hold the object
itself, only a **reference** to it, much like an address written on an envelope. That is why `b = a`
gives a second envelope with the same address, not a second house.

When no variable refers to an object any more, Java's **garbage collector** frees its memory
automatically. In C++ you would free it yourself, and forgetting (or doing it twice) was a classic
source of crashes Java was designed to remove.
:::

:::step{type=recap}
- A class is a blueprint; `new` builds objects from it.
- Fields are what an object has; methods are what it can do.
- `private` fields plus checking methods keep an object's rules safe (encapsulation).
- Variables hold references: `b = a` shares one object; a record is a compact class for plain data.
:::
