from pydantic import BaseModel, Field, field_validator
from enum import Enum
from datetime import datetime
from decimal import Decimal

class TickType(str, Enum):
    TRADE = "TRADE"
    BID = "BID"
    ASK = "ASK"


class TickEvent(BaseModel):
    ticker: str
    price: Decimal = Field(gt=0, description="Must be positive")
    volume: int = Field(ge=0)
    tick_type: TickType
    source_id: str
    source_name: str
    timestamp: datetime

    @field_validator("timestamp")
    @classmethod
    def require_timezone(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("timestamp must include timezone information")
        return value
