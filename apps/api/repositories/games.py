"""
Games Repository
================
Data access layer — all database queries live here.
"""

from typing import Optional, List

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.models.games import VocabularyWord, Quiz, QuizQuestion, QuizAttempt
from apps.api.schemas.games import VocabularyWordCreate, VocabularyWordUpdate


class GamesRepository:
    """Repository for Games entities."""

    def __init__(self, session: AsyncSession):
        self.session = session

    # ==================== Vocabulary Operations ====================

    async def get_vocabulary_by_id(self, word_id: int) -> Optional[VocabularyWord]:
        result = await self.session.execute(
            select(VocabularyWord).where(VocabularyWord.id == word_id)
        )
        return result.scalar_one_or_none()

    async def list_vocabulary(
        self,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None,
        category: Optional[str] = None
    ) -> tuple[List[VocabularyWord], int]:
        query = select(VocabularyWord)

        if search:
            search_term = f"%{search.lower()}%"
            query = query.where(
                (VocabularyWord.word.ilike(search_term)) |
                (VocabularyWord.translation.ilike(search_term))
            )

        if category:
            query = query.where(VocabularyWord.category == category)

        query = query.order_by(VocabularyWord.word).offset(skip).limit(limit)
        result = await self.session.execute(query)
        items = list(result.scalars().all())

        count_query = select(func.count()).select_from(VocabularyWord)
        if search:
            search_term = f"%{search.lower()}%"
            count_query = count_query.where(
                (VocabularyWord.word.ilike(search_term)) |
                (VocabularyWord.translation.ilike(search_term))
            )
        if category:
            count_query = count_query.where(VocabularyWord.category == category)

        count_result = await self.session.execute(count_query)
        total = count_result.scalar_one()
        return items, total

    async def create_vocabulary(self, data: VocabularyWordCreate) -> VocabularyWord:
        obj = VocabularyWord(**data.model_dump())
        self.session.add(obj)
        await self.session.flush()
        await self.session.refresh(obj)
        return obj

    async def update_vocabulary(self, word_id: int, data: VocabularyWordUpdate) -> Optional[VocabularyWord]:
        obj = await self.get_vocabulary_by_id(word_id)
        if not obj:
            return None

        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(obj, key, value)

        await self.session.flush()
        await self.session.refresh(obj)
        return obj

    async def delete_vocabulary(self, word_id: int) -> bool:
        obj = await self.get_vocabulary_by_id(word_id)
        if not obj:
            return False
        await self.session.delete(obj)
        await self.session.flush()
        return True

    # ==================== Quiz Operations ====================

    async def get_quiz_by_id(self, quiz_id: int) -> Optional[Quiz]:
        result = await self.session.execute(
            select(Quiz).where(Quiz.id == quiz_id)
        )
        return result.scalar_one_or_none()

    async def list_quizzes(
        self,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None,
        category: Optional[str] = None,
        difficulty: Optional[str] = None
    ) -> tuple[List[Quiz], int]:
        query = select(Quiz)

        if search:
            search_term = f"%{search.lower()}%"
            query = query.where(Quiz.title.ilike(search_term))

        if category:
            query = query.where(Quiz.category == category)

        if difficulty:
            query = query.where(Quiz.difficulty == difficulty)

        query = query.order_by(Quiz.title).offset(skip).limit(limit)
        result = await self.session.execute(query)
        items = list(result.scalars().all())

        count_query = select(func.count()).select_from(Quiz)
        if search:
            search_term = f"%{search.lower()}%"
            count_query = count_query.where(Quiz.title.ilike(search_term))
        if category:
            count_query = count_query.where(Quiz.category == category)
        if difficulty:
            count_query = count_query.where(Quiz.difficulty == difficulty)

        count_result = await self.session.execute(count_query)
        total = count_result.scalar_one()
        return items, total

    async def create_quiz(self, data: dict) -> Quiz:
        obj = Quiz(**data)
        self.session.add(obj)
        await self.session.flush()
        await self.session.refresh(obj)
        return obj

    async def update_quiz(self, quiz_id: int, data: dict) -> Optional[Quiz]:
        from apps.api.schemas.games import QuizUpdate
        obj = await self.get_quiz_by_id(quiz_id)
        if not obj:
            return None

        update_schema = QuizUpdate(**data)
        update_data = update_schema.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(obj, key, value)

        await self.session.flush()
        await self.session.refresh(obj)
        return obj

    async def delete_quiz(self, quiz_id: int) -> bool:
        obj = await self.get_quiz_by_id(quiz_id)
        if not obj:
            return False
        await self.session.delete(obj)
        await self.session.flush()
        return True

    # ==================== Quiz Question Operations ====================

    async def get_question_by_id(self, question_id: int) -> Optional[QuizQuestion]:
        result = await self.session.execute(
            select(QuizQuestion).where(QuizQuestion.id == question_id)
        )
        return result.scalar_one_or_none()

    async def list_questions_by_quiz(
        self, quiz_id: int, skip: int = 0, limit: int = 100
    ) -> tuple[List[QuizQuestion], int]:
        query = select(QuizQuestion).where(QuizQuestion.quiz_id == quiz_id)
        query = query.order_by(QuizQuestion.order).offset(skip).limit(limit)
        result = await self.session.execute(query)
        items = list(result.scalars().all())

        count_query = select(func.count()).select_from(QuizQuestion).where(QuizQuestion.quiz_id == quiz_id)
        count_result = await self.session.execute(count_query)
        total = count_result.scalar_one()
        return items, total

    async def create_question(self, quiz_id: int, data: dict) -> QuizQuestion:
        obj = QuizQuestion(quiz_id=quiz_id, **data)
        self.session.add(obj)
        await self.session.flush()
        await self.session.refresh(obj)
        return obj

    async def update_question(self, question_id: int, data: dict) -> Optional[QuizQuestion]:
        from apps.api.schemas.games import QuizQuestionUpdate
        obj = await self.get_question_by_id(question_id)
        if not obj:
            return None

        update_schema = QuizQuestionUpdate(**data)
        update_data = update_schema.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(obj, key, value)

        await self.session.flush()
        await self.session.refresh(obj)
        return obj

    async def delete_question(self, question_id: int) -> bool:
        obj = await self.get_question_by_id(question_id)
        if not obj:
            return False
        await self.session.delete(obj)
        await self.session.flush()
        return True

    # ==================== Quiz Attempt Operations ====================

    async def create_attempt(self, quiz_id: int, user_id: int, data: dict) -> QuizAttempt:
        from apps.api.schemas.games import QuizAttemptCreate
        obj = QuizAttempt(quiz_id=quiz_id, user_id=user_id, **data)
        self.session.add(obj)
        await self.session.flush()
        await self.session.refresh(obj)
        return obj

    async def list_attempts_by_user(
        self, user_id: int, skip: int = 0, limit: int = 100
    ) -> tuple[List[QuizAttempt], int]:
        query = select(QuizAttempt).where(QuizAttempt.user_id == user_id)
        query = query.order_by(QuizAttempt.completed_at.desc()).offset(skip).limit(limit)
        result = await self.session.execute(query)
        items = list(result.scalars().all())

        count_query = select(func.count()).select_from(QuizAttempt).where(QuizAttempt.user_id == user_id)
        count_result = await self.session.execute(count_query)
        total = count_result.scalar_one()
        return items, total

    async def get_stats(self) -> dict:
        vocab_result = await self.session.execute(select(VocabularyWord))
        vocab = vocab_result.scalars().all()

        quiz_result = await self.session.execute(select(Quiz))
        quizzes = quiz_result.scalars().all()

        attempt_result = await self.session.execute(select(QuizAttempt))
        attempts = attempt_result.scalars().all()

        return {
            "total_vocabulary": len(vocab),
            "total_quizzes": len(quizzes),
            "total_attempts": len(attempts),
            "by_category": {
                cat: len([v for v in vocab if v.category == cat])
                for cat in ["agriculture", "water", "environment", "economics", "technology"]
            },
            "by_difficulty": {
                lvl: len([q for q in quizzes if q.difficulty == lvl])
                for lvl in ["easy", "medium", "hard"]
            }
        }