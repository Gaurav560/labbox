// Chapter 7: strings.

function countWords(text) {
  // TODO (task count_words): how many words, however many spaces are between them
  return 0;
}

function cleanName(raw) {
  // TODO (task clean_name): "  riya   SHARMA " becomes "Riya Sharma"
  return raw;
}

if (require.main === module) {
  console.log(countWords("JavaScript is fun"), countWords("  lots   of   spaces  "), countWords(""));
  console.log(`[${cleanName("  riya   SHARMA ")}]`);
}

module.exports = { countWords, cleanName };
