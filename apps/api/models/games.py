"""
Games Models
============
Database models for vocabulary and quiz games.
"""

import logging

logger = logging.getLogger(__name__)
from datetime import datetime
from enum import Enum as PyEnum

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from apps.shared_core.database.session import Base


class QuestionType(str, PyEnum):
    """Question type enumeration."""

    MULTIPLE_CHOICE = "multiple_choice"
    TRUE_FALSE = "true_false"
    SHORT_ANSWER = "short_answer"


class QuizDifficulty(str, PyEnum):
    """Quiz difficulty enumeration."""

    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class WordDifficulty(str, PyEnum):
    """Word difficulty enumeration."""

    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class WordCategory(str, PyEnum):
    """Word category enumeration."""

    AGRICULTURE = "agriculture"
    WATER = "water"
    ENVIRONMENT = "environment"
    ECONOMICS = "economics"
    TECHNOLOGY = "technology"


# Backward compatibility alias
DifficultyLevel = QuizDifficulty


class VocabularyWord(Base):
    """Vocabulary word for language learning."""

    __tablename__ = "vocabulary_words"

    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    word: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    definition: Mapped[str | None] = mapped_column(Text, nullable=True)
    translation: Mapped[str] = mapped_column(String(255), nullable=False)
    pronunciation: Mapped[str | None] = mapped_column(String(100), nullable=True)
    example: Mapped[str | None] = mapped_column(Text, nullable=True)
    category: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    difficulty: Mapped[str] = mapped_column(String(30), default="medium", nullable=False)
    part_of_speech: Mapped[str | None] = mapped_column(String(30), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self) -> str:
        """Handle __repr__."""
        return f"<VocabularyWord(id={self.id}, word={self.word!r})>"


class Quiz(Base):
    """Quiz/Question model."""

    __tablename__ = "quizzes"

    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    category: Mapped[str | None] = mapped_column(String(50), nullable=True, index=True)
    difficulty: Mapped[str] = mapped_column(String(30), default="medium", nullable=False)
    time_limit: Mapped[int] = mapped_column(
        Integer, default=0, nullable=False
    )  # seconds, 0 = no limit
    time_limit_minutes: Mapped[int | None] = mapped_column(Integer, nullable=True)  # minutes
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    questions: Mapped[list["QuizQuestion"]] = relationship(
        "QuizQuestion", back_populates="quiz", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        """Handle __repr__."""
        return f"<Quiz(id={self.id}, title={self.title!r})>"


class QuizQuestion(Base):
    """Question within a quiz."""

    __tablename__ = "quiz_questions"

    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    quiz_id: Mapped[str] = mapped_column(
        String(50), ForeignKey("quizzes.id"), nullable=False, index=True
    )
    question_text: Mapped[str] = mapped_column(Text, nullable=False)
    question_type: Mapped[str] = mapped_column(
        String(30), default="multiple_choice", nullable=False
    )
    options: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON array of options
    option_a: Mapped[str | None] = mapped_column(String(255), nullable=True)
    option_b: Mapped[str | None] = mapped_column(String(255), nullable=True)
    option_c: Mapped[str | None] = mapped_column(String(255), nullable=True)
    option_d: Mapped[str | None] = mapped_column(String(255), nullable=True)
    correct_answer: Mapped[str] = mapped_column(
        String(10), nullable=False
    )  # 'a', 'b', 'c', 'd', or index
    points: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Relationships
    quiz: Mapped["Quiz"] = relationship("Quiz", back_populates="questions")

    def __repr__(self) -> str:
        """Handle __repr__."""
        return f"<QuizQuestion(id={self.id}, quiz_id={self.quiz_id})>"


class QuizAttempt(Base):
    """User's quiz attempt/score."""

    __tablename__ = "quiz_attempts"

    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    quiz_id: Mapped[str] = mapped_column(
        String(50), ForeignKey("quizzes.id"), nullable=False, index=True
    )
    user_id: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)  # percentage 0-100
    total_questions: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    correct_answers: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    total_points: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    percentage: Mapped[int] = mapped_column(Integer, default=0, nullable=False)  # 0-100
    time_taken: Mapped[int] = mapped_column(Integer, default=0, nullable=False)  # seconds
    completed_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )

    # Relationships
    quiz: Mapped["Quiz"] = relationship("Quiz")

    def __repr__(self) -> str:
        """Handle __repr__."""
        return f"<QuizAttempt(quiz_id={self.quiz_id}, user_id={self.user_id}, score={self.score})>"
