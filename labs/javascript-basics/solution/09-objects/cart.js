// Chapter 9: objects.

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

if (require.main === module) {
  console.log(cartTotal([{ price: 20, qty: 2 }, { price: 15, qty: 1 }]));
  console.log(withDiscount({ name: "jelly", price: 20 }, 10));
}

module.exports = { cartTotal, withDiscount };
