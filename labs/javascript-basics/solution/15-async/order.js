// Chapter 15: in what order do these four lines print?
console.log("1. start");
setTimeout(() => console.log("2. timer, after 0 ms"), 0);
Promise.resolve().then(() => console.log("3. promise"));
console.log("4. end");
