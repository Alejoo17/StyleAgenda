from decimal import Decimal
from pydantic import BaseModel, ConfigDict, Field


class ServiceCreate(BaseModel):
    name: str
    description: str = ""
    duration_minutes: int = Field(gt=0)
    base_price: Decimal = Field(gt=0)


class ServiceRead(ServiceCreate):
    model_config = ConfigDict(from_attributes=True)
    id: int
    active: bool
