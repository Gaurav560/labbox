// Chapter 14: a method handed to someone else forgets its object.
class Player {
  constructor(name) {
    this.name = name;
  }

  hello() {
    return `${this.name} says hello`;
  }
}

const p = new Player("Mixtape");
console.log(p.hello());

const later = p.hello;
try {
  console.log(later());
} catch (error) {
  console.log(error.name + ":", error.message);
}

const bound = p.hello.bind(p);
console.log(bound());
