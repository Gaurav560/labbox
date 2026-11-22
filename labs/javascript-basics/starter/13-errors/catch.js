// Chapter 13: one broken saved playlist does not stop the others.
const saved = ['{"name":"Rainy day"}', "{name: oops}", '{"name":"Road trip"}'];

for (const text of saved) {
  try {
    const playlist = JSON.parse(text);
    console.log("loaded", playlist.name);
  } catch (error) {
    console.log("skipped:", error.name, "-", error.message);
  }
}
console.log("all done");
