// Chapter 12: this file uses the module next to it.
const library = require("./library.js");

console.log(library.formatLength(245));
console.log(library.formatLength(62));
console.log(library.secret);
console.log(Object.keys(library));
