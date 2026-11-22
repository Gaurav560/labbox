// Chapter 14: one class, many songs, each with its own plays.
class Song {
  #plays = 0;

  constructor(title, seconds) {
    this.title = title;
    this.seconds = seconds;
  }

  play() {
    this.#plays = this.#plays + 1;
    return `${this.title}: play number ${this.#plays}`;
  }

  get plays() {
    return this.#plays;
  }
}

const a = new Song("Neon Lanes", 198);
const b = new Song("Slow Sunday", 312);
console.log(a.play());
console.log(a.play());
console.log(b.play());
console.log(a.plays, b.plays, a.title);
console.log(a.secret, typeof Song);
