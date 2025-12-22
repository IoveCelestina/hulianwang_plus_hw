from pydantic import BaseModel

class CategoryOut(BaseModel):
    id: int
    name: str
    sort_order: int

class DishListItem(BaseModel):
    id: int
    name: str
    price: float
    image_url: str | None
    status: str
    rating_avg: float
    rating_count: int
    sales_count: int
    ai_highlights: list[str] = []

class DishListOut(BaseModel):
    items: list[DishListItem]
    total: int

class DishSpecOut(BaseModel):
    id: int
    spec_name: str
    spec_values: list

class DishDetailOut(BaseModel):
    id: int
    category_id: int | None
    name: str
    description: str | None
    price: float
    image_url: str | None
    status: str
    rating_avg: float
    rating_count: int
    sales_count: int
    ai_metadata: dict
    specs: list[DishSpecOut]
