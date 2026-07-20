from pydantic import BaseModel, Field
from enum import Enum
from datetime import datetime


class TickType(str, Enum):
    TRADE = "TRADE"
    BID = "BID"
    ASK = "ASK"


class TickEvent(BaseModel):
    ticker: str
    price: float = Field(gt=0, description="Must be positive")
    volume: int = Field(ge=0)
    tick_type: TickType
    source_id: str
    source_name: str
    timestamp: datetime
