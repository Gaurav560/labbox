// Chapter 14: classes.

class BankAccount {
  #balance = 0;

  constructor(owner) {
    this.owner = owner;
  }

  get balance() {
    return this.#balance;
  }

  deposit(amount) {
    // TODO (task bank_account): add amount; throw a RangeError unless it is positive
  }

  withdraw(amount) {
    // TODO (task bank_account): take amount out; throw a RangeError for a bad amount
    // or more than the balance, and leave the balance as it was
  }
}

class Rect {
  constructor(width, height) {
    this.width = width;
    this.height = height;
  }

  area() {
    return this.width * this.height;
  }
}

class Circle {
  constructor(radius) {
    this.radius = radius;
  }

  // TODO (task total_area): give Circle an area() method too (Math.PI times radius squared)
}

function totalArea(shapes) {
  // TODO (task total_area): add up every shape's area(), rounded to 2 decimals
  return 0;
}

if (require.main === module) {
  const account = new BankAccount("Riya");
  account.deposit(500);
  account.withdraw(200);
  console.log(account.owner, account.balance);
  console.log(totalArea([new Rect(3, 4), new Circle(1)]));
}

module.exports = { BankAccount, Rect, Circle, totalArea };
