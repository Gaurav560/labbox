// Chapter 13: JavaScript's quiet failures. Nothing here throws.
const song = { title: "Neon Lanes" };
console.log(song.seconds * 2);
console.log(Number("twelve"));
console.log([1, 2, 3][7]);
console.log(song.artist?.name);
