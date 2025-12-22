from pydantic import BaseModel, Field


class OrderCreateItemIn(BaseModel):
    dish_id: int
    quantity: int = Field(ge=1, le=99)
    selected_specs: dict = {}


class OrderCreateIn(BaseModel):
    address_id: int
    note: str | None = None
    items: list[OrderCreateItemIn]


class OrderCreateOut(BaseModel):
    order_id: int
    status: str
    total_amount: float


class OrderListItem(BaseModel):
    id: int
    status: str
    total_amount: float
    created_at: str | None = None


class OrderListOut(BaseModel):
    items: list[OrderListItem]
    total: int


class OrderItemOut(BaseModel):
    id: int
    dish_id: int
    dish_name: str
    quantity: int
    price_snapshot: float
    selected_specs: dict


class OrderDetailOut(BaseModel):
    id: int
    status: str
    total_amount: float
    note: str | None
    created_at: str | None
    address_snapshot: dict
    items: list[OrderItemOut]
