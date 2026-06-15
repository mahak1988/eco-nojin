"""Psychology Domain Models."""
from dataclasses import dataclass
from typing import Optional, List
from datetime import datetime


@dataclass
class PsychologicalTest:
    test_id: str
    name: str
    description: str
    questions: List[dict]
    scoring_method: str


@dataclass
class TestResult:
    user_id: str
    test_id: str
    answers: List[int]
    score: float
    interpretation: str
    timestamp: datetime
