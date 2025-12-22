from pydantic import BaseModel, Field

class OK(BaseModel):
    ok: bool = True
