// Chapter 16: the words typed after the file name arrive in process.argv.
console.log(process.argv.length, "items");
console.log(process.argv.slice(2));
if (process.argv.length < 3) {
  console.error("Usage: node args.js <words>");
  process.exitCode = 2;
}
