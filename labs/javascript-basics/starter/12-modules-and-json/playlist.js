// Chapter 12: Mixtape saves a playlist as JSON text, and loads it back.

// TODO (task save_playlist): JSON text of { name, count, songs }, where count is how many songs there are.
function savePlaylist(name, songs) {
  return "";
}

// TODO (task load_playlist): the titles of the songs in the JSON text; [] when it has no "songs".
function loadPlaylist(text) {
  return [];
}

if (require.main === module) {
  const text = savePlaylist("Rainy day", [{ title: "Monsoon Drive", seconds: 245 }]);
  console.log(text);
  console.log(loadPlaylist(text));
}

module.exports = { savePlaylist, loadPlaylist };
