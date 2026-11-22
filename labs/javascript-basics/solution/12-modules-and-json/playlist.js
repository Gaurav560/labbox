// Chapter 12: Mixtape saves a playlist as JSON text, and loads it back.

function savePlaylist(name, songs) {
  return JSON.stringify({ name, count: songs.length, songs });
}

function loadPlaylist(text) {
  const playlist = JSON.parse(text);
  return (playlist.songs ?? []).map((song) => song.title);
}

if (require.main === module) {
  const text = savePlaylist("Rainy day", [{ title: "Monsoon Drive", seconds: 245 }]);
  console.log(text);
  console.log(loadPlaylist(text));
}

module.exports = { savePlaylist, loadPlaylist };
