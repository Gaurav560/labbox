# Chapter 15: one class, two objects. Each object keeps its own values.
class Item:
    def __init__(self, name, price):
        self.name = name
        self.price = price

    def with_tax(self, percent):
        return round(self.price * (100 + percent) / 100, 2)


tea = Item("tea", 15)
cake = Item("cake", 40)
print(tea.name, tea.price)
print(cake.name, cake.with_tax(5))
cake.price = 45
print(cake.price, tea.price)
print(type(tea))
