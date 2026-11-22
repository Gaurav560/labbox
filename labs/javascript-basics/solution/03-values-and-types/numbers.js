// Chapter 3: numbers and text.

function percent(scored, total) {
  if (total === 0) {
    return 0;
  }
  return Math.round((scored / total) * 1000) / 10;
}

function formatRupees(paise) {
  return `₹${(paise / 100).toFixed(2)}`;
}

if (require.main === module) {
  console.log(percent(45, 50), percent(1, 3), percent(7, 0));
  console.log(formatRupees(1250), formatRupees(5));
}

module.exports = { percent, formatRupees };
