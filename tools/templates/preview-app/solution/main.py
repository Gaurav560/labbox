from fastapi import FastAPI, HTTPException

app = FastAPI(title="Ravi's Snack Corner")

# Prices in rupees.
MENU = {"corn cutlet": 15, "fried idli": 20, "bun maska": 30, "vada pav": 25}


@app.get("/")
def home():
    return {"message": "Welcome to Ravi's Snack Corner"}


@app.get("/menu")
def menu():
    return {"items": sorted(MENU)}


@app.get("/menu/{item}")
def price(item: str):
    if item not in MENU:
        raise HTTPException(status_code=404, detail=f"{item} is not on the menu")
    return {"item": item, "price": MENU[item]}
