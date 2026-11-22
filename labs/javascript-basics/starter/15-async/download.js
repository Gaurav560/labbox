// Chapter 15: three songs to download. One at a time, or all at once?
const download = (title, ms) => new Promise((resolve) => setTimeout(() => resolve(title), ms));

async function oneByOne() {
  const start = Date.now();
  await download("Monsoon Drive", 300);
  await download("Neon Lanes", 300);
  await download("Slow Sunday", 300);
  return Date.now() - start;
}

async function allAtOnce() {
  const start = Date.now();
  const titles = await Promise.all([
    download("Monsoon Drive", 300),
    download("Neon Lanes", 300),
    download("Slow Sunday", 300),
  ]);
  console.log(titles);
  return Date.now() - start;
}

async function main() {
  const slow = await oneByOne();
  const fast = await allAtOnce();
  console.log(slow >= 900, fast < 450);
}

main();
