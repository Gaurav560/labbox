# Chapter 10: who came to the shop on Monday and on Tuesday? Sets answer it in one line each.
monday = ["Asha", "Ravi", "Asha", "Meera"]
tuesday = ["Ravi", "Kabir", "Meera"]

print(len(monday), len(set(monday)))
print(sorted(set(monday)))
print("both days:", sorted(set(monday) & set(tuesday)))
print("either day:", sorted(set(monday) | set(tuesday)))
print("only Monday:", sorted(set(monday) - set(tuesday)))
