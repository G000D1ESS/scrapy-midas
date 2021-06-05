from datetime import datetime
from typing import List, Optional, Dict

from pydantic import BaseModel, AnyHttpUrl


class Company(BaseModel):
    name: Optional[str]
    url: Optional[AnyHttpUrl]


class Salary(BaseModel):
    value: float = 0
    maximum: float = 0
    minimum: float = 0


class Offer(BaseModel):
    offer_id: str
    title: str
    url: AnyHttpUrl
    company: Company
    city: str
    salary: Salary
    info: Dict[str, str]
    created_at: datetime
    tags: List[str] = []
