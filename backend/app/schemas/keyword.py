from pydantic import BaseModel
from typing import List, Optional
from uuid import UUID


class KeywordSearchRequest(BaseModel):
    keyword: str


class KeywordResult(BaseModel):
    keyword: str
    search_volume: int
    competition_score: float
    opportunity_score: int
    related_keywords: List[str]
