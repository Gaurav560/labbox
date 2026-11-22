// Chapter 17: how long a song or a playlist is. This code is correct: your job is to write tests that prove it.

/** 245 seconds is "4:05"; an hour or more shows hours too: 3725 seconds is "1:02:05". Negative seconds throw. */
function formatDuration(seconds) {
  if (seconds < 0) {
    throw new RangeError(`seconds cannot be negative: ${seconds}`);
  }
  const h = Math.floor(seconds / 3600);
  const m = Math.floor((seconds % 3600) / 60);
  const s = String(seconds % 60).padStart(2, "0");
  if (h > 1) {
    return `${h}:${String(m).padStart(2, "0")}:${s}`;
  }
  return `${m}:${s}`;
}

module.exports = { formatDuration };
