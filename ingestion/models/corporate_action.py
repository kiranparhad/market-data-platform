from pydantic import BaseModel, Field
from enum import Enum
from datetime import date
from typing import Optional


class ActionType(str, Enum):
    SPLIT = "SPLIT"
    ADDITION = "ADDITION"
    REMOVAL = "REMOVAL"


class Status(str, Enum):
    CONFIRMED = "CONFIRMED"
    PENDING = "PENDING"


class CorporateAction(BaseModel):
    action_id: str
    ticker: str
    action_type: ActionType
    ratio: Optional[float] = Field(None, gt=0)
    index_id: Optional[str] = None
    effective_date: date
    announced_date: date
    status: Status
