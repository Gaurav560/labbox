// Chapter 3: making decisions.

function grade(marks) {
  if (marks < 0 || marks > 100) {
    return "Invalid";
  }
  if (marks >= 80) {
    return "A";
  } else if (marks >= 60) {
    return "B";
  } else if (marks >= 40) {
    return "C";
  }
  return "F";
}

function isLeapYear(year) {
  return (year % 4 === 0 && year % 100 !== 0) || year % 400 === 0;
}

module.exports = { grade, isLeapYear };
