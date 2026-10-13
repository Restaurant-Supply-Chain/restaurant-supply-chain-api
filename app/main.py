from fastapi import FastAPI, HTTPException
from schemas import RestaurantCreate, OutletCreate, AddressCreate

app = FastAPI()

restaurants = [{"id": 1, "name": "ABC Restaurant", "cuisine_type": "South Indian", "location": "Chennai", "phone": "9876543210", "status": "ACTIVE"},
    {"id": 2, "name": "Green Leaf Restaurant", "cuisine_type": "North Indian", "location": "Coimbatore", "phone": "9876543211", "status": "ACTIVE"},
    {"id": 3, "name": "Spicy Hub", "cuisine_type": "Chinese", "location": "Madurai", "phone": "9876543212", "status": "ACTIVE"},
    {"id": 4, "name": "Royal Meals", "cuisine_type": "Tamil Meals", "location": "Namakkal", "phone": "9876543213", "status": "ACTIVE"},
    {"id": 5, "name": "Food Palace", "cuisine_type": "Italian", "location": "Salem", "phone": "9876543214", "status": "ACTIVE"},
    {"id": 6, "name": "Fresh Bites", "cuisine_type": "Fast Food", "location": "Trichy", "phone": "9876543215", "status": "ACTIVE"},
    {"id": 7, "name": "Spice Garden", "cuisine_type": "Chettinad", "location": "Karaikudi", "phone": "9876543216", "status": "ACTIVE"},
    {"id": 8, "name": "Burger Point", "cuisine_type": "American", "location": "Bangalore", "phone": "9876543217", "status": "ACTIVE"},
    {"id": 9, "name": "Ocean Delight", "cuisine_type": "Seafood", "location": "Pondicherry", "phone": "9876543218", "status": "ACTIVE"},
    {"id": 10, "name": "Morning Fresh Cafe", "cuisine_type": "Cafe", "location": "Erode", "phone": "9876543219", "status": "ACTIVE"}]
outlets = []
addresses = []


@app.get("/")
def homes():
    return {"message": "Restaurant API   nisa running"}

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