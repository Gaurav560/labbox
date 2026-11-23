# Chapter 8: a shopping cart is a list. Run it, then try your own changes.
cart = ["rice", "mint", "bread"]
print(cart, len(cart))

cart.append("eggs")
print(cart)

cart.remove("mint")
print(cart)

print(cart[0], cart[-1], cart[1:3])
print("rice" in cart, "salt" in cart)
