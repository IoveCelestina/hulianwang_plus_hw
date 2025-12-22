from pydantic import BaseModel


class PreferencesOut(BaseModel):
    explicit_tags: list[str]
    implicit_profile: dict
    dietary_restrictions: list[str]


class PreferencesUpdateIn(BaseModel):
    explicit_tags: list[str] | None = None
    dietary_restrictions: list[str] | None = None


class AddressIn(BaseModel):
    contact_name: str
    phone: str
    address_line: str
    is_default: bool = False


class AddressOut(BaseModel):
    id: int
    contact_name: str
    phone: str
    address_line: str
    is_default: bool
