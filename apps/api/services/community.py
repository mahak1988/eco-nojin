"""
Community Service
==================
Business logic layer — orchestrates repositories and enforces rules.
"""

import logging

logger = logging.getLogger(__name__)
from typing import Optional, List

from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.repositories.community import CommunityRepository
from apps.api.schemas.community import PostCreate, PostUpdate, CommentCreate, CommentUpdate
from apps.api.models.community import Post, Comment, Like


class CommunityService:
    """Service for community operations."""

    def __init__(self, session: AsyncSession) -> None:
        """Handle __init__ (session)."""
        self.repo = CommunityRepository(session)

    # ==================== Post Operations ====================

    async def list_posts(
        self, skip: int = 0, limit: int = 100,
        search: Optional[str] = None, category: Optional[str] = None, author_id: Optional[int] = None
    ) -> tuple[List[Post], int]:
        """Handle list_posts (skip, limit, search, category, author_id)."""
        limit = min(limit, 200)
        return await self.repo.list_posts(skip, limit, search, category, author_id)

    async def create_post(self, author_id: int, data: PostCreate) -> Post:
        """Handle create_post (author_id, data)."""
        return await self.repo.create_post(author_id, data)

    async def get_post(self, post_id: int) -> Post:
        """Handle get_post (post_id)."""
        obj = await self.repo.get_post_by_id(post_id)
        if not obj:
            raise ValueError(f"Post with id={post_id} not found")
        return obj

    async def update_post(self, post_id: int, data: PostUpdate) -> Post:
        """Handle update_post (post_id, data)."""
        obj = await self.repo.update_post(post_id, data)
        if not obj:
            raise ValueError(f"Post with id={post_id} not found")
        return obj

    async def delete_post(self, post_id: int) -> None:
        """Handle delete_post (post_id)."""
        if not await self.repo.delete_post(post_id):
            raise ValueError(f"Post with id={post_id} not found")

    # ==================== Comment Operations ====================

    async def list_comments(self, post_id: int, skip: int = 0, limit: int = 100) -> tuple[List[Comment], int]:
        """Handle list_comments (post_id, skip, limit)."""
        return await self.repo.list_comments_by_post(post_id, skip, limit)

    async def create_comment(self, post_id: int, author_id: int, data: CommentCreate) -> Comment:
        # Verify post exists
        """Handle create_comment (post_id, author_id, data)."""
        await self.get_post(post_id)
        return await self.repo.create_comment(post_id, author_id, data.model_dump())

    async def update_comment(self, comment_id: int, data: CommentUpdate) -> Comment:
        """Handle update_comment (comment_id, data)."""
        obj = await self.repo.update_comment(comment_id, data.model_dump())
        if not obj:
            raise ValueError(f"Comment with id={comment_id} not found")
        return obj

    async def delete_comment(self, comment_id: int) -> None:
        """Handle delete_comment (comment_id)."""
        if not await self.repo.delete_comment(comment_id):
            raise ValueError(f"Comment with id={comment_id} not found")

    # ==================== Like Operations ====================

    async def create_post_like(self, user_id: int, post_id: int) -> Like:
        # Check if already liked
        """Handle create_post_like (user_id, post_id)."""
        existing = await self.repo.get_user_post_like(user_id, post_id)
        if existing:
            raise ValueError("Already liked this post")
        return await self.repo.create_post_like(user_id, post_id)

    async def create_comment_like(self, user_id: int, comment_id: int) -> Like:
        """Handle create_comment_like (user_id, comment_id)."""
        existing = await self.repo.get_user_comment_like(user_id, comment_id)
        if existing:
            raise ValueError("Already liked this comment")
        return await self.repo.create_comment_like(user_id, comment_id)

    async def delete_like(self, like_id: int) -> None:
        """Handle delete_like (like_id)."""
        if not await self.repo.delete_like(like_id):
            raise ValueError(f"Like with id={like_id} not found")

    async def get_stats(self) -> dict:
        """Handle get_stats."""
        return await self.repo.get_stats()