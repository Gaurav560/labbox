"""Dabba Express order helpers. Run the examples with: python3 orders.py"""

PRICES = {"veg thali": 120, "dal rice": 90, "paneer roll": 110, "curd rice": 80}


def total_bill(items, prices):
    # TODO (task total_bill): add up the price of every item. Repeated items count every time.
    pass


def top_dishes(orders, n):
    # TODO (task top_dishes): the n most ordered dishes, most first. Ties: A to Z.
    pass


def unique_areas(orders):
    # TODO (task unique_areas): every delivery area once, sorted A to Z.
    # Each order looks like {"dish": "veg thali", "area": "Kothrud"}.
    pass


def route_order(stops):
    # TODO (task route_order): area names from nearest to farthest. Same distance: A to Z.
    # Each stop is a tuple like ("Baner", 7.5).
    pass


if __name__ == "__main__":
    print(total_bill(["veg thali", "dal rice", "veg thali"], PRICES))  # 330
    print(top_dishes(["dal rice", "veg thali", "dal rice"], 1))  # ['dal rice']
    print(unique_areas([{"dish": "dal rice", "area": "Baner"}, {"dish": "veg thali", "area": "Aundh"}]))
    print(route_order([("Baner", 7.5), ("Aundh", 3.0)]))  # ['Aundh', 'Baner']
