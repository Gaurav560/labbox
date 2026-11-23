"""Thali House order helpers. Run the examples with: python3 orders.py"""
from collections import Counter

PRICES = {"veg thali": 120, "dal rice": 90, "paneer roll": 110, "curd rice": 80}


def total_bill(items, prices):
    return sum(prices[item] for item in items)


def top_dishes(orders, n):
    counts = Counter(orders)
    ranked = sorted(counts.items(), key=lambda pair: (-pair[1], pair[0]))
    return [dish for dish, _ in ranked[:n]]


def unique_areas(orders):
    return sorted({order["area"] for order in orders})


def route_order(stops):
    return [area for area, _ in sorted(stops, key=lambda stop: (stop[1], stop[0]))]


if __name__ == "__main__":
    print(total_bill(["veg thali", "dal rice", "veg thali"], PRICES))  # 330
    print(top_dishes(["dal rice", "veg thali", "dal rice"], 1))  # ['dal rice']
    print(unique_areas([{"dish": "dal rice", "area": "Baner"}, {"dish": "veg thali", "area": "Aundh"}]))
    print(route_order([("Baner", 7.5), ("Aundh", 3.0)]))  # ['Aundh', 'Baner']
