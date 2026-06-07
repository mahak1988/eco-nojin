# api/modules/community/router.py
from api.core.schemas import SuccessResponse, IDResponse, StatsResponse, PaginatedResponse
from typing import Dict, Any, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from api.core.database import get_db
from api.modules.community.models import Comment, CommunityEvent, Post, PostType, UserReputation



class CommunityFeedResponse(BaseModel):
    """Auto-generated response model for /feed"""
    posts: List[Any] = []
    total: int = 0
    trending_topics: List[str] = []


router = APIRouter(prefix="/community", tags=["Farmers Community"])


class PostCreate(BaseModel):
    author_id: int
    post_type: str
    title: Optional[str] = None
    content: str
    category: str
    location_name: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    images: Optional[List[str]] = None
    voice_note_url: Optional[str] = None
    tags: Optional[List[str]] = []


class CommentCreate(BaseModel):
    author_id: int
    content: str
    voice_note_url: Optional[str] = None
    parent_id: Optional[int] = None


@router.get("/feed", response_model=CommunityFeedResponse)
async def get_community_feed(
    category: Optional[str] = None,
    post_type: Optional[str] = None,
    limit: int = Query(20, le=100),
    db: AsyncSession = Depends(get_db),
):
    query = select(Post).order_by(desc(Post.created_at)).limit(limit)
    if category:
        query = query.where(Post.category == category)
    if post_type:
        query = query.where(Post.post_type == PostType(post_type))

    result = await db.execute(query)
    posts = result.scalars().all()

    return {
        "posts": [
            {
                "id": p.id,
                "post_type": p.post_type.value,
                "title": p.title,
                "content": p.content,
                "category": p.category,
                "location_name": p.location_name,
                "images": p.images,
                "voice_note_url": p.voice_note_url,
                "upvotes": p.upvotes,
                "comment_count": p.comment_count,
                "is_resolved": p.is_resolved,
                "created_at": p.created_at,
                "author": {
                    "id": p.author.id,
                    "name": p.author.full_name,
                    "level": getattr(p.author, "reputation_level", "novice"),
                },
            }
            for p in posts
        ]
    }


@router.post("/posts", response_model=Dict[str, Any])
async def create_post(post_data: PostCreate, db: AsyncSession = Depends(get_db)):
    new_post = Post(
        author_id=post_data.author_id,
        post_type=PostType(post_data.post_type),
        title=post_data.title,
        content=post_data.content,
        category=post_data.category,
        location_name=post_data.location_name,
        latitude=post_data.latitude,
        longitude=post_data.longitude,
        images=post_data.images,
        voice_note_url=post_data.voice_note_url,
        tags=post_data.tags,
    )
    db.add(new_post)

    # افزایش امتیاز کاربر
    rep = await db.execute(
        select(UserReputation).where(UserReputation.user_id == post_data.author_id)
    )
    reputation = rep.scalar_one_or_none()
    if reputation:
        reputation.total_points += 10
        reputation.posts_count += 1

    await db.commit()
    await db.refresh(new_post)
    return {"id": new_post.id, "status": "created"}


@router.post("/posts/{post_id}/comments", response_model=IDResponse)
async def add_comment(
    post_id: int, comment_data: CommentCreate, db: AsyncSession = Depends(get_db)
):
    new_comment = Comment(
        post_id=post_id,
        author_id=comment_data.author_id,
        content=comment_data.content,
        voice_note_url=comment_data.voice_note_url,
        parent_id=comment_data.parent_id,
    )
    db.add(new_comment)

    # افزایش تعداد کامنت پست
    result = await db.execute(select(Post).where(Post.id == post_id))
    post = result.scalar_one()
    post.comment_count += 1

    await db.commit()
    return {"id": new_comment.id, "status": "created"}


@router.post("/posts/{post_id}/upvote", response_model=Dict[str, Any])
async def upvote_post(post_id: int, user_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Post).where(Post.id == post_id))
    post = result.scalar_one_or_none()
    if not post:
        raise HTTPException(404, "پست یافت نشد")
    post.upvotes += 1
    await db.commit()
    return {"status": "upvoted", "new_upvotes": post.upvotes}


@router.get("/events", response_model=Dict[str, Any])
async def get_events(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(CommunityEvent).order_by(CommunityEvent.start_time))
    events = result.scalars().all()
    return {
        "events": [
            {
                "id": e.id,
                "title": e.title,
                "event_type": e.event_type,
                "location_name": e.location_name,
                "start_time": e.start_time,
                "registered_count": e.registered_count,
                "max_participants": e.max_participants,
                "cover_image_url": e.cover_image_url,
            }
            for e in events
        ]
    }


@router.get("/users/{user_id}/reputation", response_model=Dict[str, Any])
async def get_user_reputation(user_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(UserReputation).where(UserReputation.user_id == user_id))
    rep = result.scalar_one_or_none()
    if not rep:
        rep = UserReputation(user_id=user_id)
        db.add(rep)
        await db.commit()

    return {
        "total_points": rep.total_points,
        "level": rep.level,
        "badges": rep.badges or [],
        "posts_count": rep.posts_count,
        "accepted_answers": rep.accepted_answers_count,
    }
