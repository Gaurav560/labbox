# Chapter 5: loops. Pocket goes through a whole list of amounts, one at a time.


def count_above(amounts, limit):
    count = 0
    for amount in amounts:
        if amount > limit:
            count = count + 1
    return count


def first_negative(amounts):
    for amount in amounts:
        if amount < 0:
            return amount
    return None
