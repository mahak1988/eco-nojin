"""Games API routes."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.schemas.games import (
    GamesStats,
    QuizAttemptListResponse,
    QuizAttemptResponse,
    QuizCreate,
    QuizListResponse,
    QuizQuestionCreate,
    QuizQuestionResponse,
    QuizQuestionUpdate,
    QuizResponse,
    QuizUpdate,
    VocabularyWordCreate,
    VocabularyWordListResponse,
    VocabularyWordResponse,
    VocabularyWordUpdate,
)
from apps.api.services.games import GamesService
from apps.shared_core.database.session import get_db_session
from apps.shared_core.deps import require_write_auth

router = APIRouter(prefix="/api/v1/games", tags=["Games"])


@router.get("/vocabulary", response_model=VocabularyWordListResponse)
async def list_vocabulary(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    search: str | None = Query(None),
    category: str | None = Query(None),
    session: AsyncSession = Depends(get_db_session),
) -> VocabularyWordListResponse:
    service = GamesService(session)
    words, total = await service.list_vocabulary(skip, limit, search, category)
    return VocabularyWordListResponse(items=words, total=total, skip=skip, limit=limit)


@router.post("/vocabulary", response_model=VocabularyWordResponse, status_code=status.HTTP_201_CREATED)
async def create_vocabulary(
    payload: VocabularyWordCreate,
    session: AsyncSession = Depends(get_db_session),
    _: None = Depends(require_write_auth),
) -> VocabularyWordResponse:
    service = GamesService(session)
    word = await service.create_vocabulary(payload)
    return VocabularyWordResponse.model_validate(word)


@router.get("/vocabulary/{word_id}", response_model=VocabularyWordResponse)
async def get_vocabulary(
    word_id: int,
    session: AsyncSession = Depends(get_db_session),
) -> VocabularyWordResponse:
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
    session: AsyncSession = Depends(get_db_session),
    _: None = Depends(require_write_auth),
) -> VocabularyWordResponse:
    service = GamesService(session)
    try:
        word = await service.update_vocabulary(word_id, payload)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    return VocabularyWordResponse.model_validate(word)


@router.delete("/vocabulary/{word_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_vocabulary(
    word_id: int,
    session: AsyncSession = Depends(get_db_session),
    _: None = Depends(require_write_auth),
) -> None:
    service = GamesService(session)
    try:
        await service.delete_vocabulary(word_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("/quizzes", response_model=QuizListResponse)
async def list_quizzes(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    search: str | None = Query(None),
    category: str | None = Query(None),
    difficulty: str | None = Query(None),
    session: AsyncSession = Depends(get_db_session),
) -> QuizListResponse:
    service = GamesService(session)
    quizzes, total = await service.list_quizzes(skip, limit, search, category, difficulty)
    return QuizListResponse(items=quizzes, total=total, skip=skip, limit=limit)


@router.post("/quizzes", response_model=QuizResponse, status_code=status.HTTP_201_CREATED)
async def create_quiz(
    payload: QuizCreate,
    author_id: int = Query(...),
    session: AsyncSession = Depends(get_db_session),
    _: None = Depends(require_write_auth),
) -> QuizResponse:
    service = GamesService(session)
    quiz = await service.create_quiz(author_id, payload)
    return QuizResponse.model_validate(quiz)


@router.get("/quizzes/{quiz_id}", response_model=QuizResponse)
async def get_quiz(
    quiz_id: int,
    session: AsyncSession = Depends(get_db_session),
) -> QuizResponse:
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
    session: AsyncSession = Depends(get_db_session),
    _: None = Depends(require_write_auth),
) -> QuizResponse:
    service = GamesService(session)
    try:
        quiz = await service.update_quiz(quiz_id, payload)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    return QuizResponse.model_validate(quiz)


@router.delete("/quizzes/{quiz_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_quiz(
    quiz_id: int,
    session: AsyncSession = Depends(get_db_session),
    _: None = Depends(require_write_auth),
) -> None:
    service = GamesService(session)
    try:
        await service.delete_quiz(quiz_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("/quizzes/{quiz_id}/questions", response_model=list[QuizQuestionResponse])
async def list_questions(
    quiz_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    session: AsyncSession = Depends(get_db_session),
) -> list[QuizQuestionResponse]:
    service = GamesService(session)
    questions, _ = await service.list_questions(quiz_id, skip, limit)
    return [QuizQuestionResponse.model_validate(q) for q in questions]


@router.post(
    "/quizzes/{quiz_id}/questions",
    response_model=QuizQuestionResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_question(
    quiz_id: int,
    payload: QuizQuestionCreate,
    session: AsyncSession = Depends(get_db_session),
    _: None = Depends(require_write_auth),
) -> QuizQuestionResponse:
    service = GamesService(session)
    try:
        question = await service.create_question(quiz_id, payload)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    return QuizQuestionResponse.model_validate(question)


@router.patch("/questions/{question_id}", response_model=QuizQuestionResponse)
async def update_question(
    question_id: int,
    payload: QuizQuestionUpdate,
    session: AsyncSession = Depends(get_db_session),
    _: None = Depends(require_write_auth),
) -> QuizQuestionResponse:
    service = GamesService(session)
    try:
        question = await service.update_question(question_id, payload)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    return QuizQuestionResponse.model_validate(question)


@router.delete("/questions/{question_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_question(
    question_id: int,
    session: AsyncSession = Depends(get_db_session),
    _: None = Depends(require_write_auth),
) -> None:
    service = GamesService(session)
    try:
        await service.delete_question(question_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("/users/{user_id}/attempts", response_model=QuizAttemptListResponse)
async def list_attempts(
    user_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    session: AsyncSession = Depends(get_db_session),
) -> QuizAttemptListResponse:
    service = GamesService(session)
    attempts, total = await service.list_attempts(user_id, skip, limit)
    return QuizAttemptListResponse(items=attempts, total=total, skip=skip, limit=limit)


@router.post(
    "/quizzes/{quiz_id}/attempts",
    response_model=QuizAttemptResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_attempt(
    quiz_id: int,
    user_id: int = Query(...),
    score: int = Query(0, ge=0),
    percentage: int = Query(0, ge=0, le=100),
    time_taken: int = Query(0, ge=0),
    session: AsyncSession = Depends(get_db_session),
    _: None = Depends(require_write_auth),
) -> QuizAttemptResponse:
    service = GamesService(session)
    attempt = await service.create_attempt(
        quiz_id,
        user_id,
        {"score": score, "percentage": percentage, "time_taken": time_taken},
    )
    return QuizAttemptResponse.model_validate(attempt)


@router.get("/stats", response_model=GamesStats)
async def get_stats(session: AsyncSession = Depends(get_db_session)) -> GamesStats:
    service = GamesService(session)
    return GamesStats(**await service.get_stats())
