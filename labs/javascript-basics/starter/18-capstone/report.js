// Chapter 18: the capstone, a monthly report.
const fs = require("node:fs");

function readTotals(path) {
  // TODO (task read_totals): the total per category from a CSV file, rounded to 2 decimals;
  // skip the header, blank lines, rows without a category and amounts that are not numbers
  return {};
}

function monthlyReport(path) {
  // TODO (task monthly_report): { total, count, average, perCategory, badLines }
  return { total: 0, count: 0, average: 0, perCategory: {}, badLines: [] };
}

if (require.main === module) {
  const report = monthlyReport("expenses.csv");
  console.log(`total ${report.total}, ${report.count} rows, average ${report.average}`);
  console.log(`rent ${report.perCategory.rent}, food ${report.perCategory.food}`);
  console.log(`bad lines ${JSON.stringify(report.badLines)}`);
}

module.exports = { readTotals, monthlyReport };
