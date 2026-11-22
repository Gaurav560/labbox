// Chapter 4: making decisions.

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

if (require.main === module) {
  console.log(grade(80), grade(79), grade(39), grade(101));
  console.log(isLeapYear(2024), isLeapYear(1900), isLeapYear(2000));
}

module.exports = { grade, isLeapYear };
