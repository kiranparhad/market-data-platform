from pydantic import BaseModel, Field, field_validator
from enum import Enum
from datetime import datetime, timezone
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

    @field_validator("timestamp", mode="before")
    @classmethod
    def normalize_timestamp(cls, value):
        if isinstance(value, str):
            value = datetime.fromisoformat(value)

        if isinstance(value, datetime) and value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)

        return value
