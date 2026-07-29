"""
Games Service
==============
Business logic layer — orchestrates repositories and enforces rules.
"""

import logging

logger = logging.getLogger(__name__)
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

    def __init__(self, session: AsyncSession) -> None:
        """Handle __init__ (session)."""
        self.repo = GamesRepository(session)

    # ==================== Vocabulary Operations ====================

    async def list_vocabulary(
        self, skip: int = 0, limit: int = 100,
        search: Optional[str] = None, category: Optional[str] = None
    ) -> tuple[List[VocabularyWord], int]:
        """Handle list_vocabulary (skip, limit, search, category)."""
        limit = min(limit, 200)
        return await self.repo.list_vocabulary(skip, limit, search, category)

    async def create_vocabulary(self, data: VocabularyWordCreate) -> VocabularyWord:
        """Handle create_vocabulary (data)."""
        return await self.repo.create_vocabulary(data)

    async def get_vocabulary(self, word_id: int) -> VocabularyWord:
        """Handle get_vocabulary (word_id)."""
        obj = await self.repo.get_vocabulary_by_id(word_id)
        if not obj:
            raise ValueError(f"VocabularyWord with id={word_id} not found")
        return obj

    async def update_vocabulary(self, word_id: int, data: VocabularyWordUpdate) -> VocabularyWord:
        """Handle update_vocabulary (word_id, data)."""
        obj = await self.repo.update_vocabulary(word_id, data)
        if not obj:
            raise ValueError(f"VocabularyWord with id={word_id} not found")
        return obj

    async def delete_vocabulary(self, word_id: int) -> None:
        """Handle delete_vocabulary (word_id)."""
        if not await self.repo.delete_vocabulary(word_id):
            raise ValueError(f"VocabularyWord with id={word_id} not found")

    # ==================== Quiz Operations ====================

    async def list_quizzes(
        self, skip: int = 0, limit: int = 100,
        search: Optional[str] = None, category: Optional[str] = None, difficulty: Optional[str] = None
    ) -> tuple[List[Quiz], int]:
        """Handle list_quizzes (skip, limit, search, category, difficulty)."""
        limit = min(limit, 200)
        return await self.repo.list_quizzes(skip, limit, search, category, difficulty)

    async def create_quiz(self, author_id: int, data: QuizCreate) -> Quiz:
        """Handle create_quiz (author_id, data)."""
        obj = await self.repo.create_quiz({**data.model_dump(exclude={"questions"}), "author_id": author_id})

        # Add questions
        for q_data in (data.questions or []):
            await self.repo.create_question(obj.id, q_data.model_dump())

        await self.repo.session.refresh(obj)
        return obj

    async def get_quiz(self, quiz_id: int) -> Quiz:
        """Handle get_quiz (quiz_id)."""
        obj = await self.repo.get_quiz_by_id(quiz_id)
        if not obj:
            raise ValueError(f"Quiz with id={quiz_id} not found")
        return obj

    async def update_quiz(self, quiz_id: int, data: QuizUpdate) -> Quiz:
        """Handle update_quiz (quiz_id, data)."""
        from apps.api.schemas.games import QuizUpdate
        obj = await self.repo.update_quiz(quiz_id, data.model_dump())
        if not obj:
            raise ValueError(f"Quiz with id={quiz_id} not found")
        return obj

    async def delete_quiz(self, quiz_id: int) -> None:
        """Handle delete_quiz (quiz_id)."""
        if not await self.repo.delete_quiz(quiz_id):
            raise ValueError(f"Quiz with id={quiz_id} not found")

    # ==================== Quiz Question Operations ====================

    async def list_questions(self, quiz_id: int, skip: int = 0, limit: int = 100) -> tuple[List[QuizQuestion], int]:
        """Handle list_questions (quiz_id, skip, limit)."""
        return await self.repo.list_questions_by_quiz(quiz_id, skip, limit)

    async def create_question(self, quiz_id: int, data: QuizQuestionCreate) -> QuizQuestion:
        """Handle create_question (quiz_id, data)."""
        await self.get_quiz(quiz_id)
        return await self.repo.create_question(quiz_id, data.model_dump())

    async def get_question(self, question_id: int) -> QuizQuestion:
        """Handle get_question (question_id)."""
        obj = await self.repo.get_question_by_id(question_id)
        if not obj:
            raise ValueError(f"QuizQuestion with id={question_id} not found")
        return obj

    async def update_question(self, question_id: int, data: QuizQuestionUpdate) -> QuizQuestion:
        """Handle update_question (question_id, data)."""
        from apps.api.schemas.games import QuizQuestionUpdate
        obj = await self.repo.update_question(question_id, data.model_dump())
        if not obj:
            raise ValueError(f"QuizQuestion with id={question_id} not found")
        return obj

    async def delete_question(self, question_id: int) -> None:
        """Handle delete_question (question_id)."""
        if not await self.repo.delete_question(question_id):
            raise ValueError(f"QuizQuestion with id={question_id} not found")

    # ==================== Quiz Attempt Operations ====================

    async def list_attempts(self, user_id: int, skip: int = 0, limit: int = 100) -> tuple[List[QuizAttempt], int]:
        """Handle list_attempts (user_id, skip, limit)."""
        return await self.repo.list_attempts_by_user(user_id, skip, limit)

    async def create_attempt(self, quiz_id: int, user_id: int, data: dict) -> QuizAttempt:
        """Handle create_attempt (quiz_id, user_id, data)."""
        return await self.repo.create_attempt(quiz_id, user_id, data)

    async def get_stats(self) -> dict:
        """Handle get_stats."""
        return await self.repo.get_stats()