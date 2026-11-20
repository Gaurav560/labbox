# Chapter 9: functions in depth.


# TODO (task add_item): this has a famous bug. Every call without a basket shares one list.
def add_item(item, basket=[]):
    basket.append(item)
    return basket


# TODO (task total): total(*prices, discount=0): the sum minus discount percent, rounded to 2, a float.
