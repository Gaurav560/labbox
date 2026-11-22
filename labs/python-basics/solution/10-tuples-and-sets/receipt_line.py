# Chapter 10: a tuple is a small, fixed group of values. Unpacking gives each one a name.
line = ("Veg sandwich", 2, 45.0)
name, quantity, price = line
print(name, "x", quantity, "=", quantity * price)
print(line[0], len(line))
line[1] = 3
