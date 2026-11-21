# Chapter 12: where do names live? Run it and compare the two prints of total.
total = 100


def add_tip(amount):
    total = amount + 10
    print("inside:", total)
    return total


add_tip(50)
print("outside:", total)
