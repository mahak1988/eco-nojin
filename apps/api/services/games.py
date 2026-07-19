"""
Games Service
==============
Business logic layer — orchestrates repositories and enforces rules.
"""

from typing import Optional, List

from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.repositories.games import GamesRepository
from apps.api.schemas.games import (
    VocabularyWordCreate, VocabularyWordUpdate, QuizCreate,
    QuizUpdate, QuizQuestionCreate, QuizQuestionUpdate
)
from apps.api.models.games import VocabularyWord, Quiz, QuizQuestion, QuizAttempt


class GamesService:
    """Service for games operations."""

    def __init__(self, session: AsyncSession):
        self.repo = GamesRepository(session)

    # ==================== Vocabulary Operations ====================

    async def list_vocabulary(
        self, skip: int = 0, limit: int = 100,
        search: Optional[str] = None, category: Optional[str] = None
    ) -> tuple[List[VocabularyWord], int]:
        limit = min(limit, 200)
        return await self.repo.list_vocabulary(skip, limit, search, category)

    async def create_vocabulary(self, data: VocabularyWordCreate) -> VocabularyWord:
        return await self.repo.create_vocabulary(data)

    async def get_vocabulary(self, word_id: int) -> VocabularyWord:
        obj = await self.repo.get_vocabulary_by_id(word_id)
        if not obj:
            raise ValueError(f"VocabularyWord with id={word_id} not found")
        return obj

    async def update_vocabulary(self, word_id: int, data: VocabularyWordUpdate) -> VocabularyWord:
        obj = await self.repo.update_vocabulary(word_id, data)
        if not obj:
            raise ValueError(f"VocabularyWord with id={word_id} not found")
        return obj

    async def delete_vocabulary(self, word_id: int) -> None:
        if not await self.repo.delete_vocabulary(word_id):
            raise ValueError(f"VocabularyWord with id={word_id} not found")

    # ==================== Quiz Operations ====================

    async def list_quizzes(
        self, skip: int = 0, limit: int = 100,
        search: Optional[str] = None, category: Optional[str] = None, difficulty: Optional[str] = None
    ) -> tuple[List[Quiz], int]:
        limit = min(limit, 200)
        return await self.repo.list_quizzes(skip, limit, search, category, difficulty)

    async def create_quiz(self, author_id: int, data: QuizCreate) -> Quiz:
        obj = await self.repo.create_quiz({**data.model_dump(exclude={"questions"}), "author_id": author_id})

        # Add questions
        for q_data in (data.questions or []):
            await self.repo.create_question(obj.id, q_data.model_dump())

        await self.repo.session.refresh(obj)
        return obj

    async def get_quiz(self, quiz_id: int) -> Quiz:
        obj = await self.repo.get_quiz_by_id(quiz_id)
        if not obj:
            raise ValueError(f"Quiz with id={quiz_id} not found")
        return obj

    async def update_quiz(self, quiz_id: int, data: QuizUpdate) -> Quiz:
        from apps.api.schemas.games import QuizUpdate
        obj = await self.repo.update_quiz(quiz_id, data.model_dump())
        if not obj:
            raise ValueError(f"Quiz with id={quiz_id} not found")
        return obj

    async def delete_quiz(self, quiz_id: int) -> None:
        if not await self.repo.delete_quiz(quiz_id):
            raise ValueError(f"Quiz with id={quiz_id} not found")

    # ==================== Quiz Question Operations ====================

    async def list_questions(self, quiz_id: int, skip: int = 0, limit: int = 100) -> tuple[List[QuizQuestion], int]:
        return await self.repo.list_questions_by_quiz(quiz_id, skip, limit)

    async def create_question(self, quiz_id: int, data: QuizQuestionCreate) -> QuizQuestion:
        await self.get_quiz(quiz_id)
        return await self.repo.create_question(quiz_id, data.model_dump())

    async def get_question(self, question_id: int) -> QuizQuestion:
        obj = await self.repo.get_question_by_id(question_id)
        if not obj:
            raise ValueError(f"QuizQuestion with id={question_id} not found")
        return obj

    async def update_question(self, question_id: int, data: QuizQuestionUpdate) -> QuizQuestion:
        from apps.api.schemas.games import QuizQuestionUpdate
        obj = await self.repo.update_question(question_id, data.model_dump())
        if not obj:
            raise ValueError(f"QuizQuestion with id={question_id} not found")
        return obj

    async def delete_question(self, question_id: int) -> None:
        if not await self.repo.delete_question(question_id):
            raise ValueError(f"QuizQuestion with id={question_id} not found")

    # ==================== Quiz Attempt Operations ====================

    async def list_attempts(self, user_id: int, skip: int = 0, limit: int = 100) -> tuple[List[QuizAttempt], int]:
        return await self.repo.list_attempts_by_user(user_id, skip, limit)

    async def create_attempt(self, quiz_id: int, user_id: int, data: dict) -> QuizAttempt:
        return await self.repo.create_attempt(quiz_id, user_id, data)

    async def get_stats(self) -> dict:
        return await self.repo.get_stats()