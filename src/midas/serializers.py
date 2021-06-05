from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, AnyHttpUrl


class Company(BaseModel):
    name: Optional[str]
    url: Optional[AnyHttpUrl]


class Salary(BaseModel):
    value: int = 'Не указанна'
    maximum: float = 0
    minimum: float = 0


class Offer(BaseModel):
    offer_id: str
    title: str
    url: AnyHttpUrl
    company: Company
    city: str
    salary: Salary
    created_at: datetime
    tags: List[str] = []
