from pydantic import BaseModel, Field


class ReviewCreateIn(BaseModel):
    order_id: int
    dish_id: int
    rating: int = Field(ge=1, le=5)
    comment: str | None = None
    tags: list[str] = []


class ReviewOut(BaseModel):
    id: int
    user_id: int
    dish_id: int
    order_id: int
    rating: int
    comment: str | None
    tags: list[str]
    created_at: str | None = None


class ReviewListOut(BaseModel):
    items: list[ReviewOut]
    total: int
