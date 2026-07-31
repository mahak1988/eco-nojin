"""Community API routes."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.schemas.community import (
    CommentCreate,
    CommentResponse,
    CommentUpdate,
    LikeResponse,
    PostCreate,
    PostListResponse,
    PostResponse,
    PostStats,
    PostUpdate,
)
from apps.api.services.community import CommunityService
from apps.shared_core.database.session import get_db_session
from apps.shared_core.deps import require_write_auth

router = APIRouter(prefix="/api/v1/community", tags=["Community"])


@router.get("/posts", response_model=PostListResponse)
async def list_posts(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    search: str | None = Query(None),
    category: str | None = Query(None),
    author_id: int | None = Query(None),
    session: AsyncSession = Depends(get_db_session),
) -> PostListResponse:
    service = CommunityService(session)
    posts, total = await service.list_posts(skip, limit, search, category, author_id)
    return PostListResponse(items=posts, total=total, skip=skip, limit=limit)


@router.get("/posts/stats", response_model=PostStats)
async def get_post_stats(session: AsyncSession = Depends(get_db_session)) -> PostStats:
    service = CommunityService(session)
    return PostStats(**await service.get_stats())


@router.post("/posts", response_model=PostResponse, status_code=status.HTTP_201_CREATED)
async def create_post(
    payload: PostCreate,
    author_id: int = Query(..., description="Author user ID"),
    session: AsyncSession = Depends(get_db_session),
    _: None = Depends(require_write_auth),
) -> PostResponse:
    service = CommunityService(session)
    post = await service.create_post(author_id, payload)
    return PostResponse.model_validate(post)


@router.get("/posts/{post_id}", response_model=PostResponse)
async def get_post(
    post_id: int,
    session: AsyncSession = Depends(get_db_session),
) -> PostResponse:
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
    session: AsyncSession = Depends(get_db_session),
    _: None = Depends(require_write_auth),
) -> PostResponse:
    service = CommunityService(session)
    try:
        post = await service.update_post(post_id, payload)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    return PostResponse.model_validate(post)


@router.delete("/posts/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(
    post_id: int,
    session: AsyncSession = Depends(get_db_session),
    _: None = Depends(require_write_auth),
) -> None:
    service = CommunityService(session)
    try:
        await service.delete_post(post_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("/posts/{post_id}/comments", response_model=list[CommentResponse])
async def list_comments(
    post_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    session: AsyncSession = Depends(get_db_session),
) -> list[CommentResponse]:
    service = CommunityService(session)
    comments, _ = await service.list_comments(post_id, skip, limit)
    return [CommentResponse.model_validate(c) for c in comments]


@router.post(
    "/posts/{post_id}/comments",
    response_model=CommentResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_comment(
    post_id: int,
    payload: CommentCreate,
    author_id: int = Query(...),
    session: AsyncSession = Depends(get_db_session),
    _: None = Depends(require_write_auth),
) -> CommentResponse:
    service = CommunityService(session)
    try:
        comment = await service.create_comment(post_id, author_id, payload)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    return CommentResponse.model_validate(comment)


@router.patch("/comments/{comment_id}", response_model=CommentResponse)
async def update_comment(
    comment_id: int,
    payload: CommentUpdate,
    session: AsyncSession = Depends(get_db_session),
    _: None = Depends(require_write_auth),
) -> CommentResponse:
    service = CommunityService(session)
    try:
        comment = await service.update_comment(comment_id, payload)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    return CommentResponse.model_validate(comment)


@router.delete("/comments/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_comment(
    comment_id: int,
    session: AsyncSession = Depends(get_db_session),
    _: None = Depends(require_write_auth),
) -> None:
    service = CommunityService(session)
    try:
        await service.delete_comment(comment_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post("/posts/{post_id}/like", response_model=LikeResponse, status_code=status.HTTP_201_CREATED)
async def like_post(
    post_id: int,
    user_id: int = Query(...),
    session: AsyncSession = Depends(get_db_session),
    _: None = Depends(require_write_auth),
) -> LikeResponse:
    service = CommunityService(session)
    try:
        like = await service.create_post_like(user_id, post_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    return LikeResponse.model_validate(like)
