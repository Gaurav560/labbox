// Chapter 18: the capstone, a monthly report.
const fs = require("node:fs");

const round2 = (n) => Math.round(n * 100) / 100;

function readRows(path) {
  const lines = fs.readFileSync(path, "utf8").split("\n");
  const rows = [];
  lines.forEach((line, i) => {
    if (i === 0 || line.trim() === "") {
      return; // the header, or a blank line
    }
    const [date, category, amountText] = line.trim().split(",");
    const amount = Number(amountText);
    const good = Boolean(category) && amountText !== undefined && amountText.trim() !== "" && !Number.isNaN(amount);
    rows.push({ lineNumber: i + 1, date, category, amount, good });
  });
  return rows;
}

function readTotals(path) {
  const totals = {};
  for (const row of readRows(path)) {
    if (row.good) {
      totals[row.category] = round2((totals[row.category] ?? 0) + row.amount);
    }
  }
  return totals;
}

function monthlyReport(path) {
  const rows = readRows(path);
  const good = rows.filter((r) => r.good);
  const total = round2(good.reduce((sum, r) => sum + r.amount, 0));
  const perCategory = {};
  for (const r of good) {
    perCategory[r.category] = round2((perCategory[r.category] ?? 0) + r.amount);
  }
  return {
    total,
    count: good.length,
    average: good.length === 0 ? 0 : round2(total / good.length),
    perCategory,
    badLines: rows.filter((r) => !r.good).map((r) => r.lineNumber),
  };
}

if (require.main === module) {
  const report = monthlyReport("expenses.csv");
  console.log(`total ${report.total}, ${report.count} rows, average ${report.average}`);
  console.log(`rent ${report.perCategory.rent}, food ${report.perCategory.food}`);
  console.log(`bad lines ${JSON.stringify(report.badLines)}`);
}

module.exports = { readTotals, monthlyReport };
