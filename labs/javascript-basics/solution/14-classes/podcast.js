// Chapter 14: a podcast is a kind of track, with one thing different.
class Track {
  constructor(title, seconds) {
    this.title = title;
    this.seconds = seconds;
  }

  label() {
    return `${this.title} ${this.length()}`;
  }

  length() {
    return `${Math.floor(this.seconds / 60)} min`;
  }
}

class Podcast extends Track {
  constructor(title, seconds, host) {
    super(title, seconds);
    this.host = host;
  }

  length() {
    return `${Math.round(this.seconds / 60)} min episode`;
  }
}

console.log(new Track("Neon Lanes", 198).label());
console.log(new Podcast("Night Shift", 2730, "Riya").label());
console.log(new Podcast("Night Shift", 2730, "Riya") instanceof Track);
