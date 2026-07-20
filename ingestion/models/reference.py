from pydantic import BaseModel, Field
from datetime import date
from typing import List


class Constituent(BaseModel):
    ticker: str
    company_name: str
    weight: float = Field(ge=0, le=1)
    shares_outstanding: int = Field(ge=0)
    sector: str


class ReferenceData(BaseModel):
    index_id: str
    effective_date: date
    version: int = Field(gt=0, description="Version should be > 0")
    constituents: List[Constituent]
