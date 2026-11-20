// Chapter 2: numbers and text.

function percent(scored, total) {
  if (total === 0) {
    return 0;
  }
  return Math.round((scored / total) * 1000) / 10;
}

function formatRupees(paise) {
  return `₹${(paise / 100).toFixed(2)}`;
}

module.exports = { percent, formatRupees };
