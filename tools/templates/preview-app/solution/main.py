from fastapi import FastAPI, HTTPException

app = FastAPI(title="Ravi's Tapri")

# Prices in rupees.
MENU = {"cutting chai": 15, "masala chai": 20, "bun maska": 30, "vada pav": 25}


@app.get("/")
def home():
    return {"message": "Welcome to Ravi's Tapri"}


@app.get("/menu")
def menu():
    return {"items": sorted(MENU)}


@app.get("/menu/{item}")
def price(item: str):
    if item not in MENU:
        raise HTTPException(status_code=404, detail=f"{item} is not on the menu")
    return {"item": item, "price": MENU[item]}
