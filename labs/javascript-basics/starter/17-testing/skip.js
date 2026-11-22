// Chapter 17: the Skip button. skip.test.js says something is wrong here.

/** The position of the next song; after the last song, back to the first. */
function nextIndex(index, count) {
  // TODO (task fix_skip): one test in skip.test.js fails. Read its message, then fix this line.
  return index + 1;
}

module.exports = { nextIndex };
