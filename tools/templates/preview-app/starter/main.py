from fastapi import FastAPI, HTTPException

app = FastAPI(title="Ravi's Snack Corner")

# Prices in rupees.
MENU = {"corn cutlet": 15, "fried idli": 20, "bun maska": 30, "vada pav": 25}


@app.get("/")
def home():
    return {"message": "Welcome to Ravi's Snack Corner"}


# TODO (task menu): GET /menu returns {"items": [...]} with every item name, A to Z.


# TODO (task price): GET /menu/{item} returns {"item": item, "price": price}.
#                    An item that is not on the menu returns 404.
