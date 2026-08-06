"""
Games System Tests
==================
Tests for VocabularyWord, Quiz, QuizQuestion, QuizAttempt CRUD operations.
"""

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.models.games import (
    VocabularyWord, Quiz, QuizQuestion, QuizAttempt,
    QuestionType, QuizDifficulty, WordDifficulty
)


@pytest.fixture
async def games_db_session():
    """Create a test database session for games models."""
    from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
    from apps.shared_core.database.session import Base

    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with async_session() as session:
        yield session

    await engine.dispose()


@pytest.mark.asyncio
async def test_vocabulary_word_crud(games_db_session: AsyncSession):
    """Test vocabulary word CRUD operations."""
    # Create
    word = VocabularyWord(
        id="word-1",
        word="Sustainability",
        definition="The ability to maintain at a certain rate",
        translation="پایداری",
        difficulty=WordDifficulty.MEDIUM,
        category="agriculture",
    )
    games_db_session.add(word)
    await games_db_session.flush()

    # Read
    result = await games_db_session.execute(select(VocabularyWord).where(VocabularyWord.id == "word-1"))
    fetched = result.scalar_one_or_none()
    assert fetched is not None
    assert fetched.word == "Sustainability"
    assert fetched.translation == "پایداری"

    # Update
    fetched.definition = "Updated definition"
    await games_db_session.flush()

    result = await games_db_session.execute(select(VocabularyWord).where(VocabularyWord.id == "word-1"))
    updated = result.scalar_one()
    assert updated.definition == "Updated definition"


@pytest.mark.asyncio
async def test_quiz_crud(games_db_session: AsyncSession):
    """Test quiz CRUD operations."""
    # Create
    quiz = Quiz(
        id="quiz-1",
        title="Environmental Basics",
        description="Test your knowledge of environment",
        difficulty=QuizDifficulty.EASY,
        time_limit_minutes=10,
    )
    games_db_session.add(quiz)
    await games_db_session.flush()

    # Read
    result = await games_db_session.execute(select(Quiz).where(Quiz.id == "quiz-1"))
    fetched = result.scalar_one_or_none()
    assert fetched is not None
    assert fetched.title == "Environmental Basics"

    # Update
    fetched.time_limit_minutes = 15
    await games_db_session.flush()

    result = await games_db_session.execute(select(Quiz).where(Quiz.id == "quiz-1"))
    updated = result.scalar_one()
    assert updated.time_limit_minutes == 15


@pytest.mark.asyncio
async def test_quiz_question_crud(games_db_session: AsyncSession):
    """Test quiz question CRUD operations."""
    # Create quiz first
    quiz = Quiz(
        id="quiz-2",
        title="Test Quiz",
        difficulty=QuizDifficulty.MEDIUM,
    )
    games_db_session.add(quiz)
    await games_db_session.flush()

    # Create question
    question = QuizQuestion(
        id="question-1",
        quiz_id="quiz-2",
        question_text="What is photosynthesis?",
        question_type=QuestionType.MULTIPLE_CHOICE,
        options='["Process of making food", "Process of breathing", "Process of sleeping", "Process of walking"]',
        correct_answer="0",
        points=10,
    )
    games_db_session.add(question)
    await games_db_session.flush()

    # Read
    result = await games_db_session.execute(select(QuizQuestion).where(QuizQuestion.id == "question-1"))
    fetched = result.scalar_one_or_none()
    assert fetched is not None
    assert fetched.question_type == QuestionType.MULTIPLE_CHOICE


@pytest.mark.asyncio
async def test_quiz_attempt_crud(games_db_session: AsyncSession):
    """Test quiz attempt CRUD operations."""
    # Create quiz
    quiz = Quiz(
        id="quiz-3",
        title="Attempt Test Quiz",
        difficulty=QuizDifficulty.HARD,
    )
    games_db_session.add(quiz)
    await games_db_session.flush()

    # Create attempt
    attempt = QuizAttempt(
        id="attempt-1",
        quiz_id="quiz-3",
        user_id="user-1",
        score=85.5,
        total_questions=10,
        correct_answers=8,
    )
    games_db_session.add(attempt)
    await games_db_session.flush()

    # Read
    result = await games_db_session.execute(select(QuizAttempt).where(QuizAttempt.id == "attempt-1"))
    fetched = result.scalar_one_or_none()
    assert fetched is not None
    assert fetched.score == 85.5


@pytest.mark.asyncio
async def test_question_type_enum():
    """Test question type enum values."""
    assert QuestionType.MULTIPLE_CHOICE == "multiple_choice"
    assert QuestionType.TRUE_FALSE == "true_false"
    assert QuestionType.SHORT_ANSWER == "short_answer"


@pytest.mark.asyncio
async def test_quiz_difficulty_enum():
    """Test quiz difficulty enum values."""
    assert QuizDifficulty.EASY == "easy"
    assert QuizDifficulty.MEDIUM == "medium"
    assert QuizDifficulty.HARD == "hard"


@pytest.mark.asyncio
async def test_word_difficulty_enum():
    """Test word difficulty enum values."""
    assert WordDifficulty.EASY == "easy"
    assert WordDifficulty.MEDIUM == "medium"
    assert WordDifficulty.HARD == "hard"