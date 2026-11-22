// Chapter 17: the Skip button. skip.test.js says something is wrong here.

/** The position of the next song; after the last song, back to the first. */
function nextIndex(index, count) {
  return (index + 1) % count;
}

module.exports = { nextIndex };
