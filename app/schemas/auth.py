from pydantic import BaseModel, Field

class RegisterIn(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=6, max_length=72)
    phone: str | None = None

class LoginIn(BaseModel):
    username: str
    password: str

class TokenOut(BaseModel):
    user_id: int
    access_token: str
    token_type: str = "bearer"

class MeOut(BaseModel):
    id: int
    username: str
    role: str
    created_at: str | None = None
