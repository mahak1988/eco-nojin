"""
Games Router - Database backed
===============================
RESTful endpoints for vocabulary and quiz games.
"""

from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from apps.shared_core.database.session import get_db_session
from apps.api.schemas.games import (
    VocabularyWordCreate, VocabularyWordUpdate,
    VocabularyWordResponse, VocabularyWordListResponse,
    QuizCreate, QuizUpdate,
    QuizResponse, QuizListResponse,
    QuizQuestionCreate, QuizQuestionUpdate,
    QuizQuestionResponse,
    QuizAttemptResponse, QuizAttemptListResponse,
    GamesStats
)
from apps.api.services.games import GamesService

router = APIRouter(prefix="/api/v1/games", tags=["🎮 Games"])


# ==================== Vocabulary ====================

@router.get("/vocabulary", response_model=VocabularyWordListResponse)
async def list_vocabulary(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    search: Optional[str] = Query(None, description="Search by word or translation"),
    category: Optional[str] = Query(None, description="Filter by category"),
    session: AsyncSession = Depends(get_db_session)
) -> VocabularyWordListResponse:
    """List vocabulary words with optional search and filtering."""
    service = GamesService(session)
    words, total = await service.list_vocabulary(skip, limit, search, category)
    return VocabularyWordListResponse(items=words, total=total, skip=skip, limit=limit)


@router.post("/vocabulary", response_model=VocabularyWordResponse, status_code=status.HTTP_201_CREATED)
async def create_vocabulary(
    payload: VocabularyWordCreate,
    session: AsyncSession = Depends(get_db_session)
) -> VocabularyWordResponse:
    """Create a new vocabulary word."""
    service = GamesService(session)
    word = await service.create_vocabulary(payload)
    await session.commit()
    return VocabularyWordResponse.model_validate(word)


@router.get("/vocabulary/{word_id}", response_model=VocabularyWordResponse)
async def get_vocabulary(
    word_id: int,
    session: AsyncSession = Depends(get_db_session)
) -> VocabularyWordResponse:
    """Get a specific vocabulary word by ID."""
    service = GamesService(session)
    try:
        word = await service.get_vocabulary(word_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    return VocabularyWordResponse.model_validate(word)


@router.patch("/vocabulary/{word_id}", response_model=VocabularyWordResponse)
async def update_vocabulary(
    word_id: int,
    payload: VocabularyWordUpdate,
    session: AsyncSession = Depends(get_db_session)
) -> VocabularyWordResponse:
    """Update a vocabulary word."""
    service = GamesService(session)
    try:
        word = await service.update_vocabulary(word_id, payload)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    await session.commit()
    return VocabularyWordResponse.model_validate(word)


@router.delete("/vocabulary/{word_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_vocabulary(
    word_id: int,
    session: AsyncSession = Depends(get_db_session)
) -> None:
    """Delete a vocabulary word."""
    service = GamesService(session)
    try:
        await service.delete_vocabulary(word_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    await session.commit()


# ==================== Quizzes ====================

@router.get("/quizzes", response_model=QuizListResponse)
async def list_quizzes(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    search: Optional[str] = Query(None, description="Search by title"),
    category: Optional[str] = Query(None, description="Filter by category"),
    difficulty: Optional[str] = Query(None, description="Filter by difficulty"),
    session: AsyncSession = Depends(get_db_session)
) -> QuizListResponse:
    """List quizzes with optional search and filtering."""
    service = GamesService(session)
    quizzes, total = await service.list_quizzes(skip, limit, search, category, difficulty)
    return QuizListResponse(items=quizzes, total=total, skip=skip, limit=limit)


@router.post("/quizzes", response_model=QuizResponse, status_code=status.HTTP_201_CREATED)
async def create_quiz(
    author_id: int = Query(..., description="Author user ID"),
    payload: QuizCreate = ...,
    session: AsyncSession = Depends(get_db_session)
) -> QuizResponse:
    """Create a new quiz."""
    service = GamesService(session)
    quiz = await service.create_quiz(author_id, payload)
    await session.commit()
    return QuizResponse.model_validate(quiz)


@router.get("/quizzes/{quiz_id}", response_model=QuizResponse)
async def get_quiz(
    quiz_id: int,
    session: AsyncSession = Depends(get_db_session)
) -> QuizResponse:
    """Get a specific quiz by ID."""
    service = GamesService(session)
    try:
        quiz = await service.get_quiz(quiz_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    return QuizResponse.model_validate(quiz)


@router.patch("/quizzes/{quiz_id}", response_model=QuizResponse)
async def update_quiz(
    quiz_id: int,
    payload: QuizUpdate,
    session: AsyncSession = Depends(get_db_session)
) -> QuizResponse:
    """Update a quiz."""
    service = GamesService(session)
    try:
        quiz = await service.update_quiz(quiz_id, payload)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    await session.commit()
    return QuizResponse.model_validate(quiz)


@router.delete("/quizzes/{quiz_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_quiz(
    quiz_id: int,
    session: AsyncSession = Depends(get_db_session)
) -> None:
    """Delete a quiz."""
    service = GamesService(session)
    try:
        await service.delete_quiz(quiz_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    await session.commit()


# ==================== Quiz Questions ====================

@router.get("/quizzes/{quiz_id}/questions", response_model=List[QuizQuestionResponse])
async def list_questions(
    quiz_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    session: AsyncSession = Depends(get_db_session)
) -> List[QuizQuestionResponse]:
    """List questions for a specific quiz."""
    service = GamesService(session)
    questions, _ = await service.list_questions(quiz_id, skip, limit)
    return [QuizQuestionResponse.model_validate(q) for q in questions]


@router.post("/quizzes/{quiz_id}/questions", response_model=QuizQuestionResponse, status_code=status.HTTP_201_CREATED)
async def create_question(
    quiz_id: int,
    payload: QuizQuestionCreate = ...,
    session: AsyncSession = Depends(get_db_session)
) -> QuizQuestionResponse:
    """Create a new question within a quiz."""
    service = GamesService(session)
    try:
        question = await service.create_question(quiz_id, payload)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    await session.commit()
    return QuizQuestionResponse.model_validate(question)


@router.get("/questions/{question_id}", response_model=QuizQuestionResponse)
async def get_question(
    question_id: int,
    session: AsyncSession = Depends(get_db_session)
) -> QuizQuestionResponse:
    """Get a specific question by ID."""
    service = GamesService(session)
    try:
        question = await service.get_question(question_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    return QuizQuestionResponse.model_validate(question)


@router.patch("/questions/{question_id}", response_model=QuizQuestionResponse)
async def update_question(
    question_id: int,
    payload: QuizQuestionUpdate,
    session: AsyncSession = Depends(get_db_session)
) -> QuizQuestionResponse:
    """Update a question."""
    service = GamesService(session)
    try:
        question = await service.update_question(question_id, payload)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    await session.commit()
    return QuizQuestionResponse.model_validate(question)


@router.delete("/questions/{question_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_question(
    question_id: int,
    session: AsyncSession = Depends(get_db_session)
) -> None:
    """Delete a question."""
    service = GamesService(session)
    try:
        await service.delete_question(question_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    await session.commit()


# ==================== Quiz Attempts ====================

@router.get("/users/{user_id}/attempts", response_model=QuizAttemptListResponse)
async def list_attempts(
    user_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    session: AsyncSession = Depends(get_db_session)
) -> QuizAttemptListResponse:
    """List quiz attempts for a specific user."""
    service = GamesService(session)
    attempts, total = await service.list_attempts(user_id, skip, limit)
    return QuizAttemptListResponse(items=attempts, total=total, skip=skip, limit=limit)


@router.post("/quizzes/{quiz_id}/attempts", response_model=QuizAttemptResponse, status_code=status.HTTP_201_CREATED)
async def create_attempt(
    quiz_id: int,
    user_id: int = Query(..., description="User ID taking the quiz"),
    score: int = Query(0, ge=0, description="Score earned"),
    percentage: int = Query(0, ge=0, le=100, description="Percentage score"),
    time_taken: int = Query(0, ge=0, description="Time in seconds"),
    session: AsyncSession = Depends(get_db_session)
) -> QuizAttemptResponse:
    """Create a new quiz attempt record."""
    service = GamesService(session)
    attempt = await service.create_attempt(quiz_id, user_id, {
        "score": score,
        "percentage": percentage,
        "time_taken": time_taken
    })
    await session.commit()
    return QuizAttemptResponse.model_validate(attempt)


@router.get("/stats", response_model=GamesStats)
async def get_stats(session: AsyncSession = Depends(get_db_session)) -> GamesStats:
    """Get statistics about games."""
    service = GamesService(session)
    stats = await service.get_stats()
    return GamesStats(**stats)