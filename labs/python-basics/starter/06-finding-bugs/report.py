# Chapter 6: this program crashes on the second day. Run it and read the traceback from the bottom up.
def average(amounts):
    return sum(amounts) / len(amounts)


def summary(day, amounts):
    return f"{day}: average {average(amounts):.2f}"


print(summary("Monday", [120, 80, 100]))
print(summary("Tuesday", []))
