// Chapter 8: a playlist that grows and shrinks.
const playlist = ["Monsoon Drive", "Neon Lanes"];
playlist.push("Slow Sunday");
console.log(playlist, playlist.length);
console.log(playlist[0], playlist.at(-1), playlist[9]);

const backup = playlist;
backup.pop();
console.log(playlist);

const copy = [...playlist];
copy.push("Paper Boats");
console.log(playlist.length, copy.length);
