from fastapi import FastAPI, HTTPException
from app.schemas import RestaurantCreate, OutletCreate, AddressCreate

app = FastAPI(title="Restaurant Supply Chain API")

restaurants = []
outlets = []
addresses = []


@app.get("/")
def home():
    return {"message": "Restaurant API running"}


# Restaurant CRUD

@app.post("/restaurants/")
def add_restaurant(data: RestaurantCreate):
    restaurant = data.model_dump()
    restaurant["id"] = len(restaurants) + 1
    restaurants.append(restaurant)
    return restaurant


@app.get("/restaurants/")
def get_restaurants():
    return restaurants


@app.put("/restaurants/{id}")
def update_restaurant(id: int, data: RestaurantCreate):
    for r in restaurants:
        if r["id"] == id:
            r.update(data.model_dump())
            return r
    raise HTTPException(status_code=404, detail="Restaurant not found")


@app.delete("/restaurants/{id}")
def delete_restaurant(id: int):
    for r in restaurants:
        if r["id"] == id:
            restaurants.remove(r)
            return {"message": "Restaurant deleted"}
    raise HTTPException(status_code=404, detail="Restaurant not found")


# Outlet CRUD

@app.post("/outlets/")
def add_outlet(data: OutletCreate):
    outlet = data.model_dump()
    outlet["id"] = len(outlets) + 1
    outlets.append(outlet)
    return outlet


@app.get("/outlets/")
def get_outlets():
    return outlets


@app.put("/outlets/{id}")
def update_outlet(id: int, data: OutletCreate):
    for o in outlets:
        if o["id"] == id:
            o.update(data.model_dump())
            return o
    raise HTTPException(status_code=404, detail="Outlet not found")


@app.delete("/outlets/{id}")
def delete_outlet(id: int):
    for o in outlets:
        if o["id"] == id:
            outlets.remove(o)
            return {"message": "Outlet deleted"}
    raise HTTPException(status_code=404, detail="Outlet not found")


# Address CRUD

@app.post("/addresses/")
def add_address(data: AddressCreate):
    address = data.model_dump()
    address["id"] = len(addresses) + 1
    addresses.append(address)
    return address


@app.get("/addresses/")
def get_addresses():
    return addresses


@app.put("/addresses/{id}")
def update_address(id: int, data: AddressCreate):
    for a in addresses:
        if a["id"] == id:
            a.update(data.model_dump())
            return a
    raise HTTPException(status_code=404, detail="Address not found")


@app.delete("/addresses/{id}")
def delete_address(id: int):
    for a in addresses:
        if a["id"] == id:
            addresses.remove(a)
            return {"message": "Address deleted"}
    raise HTTPException(status_code=404, detail="Address not found")

