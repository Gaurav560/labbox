// Chapter 9: objects.

function cartTotal(cart) {
  // TODO (task cart_total): add up price times qty for every line of the cart
  return 0;
}

function withDiscount(item, percent) {
  // TODO (task with_discount): a NEW item with the price lowered by percent; leave item alone
  return item;
}

if (require.main === module) {
  console.log(cartTotal([{ price: 20, qty: 2 }, { price: 15, qty: 1 }]));
  console.log(withDiscount({ name: "jelly", price: 20 }, 10));
}

module.exports = { cartTotal, withDiscount };
