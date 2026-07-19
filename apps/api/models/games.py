"""
Games Models
============
Database models for vocabulary and quiz games.
"""

from datetime import datetime
from typing import Optional, List

from sqlalchemy import String, Integer, DateTime, Boolean, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from apps.shared_core.database.session import Base


class VocabularyWord(Base):
    """Vocabulary word for language learning."""

    __tablename__ = "vocabulary_words"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    word: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    translation: Mapped[str] = mapped_column(String(255), nullable=False)
    pronunciation: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    example: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    category: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    part_of_speech: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self) -> str:
        return f"<VocabularyWord(id={self.id}, word={self.word!r})>"


class Quiz(Base):
    """Quiz/Question model."""

    __tablename__ = "quizzes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    category: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    difficulty: Mapped[str] = mapped_column(String(30), default="medium", nullable=False)
    time_limit: Mapped[int] = mapped_column(Integer, default=0, nullable=False)  # seconds, 0 = no limit
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    questions: Mapped[List["QuizQuestion"]] = relationship("QuizQuestion", back_populates="quiz", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Quiz(id={self.id}, title={self.title!r})>"


class QuizQuestion(Base):
    """Question within a quiz."""

    __tablename__ = "quiz_questions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    quiz_id: Mapped[int] = mapped_column(Integer, ForeignKey("quizzes.id"), nullable=False, index=True)
    question_text: Mapped[str] = mapped_column(Text, nullable=False)
    option_a: Mapped[str] = mapped_column(String(255), nullable=False)
    option_b: Mapped[str] = mapped_column(String(255), nullable=False)
    option_c: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    option_d: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    correct_answer: Mapped[str] = mapped_column(String(10), nullable=False)  # 'a', 'b', 'c', or 'd'
    points: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Relationships
    quiz: Mapped["Quiz"] = relationship("Quiz", back_populates="questions")

    def __repr__(self) -> str:
        return f"<QuizQuestion(id={self.id}, quiz_id={self.quiz_id})>"


class QuizAttempt(Base):
    """User's quiz attempt/score."""

    __tablename__ = "quiz_attempts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    quiz_id: Mapped[int] = mapped_column(Integer, ForeignKey("quizzes.id"), nullable=False, index=True)
    user_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    score: Mapped[int] = mapped_column(Integer, default=0, nullable=False)  # points earned
    total_points: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    percentage: Mapped[int] = mapped_column(Integer, default=0, nullable=False)  # 0-100
    time_taken: Mapped[int] = mapped_column(Integer, default=0, nullable=False)  # seconds
    completed_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    quiz: Mapped["Quiz"] = relationship("Quiz")

    def __repr__(self) -> str:
        return f"<QuizAttempt(quiz_id={self.quiz_id}, user_id={self.user_id}, score={self.percentage}%)>">


class WordCategory(str):
    AGRICULTURE = "agriculture"
    WATER = "water"
    ENVIRONMENT = "environment"
    ECONOMICS = "economics"
    TECHNOLOGY = "technology"


class DifficultyLevel(str):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"