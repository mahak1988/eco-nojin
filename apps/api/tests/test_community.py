"""
Community System Tests
=======================
Tests for Post, Comment, Like CRUD operations.
"""

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.models.community import Post, Comment, Like, PostStatus


@pytest.fixture
async def community_db_session():
    """Create a test database session for community models."""
    from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
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
    """Test post CRUD operations."""
    # Create
    post = Post(
        id="post-1",
        title="My First Post",
        content="This is test content for the community post",
        author_id="user-1",
        status=PostStatus.PUBLISHED,
    )
    community_db_session.add(post)
    await community_db_session.flush()

    # Read
    result = await community_db_session.execute(select(Post).where(Post.id == "post-1"))
    fetched = result.scalar_one_or_none()
    assert fetched is not None
    assert fetched.title == "My First Post"
    assert fetched.status == PostStatus.PUBLISHED

    # Update
    fetched.title = "Updated Post Title"
    await community_db_session.flush()

    result = await community_db_session.execute(select(Post).where(Post.id == "post-1"))
    updated = result.scalar_one()
    assert updated.title == "Updated Post Title"


@pytest.mark.asyncio
async def test_comment_crud(community_db_session: AsyncSession):
    """Test comment CRUD operations."""
    # Create post first
    post = Post(
        id="post-2",
        title="Test Post",
        content="Test content",
        author_id="user-1",
    )
    community_db_session.add(post)
    await community_db_session.flush()

    # Create comment
    comment = Comment(
        id="comment-1",
        content="This is a test comment",
        author_id="user-2",
        post_id="post-2",
    )
    community_db_session.add(comment)
    await community_db_session.flush()

    # Read
    result = await community_db_session.execute(select(Comment).where(Comment.id == "comment-1"))
    fetched = result.scalar_one_or_none()
    assert fetched is not None
    assert fetched.content == "This is a test comment"
    assert fetched.post_id == "post-2"


@pytest.mark.asyncio
async def test_like_crud(community_db_session: AsyncSession):
    """Test like CRUD operations."""
    # Create post and user
    post = Post(
        id="post-3",
        title="Liked Post",
        content="Test content",
        author_id="user-1",
    )
    community_db_session.add(post)
    await community_db_session.flush()

    # Create like
    like = Like(
        id="like-1",
        user_id="user-2",
        post_id="post-3",
    )
    community_db_session.add(like)
    await community_db_session.flush()

    # Read
    result = await community_db_session.execute(select(Like).where(Like.id == "like-1"))
    fetched = result.scalar_one_or_none()
    assert fetched is not None

    # Delete like
    await community_db_session.delete(fetched)
    await community_db_session.flush()

    result = await community_db_session.execute(select(Like).where(Like.id == "like-1"))
    assert result.scalar_one_or_none() is None


@pytest.mark.asyncio
async def test_post_status_enum():
    """Test post status enum values."""
    assert PostStatus.DRAFT == "draft"
    assert PostStatus.PUBLISHED == "published"
    assert PostStatus.ARCHIVED == "archived"