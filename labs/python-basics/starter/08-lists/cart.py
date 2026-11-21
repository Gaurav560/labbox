# Chapter 8: a shopping cart is a list. Run it, then try your own changes.
cart = ["tea", "milk", "bread"]
print(cart, len(cart))

cart.append("eggs")
print(cart)

cart.remove("milk")
print(cart)

print(cart[0], cart[-1], cart[1:3])
print("tea" in cart, "rice" in cart)
