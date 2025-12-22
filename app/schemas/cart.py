from pydantic import BaseModel

class CartItemIn(BaseModel):
    dish_id: int
    quantity: int
    selected_specs: dict = {}

class CartItemUpdateIn(BaseModel):
    quantity: int | None = None
    selected_specs: dict | None = None

class CartItemOut(BaseModel):
    id: int
    dish_id: int
    dish_name: str
    price: float
    quantity: int
    selected_specs: dict

class CartOut(BaseModel):
    items: list[CartItemOut]
    total_amount: float
