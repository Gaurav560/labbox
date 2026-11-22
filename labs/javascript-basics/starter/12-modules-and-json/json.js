// Chapter 12: an object becomes text, and text becomes an object again.
const playlist = { name: "Rainy day", songs: [{ title: "Monsoon Drive", seconds: 245 }], shuffle: false };

const text = JSON.stringify(playlist);
console.log(text);
console.log(typeof text, text.length);

const back = JSON.parse(text);
console.log(back.songs[0].title, back === playlist);
console.log(JSON.stringify({ when: new Date(0), skip: undefined, play: () => 1 }));
console.log(JSON.stringify(playlist, null, 2));
