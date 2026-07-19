"""
Community Repository
====================
Data access layer — all database queries live here.
"""

from typing import Optional, List

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.models.community import Post, Comment, Like
from apps.api.schemas.community import PostCreate, PostUpdate


class CommunityRepository:
    """Repository for Community entities."""

    def __init__(self, session: AsyncSession):
        self.session = session

    # ==================== Post Operations ====================

    async def get_post_by_id(self, post_id: int) -> Optional[Post]:
        result = await self.session.execute(
            select(Post).where(Post.id == post_id)
        )
        return result.scalar_one_or_none()

    async def list_posts(
        self,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None,
        category: Optional[str] = None,
        author_id: Optional[int] = None
    ) -> tuple[List[Post], int]:
        query = select(Post)

        if search:
            search_term = f"%{search.lower()}%"
            query = query.where(
                (Post.title.ilike(search_term)) |
                (Post.content.ilike(search_term))
            )

        if category:
            query = query.where(Post.category == category)

        if author_id:
            query = query.where(Post.author_id == author_id)

        query = query.order_by(Post.created_at.desc()).offset(skip).limit(limit)
        result = await self.session.execute(query)
        items = list(result.scalars().all())

        count_query = select(func.count()).select_from(Post)
        if search:
            search_term = f"%{search.lower()}%"
            count_query = count_query.where(
                (Post.title.ilike(search_term)) |
                (Post.content.ilike(search_term))
            )
        if category:
            count_query = count_query.where(Post.category == category)
        if author_id:
            count_query = count_query.where(Post.author_id == author_id)

        count_result = await self.session.execute(count_query)
        total = count_result.scalar_one()
        return items, total

    async def create_post(self, author_id: int, data: PostCreate) -> Post:
        data_dict = data.model_dump()
        if data_dict.get("tags"):
            data_dict["tags"] = ",".join(data_dict["tags"])
        data_dict["author_id"] = author_id

        obj = Post(**data_dict)
        self.session.add(obj)
        await self.session.flush()
        await self.session.refresh(obj)
        return obj

    async def update_post(self, post_id: int, data: PostUpdate) -> Optional[Post]:
        obj = await self.get_post_by_id(post_id)
        if not obj:
            return None

        update_data = data.model_dump(exclude_unset=True)
        if "tags" in update_data:
            update_data["tags"] = ",".join(update_data["tags"]) if update_data["tags"] else ""

        for key, value in update_data.items():
            setattr(obj, key, value)

        await self.session.flush()
        await self.session.refresh(obj)
        return obj

    async def delete_post(self, post_id: int) -> bool:
        obj = await self.get_post_by_id(post_id)
        if not obj:
            return False
        await self.session.delete(obj)
        await self.session.flush()
        return True

    # ==================== Comment Operations ====================

    async def get_comment_by_id(self, comment_id: int) -> Optional[Comment]:
        result = await self.session.execute(
            select(Comment).where(Comment.id == comment_id)
        )
        return result.scalar_one_or_none()

    async def list_comments_by_post(
        self, post_id: int, skip: int = 0, limit: int = 100
    ) -> tuple[List[Comment], int]:
        query = select(Comment).where(Comment.post_id == post_id)
        query = query.order_by(Comment.created_at).offset(skip).limit(limit)
        result = await self.session.execute(query)
        items = list(result.scalars().all())

        count_query = select(func.count()).select_from(Comment).where(Comment.post_id == post_id)
        count_result = await self.session.execute(count_query)
        total = count_result.scalar_one()
        return items, total

    async def create_comment(self, post_id: int, author_id: int, data: dict) -> Comment:
        obj = Comment(post_id=post_id, author_id=author_id, **data)
        self.session.add(obj)
        # Update comment count on post
        post = await self.get_post_by_id(post_id)
        if post:
            post.comment_count += 1
        await self.session.flush()
        await self.session.refresh(obj)
        return obj

    async def update_comment(self, comment_id: int, data: dict) -> Optional[Comment]:
        from apps.api.schemas.community import CommentUpdate
        obj = await self.get_comment_by_id(comment_id)
        if not obj:
            return None

        update_schema = CommentUpdate(**data)
        update_data = update_schema.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(obj, key, value)

        await self.session.flush()
        await self.session.refresh(obj)
        return obj

    async def delete_comment(self, comment_id: int) -> bool:
        obj = await self.get_comment_by_id(comment_id)
        if not obj:
            return False
        # Update comment count on post
        post = await self.get_post_by_id(obj.post_id)
        if post:
            post.comment_count = max(0, post.comment_count - 1)
        await self.session.delete(obj)
        await self.session.flush()
        return True

    # ==================== Like Operations ====================

    async def get_like_by_id(self, like_id: int) -> Optional[Like]:
        result = await self.session.execute(
            select(Like).where(Like.id == like_id)
        )
        return result.scalar_one_or_none()

    async def get_user_post_like(self, user_id: int, post_id: int) -> Optional[Like]:
        result = await self.session.execute(
            select(Like).where(Like.user_id == user_id, Like.post_id == post_id)
        )
        return result.scalar_one_or_none()

    async def get_user_comment_like(self, user_id: int, comment_id: int) -> Optional[Like]:
        result = await self.session.execute(
            select(Like).where(Like.user_id == user_id, Like.comment_id == comment_id)
        )
        return result.scalar_one_or_none()

    async def create_post_like(self, user_id: int, post_id: int) -> Like:
        obj = Like(user_id=user_id, post_id=post_id)
        self.session.add(obj)
        # Update like count on post
        post = await self.get_post_by_id(post_id)
        if post:
            post.like_count += 1
        await self.session.flush()
        await self.session.refresh(obj)
        return obj

    async def create_comment_like(self, user_id: int, comment_id: int) -> Like:
        obj = Like(user_id=user_id, comment_id=comment_id)
        self.session.add(obj)
        # Update like count on comment
        comment = await self.get_comment_by_id(comment_id)
        if comment:
            comment.like_count += 1
        await self.session.flush()
        await self.session.refresh(obj)
        return obj

    async def delete_like(self, like_id: int) -> bool:
        obj = await self.get_like_by_id(like_id)
        if not obj:
            return False
        if obj.post_id:
            post = await self.get_post_by_id(obj.post_id)
            if post:
                post.like_count = max(0, post.like_count - 1)
        elif obj.comment_id:
            comment = await self.get_comment_by_id(obj.comment_id)
            if comment:
                comment.like_count = max(0, comment.like_count - 1)
        await self.session.delete(obj)
        await self.session.flush()
        return True

    async def get_stats(self) -> dict:
        posts_result = await self.session.execute(select(Post))
        posts = posts_result.scalars().all()

        comments_result = await self.session.execute(select(Comment))
        comments = comments_result.scalars().all()

        likes_result = await self.session.execute(select(Like))
        likes = likes_result.scalars().all()

        return {
            "total_posts": len(posts),
            "total_comments": len(comments),
            "total_likes": len(likes),
            "by_category": {
                cat: len([p for p in posts if p.category == cat])
                for cat in ["general", "agriculture", "water", "environment", "economics", "technology"]
            }
        }