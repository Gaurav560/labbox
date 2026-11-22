# Chapter 14: Pocket's diary. "w" starts the file fresh, "a" adds to the end. Run it twice: same result?
with open("diary.txt", "w") as f:
    f.write("juice 15\n")
    f.write("bus 30\n")

with open("diary.txt", "a") as f:
    f.write("lunch 120\n")

with open("diary.txt") as f:
    for line in f:
        print(line.strip().split())
