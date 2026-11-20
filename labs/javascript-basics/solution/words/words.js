// Chapter 5: strings.

function countWords(text) {
  const words = text.trim().split(/\s+/);
  return words[0] === "" ? 0 : words.length;
}

function cleanName(raw) {
  return raw
    .trim()
    .split(/\s+/)
    .filter((w) => w !== "")
    .map((w) => w[0].toUpperCase() + w.slice(1).toLowerCase())
    .join(" ");
}

module.exports = { countWords, cleanName };
