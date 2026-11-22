// Chapter 7: a song title typed in a hurry, tidied step by step.
const typed = "   monsoon DRIVE  ";
console.log(`[${typed}]`);
console.log(`[${typed.trim()}]`);
console.log(typed.trim().toLowerCase());
console.log(typed.length, typed.trim().length);

const title = "Neon Lanes";
console.log(title[0], title.at(-1), title.slice(0, 4), title.indexOf("L"), title.includes("Lane"));
title.toUpperCase();
console.log(title);
