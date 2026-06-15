"""Psychology Domain Schemas."""
from pydantic import BaseModel, Field
from typing import List
from datetime import datetime


class TestSubmission(BaseModel):
    user_id: str
    test_id: str
    answers: List[int] = Field(..., min_items=1)


class TestResultResponse(BaseModel):
    user_id: str
    test_id: str
    score: float
    interpretation: str
    recommendations: List[str]
    timestamp: datetime
