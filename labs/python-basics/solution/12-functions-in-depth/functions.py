# Chapter 12: functions in depth.


def add_item(item, basket=None):
    if basket is None:
        basket = []
    basket.append(item)
    return basket


def total(*prices, discount=0):
    return float(round(sum(prices) * (100 - discount) / 100, 2))
