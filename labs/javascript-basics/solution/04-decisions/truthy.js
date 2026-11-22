// Chapter 4: which values count as true in an if?
const values = [0, "", "0", [], null, "hello"];
for (const value of values) {
  if (value) {
    console.log(JSON.stringify(value), "is truthy");
  } else {
    console.log(JSON.stringify(value), "is falsy");
  }
}
