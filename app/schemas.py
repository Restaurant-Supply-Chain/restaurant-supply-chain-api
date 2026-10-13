from pydantic import BaseModel


class RestaurantCreate(BaseModel):
    name: str
    cuisine_type: str
    contact_phone: str


class OutletCreate(BaseModel):
    restaurant_id: int
    name: str
    outlet_code: str


class AddressCreate(BaseModel):
    owner_type: str
    owner_id: int
    line1: str
    city: str
    state: str
    pincode: str