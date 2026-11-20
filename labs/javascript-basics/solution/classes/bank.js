// Chapter 11: classes.

class BankAccount {
  #balance = 0;

  constructor(owner) {
    this.owner = owner;
  }

  get balance() {
    return this.#balance;
  }

  deposit(amount) {
    if (!(amount > 0)) {
      throw new RangeError(`deposit must be positive: ${amount}`);
    }
    this.#balance += amount;
  }

  withdraw(amount) {
    if (!(amount > 0)) {
      throw new RangeError(`withdrawal must be positive: ${amount}`);
    }
    if (amount > this.#balance) {
      throw new RangeError(`cannot withdraw ${amount} from ${this.#balance}`);
    }
    this.#balance -= amount;
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

  area() {
    return Math.PI * this.radius ** 2;
  }
}

function totalArea(shapes) {
  let total = 0;
  for (const s of shapes) {
    total += s.area();
  }
  return Math.round(total * 100) / 100;
}

module.exports = { BankAccount, Rect, Circle, totalArea };
