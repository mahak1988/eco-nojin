"""
Community Schemas
==================
Pydantic models for request/response validation.
"""

import logging

logger = logging.getLogger(__name__)
from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class PostCategoryEnum(str, Enum):
    GENERAL = "general"
    AGRICULTURE = "agriculture"
    WATER = "water"
    ENVIRONMENT = "environment"
    ECONOMICS = "economics"
    TECHNOLOGY = "technology"


class PostBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    content: str = Field(..., min_length=1)
    author_name: str | None = Field(None, max_length=100)
    category: PostCategoryEnum = PostCategoryEnum.GENERAL
    tags: list[str] | None = Field(default_factory=list)


class PostCreate(PostBase):
    pass


class PostUpdate(BaseModel):
    title: str | None = Field(None, min_length=1, max_length=255)
    content: str | None = None
    author_name: str | None = None
    category: PostCategoryEnum | None = None
    tags: list[str] | None = None
    is_published: bool | None = None


class CommentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    author_name: str | None = None
    content: str
    parent_id: int | None = None
    like_count: int
    created_at: datetime


class PostResponse(PostBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    author_id: int
    is_published: bool
    like_count: int
    comment_count: int
    created_at: datetime
    updated_at: datetime
    comments: list[CommentResponse] = Field(default_factory=list)

    @classmethod
    def model_validate(cls, obj: "Post") -> "PostResponse":
        """Handle model_validate (cls, obj)."""
        data = super().model_validate(obj).model_dump()
        if hasattr(obj, "tags") and obj.tags:
            data["tags"] = [t.strip() for t in obj.tags.split(",") if t.strip()]
        else:
            data["tags"] = []
        return cls(**data)


class PostListResponse(BaseModel):
    items: list[PostResponse]
    total: int
    skip: int = 0
    limit: int = 100


class CommentBase(BaseModel):
    content: str = Field(..., min_length=1)
    author_name: str | None = Field(None, max_length=100)
    parent_id: int | None = None


class CommentCreate(CommentBase):
    pass


class CommentUpdate(BaseModel):
    content: str | None = Field(None, min_length=1)
    author_name: str | None = None


class LikeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    post_id: int | None = None
    comment_id: int | None = None
    created_at: datetime


class PostStats(BaseModel):
    total_posts: int
    total_comments: int
    total_likes: int
    by_category: dict[str, int]
