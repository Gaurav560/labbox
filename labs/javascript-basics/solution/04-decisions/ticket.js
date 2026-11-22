// Chapter 4: a concert ticket price, decided step by step.
function ticketPrice(age) {
  if (age < 0) {
    return "Invalid";
  } else if (age < 5) {
    return 0;
  } else if (age < 18) {
    return 250;
  } else {
    return 500;
  }
}

console.log(ticketPrice(3), ticketPrice(5), ticketPrice(17), ticketPrice(18), ticketPrice(-2));
