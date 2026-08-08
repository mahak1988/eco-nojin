"""
Community System Tests
=======================
Tests for Post, Comment, Like CRUD — aligned with Integer PKs and is_published.
"""

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.models.community import Comment, Like, Post


@pytest.fixture
async def community_db_session():
    """Create a test database session for community models."""
    from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

    from apps.shared_core.database.session import Base

    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with async_session() as session:
        yield session

    await engine.dispose()


@pytest.mark.asyncio
async def test_post_crud(community_db_session: AsyncSession):
    """Test post CRUD operations with integer autoincrement id."""
    post = Post(
        title="My First Post",
        content="This is test content for the community post",
        author_id=1,
        category="general",
        is_published=True,
    )
    community_db_session.add(post)
    await community_db_session.flush()

    assert post.id is not None
    result = await community_db_session.execute(select(Post).where(Post.id == post.id))
    fetched = result.scalar_one_or_none()
    assert fetched is not None
    assert fetched.title == "My First Post"
    assert fetched.is_published is True

    fetched.title = "Updated Post Title"
    await community_db_session.flush()

    result = await community_db_session.execute(select(Post).where(Post.id == post.id))
    updated = result.scalar_one()
    assert updated.title == "Updated Post Title"


@pytest.mark.asyncio
async def test_comment_crud(community_db_session: AsyncSession):
    """Test comment CRUD operations."""
    post = Post(
        title="Test Post",
        content="Test content",
        author_id=1,
        category="general",
    )
    community_db_session.add(post)
    await community_db_session.flush()

    comment = Comment(
        content="This is a test comment",
        author_id=2,
        post_id=post.id,
    )
    community_db_session.add(comment)
    await community_db_session.flush()

    result = await community_db_session.execute(select(Comment).where(Comment.id == comment.id))
    fetched = result.scalar_one_or_none()
    assert fetched is not None
    assert fetched.content == "This is a test comment"
    assert fetched.post_id == post.id


@pytest.mark.asyncio
async def test_like_crud(community_db_session: AsyncSession):
    """Test like CRUD operations."""
    post = Post(
        title="Liked Post",
        content="Test content",
        author_id=1,
        category="general",
    )
    community_db_session.add(post)
    await community_db_session.flush()

    like = Like(
        user_id=2,
        post_id=post.id,
    )
    community_db_session.add(like)
    await community_db_session.flush()

    result = await community_db_session.execute(select(Like).where(Like.id == like.id))
    fetched = result.scalar_one_or_none()
    assert fetched is not None

    await community_db_session.delete(fetched)
    await community_db_session.flush()

    result = await community_db_session.execute(select(Like).where(Like.id == like.id))
    assert result.scalar_one_or_none() is None


@pytest.mark.asyncio
async def test_post_published_flag():
    """is_published is the publication flag (no PostStatus enum in model)."""
    post = Post(
        title="Draft-like",
        content="x",
        author_id=1,
        category="general",
        is_published=False,
    )
    assert post.is_published is False
    post.is_published = True
    assert post.is_published is True
