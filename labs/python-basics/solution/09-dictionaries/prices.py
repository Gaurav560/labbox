# Chapter 9: a price list is a dictionary: each item name is a key, each price its value.
prices = {"jelly": 15, "samosa": 20, "cookie": 30}

print(prices["jelly"])
prices["vada"] = 25
prices["jelly"] = 18
print(prices)

for item, price in prices.items():
    print(f"{item:<8} ₹{price}")

print(prices.get("cake", 0))
print(prices["cake"])
