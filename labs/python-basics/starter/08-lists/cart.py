# Chapter 8: a shopping cart is a list. Run it, then try your own changes.
cart = ["rice", "milk", "bread"]
print(cart, len(cart))

cart.append("eggs")
print(cart)

cart.remove("milk")
print(cart)

print(cart[0], cart[-1], cart[1:3])
print("rice" in cart, "salt" in cart)
