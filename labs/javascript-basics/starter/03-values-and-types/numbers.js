// Chapter 3: numbers and text.

function percent(scored, total) {
  // TODO (task percent): scored as a percentage of total, one decimal; 0 when total is 0
  return -1;
}

function formatRupees(paise) {
  // TODO (task format_rupees): 1250 paise becomes "₹12.50"
  return "";
}

if (require.main === module) {
  console.log(percent(45, 50), percent(1, 3), percent(7, 0));
  console.log(formatRupees(1250), formatRupees(5));
}

module.exports = { percent, formatRupees };
