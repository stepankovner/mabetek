import re
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field, field_validator
from email_validator import validate_email, EmailNotValidError

Service = Literal["rail", "rent", "other"]
Kind = Literal["office", "warehouse"]

class LeadInput(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    name: str = Field(min_length=1, max_length=100)
    contact: str = Field(min_length=3, max_length=254)
    service: Service
    message: str = Field(default="", max_length=4000)
    consent: Literal[True]

    @field_validator("contact")
    @classmethod
    def valid_contact(cls, value):
        if any(ord(c) < 32 for c in value):
            raise ValueError("Invalid contact")
        if "@" in value:
            try:
                return validate_email(value, check_deliverability=False).normalized
            except EmailNotValidError as error:
                raise ValueError("Invalid email") from error
        if not re.fullmatch(r"\+?[\d ()-]+", value) or not 10 <= len(re.sub(r"\D", "", value)) <= 15:
            raise ValueError("Invalid phone")
        return value

class RentalOutput(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    slug: str
    title: str
    kind: Kind
    building: str
    description: str
    area: float | None
    floor: int | None
    monthly_price: int | None
    image_path: str
    available: bool
