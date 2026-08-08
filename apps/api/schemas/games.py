"""
Games Schemas
==============
Pydantic models for vocabulary and quiz games.
"""

import logging

logger = logging.getLogger(__name__)
from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


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
    pronunciation: str | None = Field(None, max_length=100)
    example: str | None = None
    category: WordCategoryEnum = WordCategoryEnum.AGRICULTURE
    part_of_speech: str | None = Field(None, max_length=30)


class VocabularyWordCreate(VocabularyWordBase):
    pass


class VocabularyWordUpdate(BaseModel):
    word: str | None = Field(None, min_length=1, max_length=100)
    translation: str | None = Field(None, min_length=1, max_length=255)
    pronunciation: str | None = None
    example: str | None = None
    category: WordCategoryEnum | None = None
    part_of_speech: str | None = None
    is_active: bool | None = None


class VocabularyWordResponse(VocabularyWordBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    is_active: bool
    created_at: datetime


class VocabularyWordListResponse(BaseModel):
    items: list[VocabularyWordResponse]
    total: int
    skip: int = 0
    limit: int = 100


class QuizQuestionBase(BaseModel):
    question_text: str = Field(..., min_length=1)
    option_a: str = Field(..., min_length=1, max_length=255)
    option_b: str = Field(..., min_length=1, max_length=255)
    option_c: str | None = Field(None, max_length=255)
    option_d: str | None = Field(None, max_length=255)
    correct_answer: str = Field(..., pattern="^[a-dA-D]$")
    points: int = Field(1, ge=1)
    order: int = Field(0, ge=0)


class QuizQuestionCreate(QuizQuestionBase):
    pass


class QuizQuestionUpdate(BaseModel):
    question_text: str | None = None
    option_a: str | None = None
    option_b: str | None = None
    option_c: str | None = None
    option_d: str | None = None
    correct_answer: str | None = None
    points: int | None = None
    order: int | None = None


class QuizQuestionResponse(QuizQuestionBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    quiz_id: int


class QuizBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: str | None = None
    category: WordCategoryEnum = WordCategoryEnum.AGRICULTURE
    difficulty: DifficultyLevelEnum = DifficultyLevelEnum.MEDIUM
    time_limit: int = Field(0, ge=0)


class QuizCreate(QuizBase):
    questions: list[QuizQuestionCreate] | None = Field(default_factory=list)


class QuizUpdate(BaseModel):
    title: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = None
    category: WordCategoryEnum | None = None
    difficulty: DifficultyLevelEnum | None = None
    time_limit: int | None = None
    is_active: bool | None = None


class QuizResponse(QuizBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    is_active: bool
    created_at: datetime
    questions: list[QuizQuestionResponse] = Field(default_factory=list)


class QuizListResponse(BaseModel):
    items: list[QuizResponse]
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
    items: list[QuizAttemptResponse]
    total: int
    skip: int = 0
    limit: int = 100


class GamesStats(BaseModel):
    total_vocabulary: int
    total_quizzes: int
    total_attempts: int
    by_category: dict[str, int]
    by_difficulty: dict[str, int]
