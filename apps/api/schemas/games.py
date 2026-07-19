"""
Games Schemas
==============
Pydantic models for vocabulary and quiz games.
"""

from datetime import datetime
from typing import Optional, List
from enum import Enum

from pydantic import BaseModel, Field, ConfigDict


class WordCategoryEnum(str, Enum):
    AGRICULTURE = "agriculture"
    WATER = "water"
    ENVIRONMENT = "environment"
    ECONOMICS = "economics"
    TECHNOLOGY = "technology"


class DifficultyLevelEnum(str, Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class VocabularyWordBase(BaseModel):
    word: str = Field(..., min_length=1, max_length=100)
    translation: str = Field(..., min_length=1, max_length=255)
    pronunciation: Optional[str] = Field(None, max_length=100)
    example: Optional[str] = None
    category: WordCategoryEnum = WordCategoryEnum.AGRICULTURE
    part_of_speech: Optional[str] = Field(None, max_length=30)


class VocabularyWordCreate(VocabularyWordBase):
    pass


class VocabularyWordUpdate(BaseModel):
    word: Optional[str] = Field(None, min_length=1, max_length=100)
    translation: Optional[str] = Field(None, min_length=1, max_length=255)
    pronunciation: Optional[str] = None
    example: Optional[str] = None
    category: Optional[WordCategoryEnum] = None
    part_of_speech: Optional[str] = None
    is_active: Optional[bool] = None


class VocabularyWordResponse(VocabularyWordBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    is_active: bool
    created_at: datetime


class VocabularyWordListResponse(BaseModel):
    items: List[VocabularyWordResponse]
    total: int
    skip: int = 0
    limit: int = 100


class QuizQuestionBase(BaseModel):
    question_text: str = Field(..., min_length=1)
    option_a: str = Field(..., min_length=1, max_length=255)
    option_b: str = Field(..., min_length=1, max_length=255)
    option_c: Optional[str] = Field(None, max_length=255)
    option_d: Optional[str] = Field(None, max_length=255)
    correct_answer: str = Field(..., pattern="^[a-dA-D]$")
    points: int = Field(1, ge=1)
    order: int = Field(0, ge=0)


class QuizQuestionCreate(QuizQuestionBase):
    pass


class QuizQuestionUpdate(BaseModel):
    question_text: Optional[str] = None
    option_a: Optional[str] = None
    option_b: Optional[str] = None
    option_c: Optional[str] = None
    option_d: Optional[str] = None
    correct_answer: Optional[str] = None
    points: Optional[int] = None
    order: Optional[int] = None


class QuizQuestionResponse(QuizQuestionBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    quiz_id: int


class QuizBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    category: WordCategoryEnum = WordCategoryEnum.AGRICULTURE
    difficulty: DifficultyLevelEnum = DifficultyLevelEnum.MEDIUM
    time_limit: int = Field(0, ge=0)


class QuizCreate(QuizBase):
    questions: Optional[List[QuizQuestionCreate]] = Field(default_factory=list)


class QuizUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    category: Optional[WordCategoryEnum] = None
    difficulty: Optional[DifficultyLevelEnum] = None
    time_limit: Optional[int] = None
    is_active: Optional[bool] = None


class QuizResponse(QuizBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    is_active: bool
    created_at: datetime
    questions: List[QuizQuestionResponse] = Field(default_factory=list)


class QuizListResponse(BaseModel):
    items: List[QuizResponse]
    total: int
    skip: int = 0
    limit: int = 100


class QuizAttemptBase(BaseModel):
    user_id: int = Field(..., gt=0)


class QuizAttemptCreate(QuizAttemptBase):
    pass


class QuizAttemptResponse(QuizAttemptBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    quiz_id: int
    score: int
    total_points: int
    percentage: int
    time_taken: int
    completed_at: datetime


class QuizAttemptListResponse(BaseModel):
    items: List[QuizAttemptResponse]
    total: int
    skip: int = 0
    limit: int = 100


class GamesStats(BaseModel):
    total_vocabulary: int
    total_quizzes: int
    total_attempts: int
    by_category: dict[str, int]
    by_difficulty: dict[str, int]