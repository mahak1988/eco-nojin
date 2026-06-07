# api/modules/psychology/models.py
from sqlalchemy import Column, Integer, String, Float, DateTime, JSON, Boolean, ForeignKey, Text, Enum as SQLEnum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from api.core.database import Base
import enum

class TestCategory(enum.Enum):
    CLINICAL = "clinical"
    ECO_PSYCHOLOGY = "eco_psychology"
    CLIMATE_RESILIENCE = "climate_resilience"
    PRO_SOCIAL = "pro_social"
    OCCUPATIONAL = "occupational"

class ScoringType(enum.Enum):
    SUM = "sum"
    AVERAGE = "average"
    T_SCORE = "t_score"
    CATEGORICAL = "categorical"

class PsychTest(Base):
    __tablename__ = "psych_tests"
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True, nullable=False)
    title = Column(String(300), nullable=False)
    category = Column(SQLEnum(TestCategory), nullable=False)
    scoring_type = Column(SQLEnum(ScoringType), nullable=False)
    has_subscales = Column(Boolean, default=False)
    duration_minutes = Column(Integer, default=10)
    description = Column(Text)
    is_active = Column(Boolean, default=True)
    questions = relationship("PsychQuestion", back_populates="test", cascade="all, delete-orphan")

class PsychQuestion(Base):
    __tablename__ = "psych_questions"
    id = Column(Integer, primary_key=True, index=True)
    test_id = Column(Integer, ForeignKey("psych_tests.id"), nullable=False)
    subscale_code = Column(String(50))
    question_number = Column(Integer, nullable=False)
    text = Column(Text, nullable=False)
    is_reverse_scored = Column(Boolean, default=False)
    test = relationship("PsychTest", back_populates="questions")
    options = relationship("PsychOption", back_populates="question", cascade="all, delete-orphan")

class PsychOption(Base):
    __tablename__ = "psych_options"
    id = Column(Integer, primary_key=True, index=True)
    question_id = Column(Integer, ForeignKey("psych_questions.id"), nullable=False)
    label = Column(String(500), nullable=False)
    score_value = Column(Float, nullable=False)
    question = relationship("PsychQuestion", back_populates="options")

class PsychResult(Base):
    __tablename__ = "psych_results"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    test_code = Column(String(50), nullable=False)
    raw_scores = Column(JSON)
    interpretation = Column(JSON)
    completed_at = Column(DateTime, server_default=func.now())

class EcoPsychProfile(Base):
    __tablename__ = "eco_psych_profiles"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    big_five = Column(JSON)
    eco_identity_score = Column(Float, default=0.0)
    climate_resilience_score = Column(Float, default=0.0)
    cooperation_score = Column(Float, default=0.0)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
