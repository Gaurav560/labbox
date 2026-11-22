// Chapter 9: one song, as an object.
const song = { title: "Monsoon Drive", seconds: 245, liked: false };
console.log(song.title, song["seconds"]);

song.liked = true;
song.plays = 1;
console.log(song);
console.log(song.artist);

const same = song;
same.plays = 99;
console.log(song.plays);

const copy = { ...song, plays: 0 };
console.log(song.plays, copy.plays);
