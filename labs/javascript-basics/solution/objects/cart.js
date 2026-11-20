// Chapter 7: objects.

function cartTotal(cart) {
  let total = 0;
  for (const line of cart) {
    total += line.price * line.qty;
  }
  return total;
}

function withDiscount(item, percent) {
  return { ...item, price: Math.round(item.price * (100 - percent)) / 100 };
}

module.exports = { cartTotal, withDiscount };
