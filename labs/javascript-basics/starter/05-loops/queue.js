// Chapter 5: a playlist, added up song by song.
const titles = ["Monsoon Drive", "Neon Lanes", "Slow Sunday"];
const seconds = [245, 198, 312];

let total = 0;
for (let i = 0; i < seconds.length; i++) {
  total = total + seconds[i];
  console.log(`${titles[i]}: ${total} seconds so far`);
}

for (const title of titles) {
  console.log("Up next:", title);
}
