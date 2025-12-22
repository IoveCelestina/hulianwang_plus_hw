from pydantic import BaseModel, Field, field_validator

class AiRecommendation(BaseModel):
    dish_id: int
    reason: list[str] = Field(default_factory=list, max_length=6)
    fit_score: float = Field(ge=0.0, le=1.0)
    warnings: list[str] = Field(default_factory=list, max_length=6)

class AiComboItem(BaseModel):
    dish_id: int
    qty: int = Field(ge=1, le=99)

class AiCombo(BaseModel):
    enabled: bool = False
    items: list[AiComboItem] = Field(default_factory=list, max_length=10)
    total_estimate: float | None = None
    logic: str | None = None

class AiResponse(BaseModel):
    reply: str
    questions: list[str] = Field(default_factory=list, max_length=3)
    recommendations: list[AiRecommendation] = Field(default_factory=list, max_length=3)
    combo: AiCombo | None = None
