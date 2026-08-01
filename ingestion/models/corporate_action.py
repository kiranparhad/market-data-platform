from datetime import date
from decimal import Decimal
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, model_validator


class ActionType(str, Enum):
    SPLIT = "SPLIT"
    ADDITION = "ADDITION"
    REMOVAL = "REMOVAL"


class Status(str, Enum):
    CONFIRMED = "CONFIRMED"
    PENDING = "PENDING"


class CorporateAction(BaseModel):
    action_id: str = Field(min_length=1)
    ticker: str = Field(min_length=1)
    action_type: ActionType
    ratio: Optional[Decimal] = Field(default=None, gt=0)
    index_id: Optional[str] = None
    effective_date: date
    announced_date: date
    status: Status

    @model_validator(mode="after")
    def validate_action_fields(self):
        if self.action_type == ActionType.SPLIT:
            if self.ratio is None:
                raise ValueError("ratio is required for SPLIT")
            if self.index_id is not None:
                raise ValueError("index_id is not applicable to SPLIT")

        if self.action_type in {ActionType.ADDITION, ActionType.REMOVAL}:
            if not self.index_id:
                raise ValueError("index_id is required for additions and removals")
            if self.ratio is not None:
                raise ValueError("ratio is only applicable to splits")

        if self.announced_date > self.effective_date:
            raise ValueError("announced_date cannot be after effective_date")

        return self
