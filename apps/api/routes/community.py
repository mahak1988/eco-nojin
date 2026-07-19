"""
Community Router - Database backed
==================================
RESTful endpoints for community posts, comments, and likes.
"""

from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from apps.shared_core.database.session import get_db_session
from apps.api.schemas.community import (
    PostCreate, PostUpdate,
    PostResponse, PostListResponse, PostStats,
    CommentCreate, CommentUpdate,
    CommentResponse, LikeResponse
)
from apps.api.services.community import CommunityService

router = APIRouter(prefix="/api/v1/community", tags=["💬 Community"])


# ==================== Posts ====================

@router.get("/posts", response_model=PostListResponse)
async def list_posts(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    search: Optional[str] = Query(None, description="Search by title or content"),
    category: Optional[str] = Query(None, description="Filter by category"),
    author_id: Optional[int] = Query(None, description="Filter by author"),
    session: AsyncSession = Depends(get_db_session)
) -> PostListResponse:
    """List community posts with optional search and filtering."""
    service = CommunityService(session)
    posts, total = await service.list_posts(skip, limit, search, category, author_id)
    return PostListResponse(items=posts, total=total, skip=skip, limit=limit)


@router.get("/posts/stats", response_model=PostStats)
async def get_post_stats(session: AsyncSession = Depends(get_db_session)) -> PostStats:
    """Get statistics about posts."""
    service = CommunityService(session)
    stats = await service.get_stats()
    return PostStats(**stats)


@router.post("/posts", response_model=PostResponse, status_code=status.HTTP_201_CREATED)
async def create_post(
    author_id: int = Query(..., description="Author user ID"),
    payload: PostCreate = ...,
    session: AsyncSession = Depends(get_db_session)
) -> PostResponse:
    """Create a new community post."""
    service = CommunityService(session)
    post = await service.create_post(author_id, payload)
    await session.commit()
    return PostResponse.model_validate(post)


@router.get("/posts/{post_id}", response_model=PostResponse)
async def get_post(
    post_id: int,
    session: AsyncSession = Depends(get_db_session)
) -> PostResponse:
    """Get a specific post by ID."""
    service = CommunityService(session)
    try:
        post = await service.get_post(post_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    return PostResponse.model_validate(post)


@router.patch("/posts/{post_id}", response_model=PostResponse)
async def update_post(
    post_id: int,
    payload: PostUpdate,
    session: AsyncSession = Depends(get_db_session)
) -> PostResponse:
    """Update an existing post."""
    service = CommunityService(session)
    try:
        post = await service.update_post(post_id, payload)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    await session.commit()
    return PostResponse.model_validate(post)


@router.delete("/posts/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(
    post_id: int,
    session: AsyncSession = Depends(get_db_session)
) -> None:
    """Delete a post."""
    service = CommunityService(session)
    try:
        await service.delete_post(post_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    await session.commit()


# ==================== Comments ====================

@router.get("/posts/{post_id}/comments", response_model=List[CommentResponse])
async def list_comments(
    post_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    session: AsyncSession = Depends(get_db_session)
) -> List[CommentResponse]:
    """List comments for a specific post."""
    service = CommunityService(session)
    comments, _ = await service.list_comments(post_id, skip, limit)
    return [CommentResponse.model_validate(c) for c in comments]


@router.post("/posts/{post_id}/comments", response_model=CommentResponse, status_code=status.HTTP_201_CREATED)
async def create_comment(
    post_id: int,
    author_id: int = Query(..., description="Author user ID"),
    payload: CommentCreate = ...,
    session: AsyncSession = Depends(get_db_session)
) -> CommentResponse:
    """Create a new comment on a post."""
    service = CommunityService(session)
    try:
        comment = await service.create_comment(post_id, author_id, payload)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    await session.commit()
    return CommentResponse.model_validate(comment)


@router.patch("/comments/{comment_id}", response_model=CommentResponse)
async def update_comment(
    comment_id: int,
    payload: CommentUpdate,
    session: AsyncSession = Depends(get_db_session)
) -> CommentResponse:
    """Update a comment."""
    service = CommunityService(session)
    try:
        comment = await service.update_comment(comment_id, payload)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    await session.commit()
    return CommentResponse.model_validate(comment)


@router.delete("/comments/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_comment(
    comment_id: int,
    session: AsyncSession = Depends(get_db_session)
) -> None:
    """Delete a comment."""
    service = CommunityService(session)
    try:
        await service.delete_comment(comment_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    await session.commit()


# ==================== Likes ====================

@router.post("/posts/{post_id}/like", response_model=LikeResponse, status_code=status.HTTP_201_CREATED)
async def like_post(
    post_id: int,
    user_id: int = Query(..., description="User ID liking the post"),
    session: AsyncSession = Depends(get_db_session)
) -> LikeResponse:
    """Like a post."""
    service = CommunityService(session)
    try:
        like = await service.create_post_like(user_id, post_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    await session.commit()
    return LikeResponse.model_validate(like)


@router.post("/comments/{comment_id}/like", response_model=LikeResponse, status_code=status.HTTP_201_CREATED)
async def like_comment(
    comment_id: int,
    user_id: int = Query(..., description="User ID liking the comment"),
    session: AsyncSession = Depends(get_db_session)
) -> LikeResponse:
    """Like a comment."""
    service = CommunityService(session)
    try:
        like = await service.create_comment_like(user_id, comment_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    await session.commit()
    return LikeResponse.model_validate(like)


@router.delete("/likes/{like_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_like(
    like_id: int,
    session: AsyncSession = Depends(get_db_session)
) -> None:
    """Remove a like."""
    service = CommunityService(session)
    try:
        await service.delete_like(like_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    await session.commit()