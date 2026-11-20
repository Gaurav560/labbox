// Chapter 10: errors.

function parseAge(text) {
  const trimmed = String(text).trim();
  if (!/^\d+$/.test(trimmed)) {
    throw new TypeError(`not a whole number: "${text}"`);
  }
  const age = Number(trimmed);
  if (age > 150) {
    throw new RangeError(`age must be 0 to 150: ${age}`);
  }
  return age;
}

function safeSum(values) {
  let total = 0;
  const bad = [];
  for (const v of values) {
    const n = Number(v);
    if (v.trim() === "" || Number.isNaN(n)) {
      bad.push(v);
    } else {
      total += n;
    }
  }
  return { total, bad };
}

module.exports = { parseAge, safeSum };
