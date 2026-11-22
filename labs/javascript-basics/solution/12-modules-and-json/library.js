// Chapter 12: a module. Other files can use what it exports.
function formatLength(seconds) {
  const m = Math.floor(seconds / 60);
  const s = String(seconds % 60).padStart(2, "0");
  return `${m}:${s}`;
}

const secret = "only this file can see me";

module.exports = { formatLength };
