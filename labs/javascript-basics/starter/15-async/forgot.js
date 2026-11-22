// Chapter 15: forgetting await.
const download = (title) => new Promise((resolve) => setTimeout(() => resolve(title), 100));

async function main() {
  const title = download("Neon Lanes");
  console.log(title);
  console.log(await download("Neon Lanes"));
}

main();
