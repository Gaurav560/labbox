# Chapter 11: a week of spending. Sort it, filter it, transform it.
amounts = [120, 45, 900, 300, 80]

print(sorted(amounts))
print(sorted(amounts, reverse=True))
print(amounts)

doubled = [a * 2 for a in amounts]
print(doubled)

big = [a for a in amounts if a > 100]
print(big)

words = ["samosa", "pav", "biryani"]
print(sorted(words, key=len))
