# Chapter 7: a messy line from a shop receipt. Run it and watch each method tidy it a little more.
line = "   MASALA chai x2   "

print(repr(line))
print(repr(line.strip()))
print(line.strip().lower())
print(line.strip().title())
print(line.split())
print(len(line), len(line.strip()))
