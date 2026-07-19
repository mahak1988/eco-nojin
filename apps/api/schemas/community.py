"""
Community Schemas
==================
Pydantic models for request/response validation.
"""

from datetime import datetime
from typing import Optional, List
from enum import Enum

from pydantic import BaseModel, Field, ConfigDict


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
    author_name: Optional[str] = Field(None, max_length=100)
    category: PostCategoryEnum = PostCategoryEnum.GENERAL
    tags: Optional[List[str]] = Field(default_factory=list)


class PostCreate(PostBase):
    pass


class PostUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    content: Optional[str] = None
    author_name: Optional[str] = None
    category: Optional[PostCategoryEnum] = None
    tags: Optional[List[str]] = None
    is_published: Optional[bool] = None


class CommentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    author_name: Optional[str] = None
    content: str
    parent_id: Optional[int] = None
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
    comments: List[CommentResponse] = Field(default_factory=list)

    @classmethod
    def model_validate(cls, obj: "Post") -> "PostResponse":
        data = super().model_validate(obj).model_dump()
        if hasattr(obj, "tags") and obj.tags:
            data["tags"] = [t.strip() for t in obj.tags.split(",") if t.strip()]
        else:
            data["tags"] = []
        return cls(**data)


class PostListResponse(BaseModel):
    items: List[PostResponse]
    total: int
    skip: int = 0
    limit: int = 100


class CommentBase(BaseModel):
    content: str = Field(..., min_length=1)
    author_name: Optional[str] = Field(None, max_length=100)
    parent_id: Optional[int] = None


class CommentCreate(CommentBase):
    pass


class CommentUpdate(BaseModel):
    content: Optional[str] = Field(None, min_length=1)
    author_name: Optional[str] = None


class LikeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    post_id: Optional[int] = None
    comment_id: Optional[int] = None
    created_at: datetime


class PostStats(BaseModel):
    total_posts: int
    total_comments: int
    total_likes: int
    by_category: dict[str, int]