# api/modules/library/router.py
"""
Router API کتابخانه دیجیتال
نسخه 2.0 - با سیستم تایید و دانشنامه کهن
"""
from api.core.schemas import SuccessResponse, IDResponse, StatsResponse, PaginatedResponse
from datetime import datetime
from typing import Dict, Any, List, Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile
from pydantic import BaseModel
from sqlalchemy import and_, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from api.core.database import get_db
from api.core.security import require_reviewer_or_admin
from api.modules.library.models import (
    AncientKnowledge,
    AncientKnowledgeCategory,
    ApprovalStatus,
    Publication,
    ResearchChallenge,
    ResearchGroup,
    ResearchLocation,
    User,
)

router = APIRouter(prefix="/library", tags=["Digital Library"])


# ============================================================
# Models
# ============================================================
class ResearchLocationCreate(BaseModel):
    name: str
    name_en: Optional[str] = None
    description: Optional[str] = None
    latitude: float
    longitude: float
    radius_km: float = 10
    image_url: Optional[str] = None
    research_topics: List[str] = []
    submitted_by_id: int


class ResearchGroupCreate(BaseModel):
    name: str
    name_en: Optional[str] = None
    description: Optional[str] = None
    cover_image_url: Optional[str] = None
    logo_url: Optional[str] = None
    research_areas: List[str] = []
    leader_id: int
    max_members: int = 50
    is_public: bool = True
    submitted_by_id: int


class ResearchChallengeCreate(BaseModel):
    title: str
    title_en: Optional[str] = None
    description: str
    cover_image_url: Optional[str] = None
    research_area: str
    difficulty_level: str = "intermediate"
    start_date: datetime
    end_date: datetime
    prize_description: Optional[str] = None
    prize_amount: Optional[float] = None
    evaluation_criteria: dict = {}
    submitted_by_id: int


class AncientKnowledgeCreate(BaseModel):
    title: str
    title_en: Optional[str] = None
    description: str
    content: Optional[str] = None
    category: str
    subcategory: Optional[str] = None
    tags: List[str] = []
    origin_location: Optional[str] = None
    origin_latitude: Optional[float] = None
    origin_longitude: Optional[float] = None
    cover_image_url: Optional[str] = None
    gallery_images: List[str] = []
    sources: List[str] = []
    references: Optional[str] = None
    historical_period: Optional[str] = None
    century: Optional[str] = None
    civilization: Optional[str] = None
    original_language: Optional[str] = None
    submitted_by_id: int


class ApprovalRequest(BaseModel):
    approved_by_id: int
    rejection_reason: Optional[str] = None


# ============================================================
# Research Locations Endpoints
# ============================================================
@router.get("/research-locations", response_model=Dict[str, Any])
async def list_research_locations(approved_only: bool = True, db: AsyncSession = Depends(get_db)):
    """لیست مکان‌های تحقیقاتی"""
    query = select(ResearchLocation)
    if approved_only:
        query = query.where(ResearchLocation.approval_status == ApprovalStatus.APPROVED)

    result = await db.execute(query)
    locations = result.scalars().all()

    return {
        "count": len(locations),
        "locations": [
            {
                "id": loc.id,
                "name": loc.name,
                "description": loc.description,
                "latitude": loc.latitude,
                "longitude": loc.longitude,
                "radius_km": loc.radius_km,
                "image_url": loc.image_url,
                "research_topics": loc.research_topics,
                "publication_count": loc.publication_count,
                "approval_status": loc.approval_status.value,
                "created_at": loc.created_at,
            }
            for loc in locations
        ],
    }


@router.post("/research-locations", response_model=Dict[str, Any])
async def create_research_location(
    location: ResearchLocationCreate, db: AsyncSession = Depends(get_db)
):
    """ایجاد درخواست مکان تحقیقاتی جدید"""
    new_location = ResearchLocation(
        name=location.name,
        name_en=location.name_en,
        description=location.description,
        latitude=location.latitude,
        longitude=location.longitude,
        radius_km=location.radius_km,
        image_url=location.image_url,
        research_topics=location.research_topics,
        submitted_by_id=location.submitted_by_id,
        approval_status=ApprovalStatus.PENDING,
    )

    db.add(new_location)
    await db.commit()
    await db.refresh(new_location)

    return {
        "id": new_location.id,
        "status": "pending_approval",
        "message": "درخواست شما ثبت شد و پس از تایید مدیر نمایش داده خواهد شد",
    }


@router.put("/research-locations/{location_id}/approve", response_model=IDResponse)
async def approve_research_location(
    location_id: int, approval: ApprovalRequest, db: AsyncSession = Depends(get_db)
):
    """تایید مکان تحقیقاتی"""
    result = await db.execute(select(ResearchLocation).where(ResearchLocation.id == location_id))
    location = result.scalar_one_or_none()

    if not location:
        raise HTTPException(404, "مکان یافت نشد")

    location.approval_status = ApprovalStatus.APPROVED
    location.approved_by_id = approval.approved_by_id
    location.approved_at = datetime.utcnow()

    await db.commit()

    return {"status": "approved", "id": location_id}


@router.put("/research-locations/{location_id}/reject", response_model=Dict[str, Any])
async def reject_research_location(
    location_id: int, approval: ApprovalRequest, db: AsyncSession = Depends(get_db)
):
    """رد مکان تحقیقاتی"""
    result = await db.execute(select(ResearchLocation).where(ResearchLocation.id == location_id))
    location = result.scalar_one_or_none()

    if not location:
        raise HTTPException(404, "مکان یافت نشد")

    location.approval_status = ApprovalStatus.REJECTED
    location.approved_by_id = approval.approved_by_id
    location.approved_at = datetime.utcnow()

    await db.commit()

    return {"status": "rejected", "id": location_id}


# ============================================================
# Research Groups Endpoints
# ============================================================
@router.get("/research-groups", response_model=Dict[str, Any])
async def list_research_groups(approved_only: bool = True, db: AsyncSession = Depends(get_db)):
    """لیست گروه‌های تحقیقاتی"""
    query = select(ResearchGroup)
    if approved_only:
        query = query.where(ResearchGroup.approval_status == ApprovalStatus.APPROVED)

    result = await db.execute(query)
    groups = result.scalars().all()

    return {
        "count": len(groups),
        "groups": [
            {
                "id": g.id,
                "name": g.name,
                "description": g.description,
                "cover_image_url": g.cover_image_url,
                "logo_url": g.logo_url,
                "research_areas": g.research_areas,
                "current_members": g.current_members,
                "max_members": g.max_members,
                "approval_status": g.approval_status.value,
                "created_at": g.created_at,
            }
            for g in groups
        ],
    }


@router.post("/research-groups", response_model=Dict[str, Any])
async def create_research_group(group: ResearchGroupCreate, db: AsyncSession = Depends(get_db)):
    """ایجاد درخواست گروه تحقیقاتی"""
    new_group = ResearchGroup(
        name=group.name,
        name_en=group.name_en,
        description=group.description,
        cover_image_url=group.cover_image_url,
        logo_url=group.logo_url,
        research_areas=group.research_areas,
        leader_id=group.leader_id,
        max_members=group.max_members,
        is_public=group.is_public,
        submitted_by_id=group.submitted_by_id,
        approval_status=ApprovalStatus.PENDING,
    )

    db.add(new_group)
    await db.commit()
    await db.refresh(new_group)

    return {
        "id": new_group.id,
        "status": "pending_approval",
        "message": "درخواست شما ثبت شد و پس از تایید مدیر نمایش داده خواهد شد",
    }


@router.put("/research-groups/{group_id}/approve", response_model=IDResponse)
async def approve_research_group(
    group_id: int, approval: ApprovalRequest, db: AsyncSession = Depends(get_db)
):
    """تایید گروه تحقیقاتی"""
    result = await db.execute(select(ResearchGroup).where(ResearchGroup.id == group_id))
    group = result.scalar_one_or_none()

    if not group:
        raise HTTPException(404, "گروه یافت نشد")

    group.approval_status = ApprovalStatus.APPROVED
    group.approved_by_id = approval.approved_by_id
    group.approved_at = datetime.utcnow()

    await db.commit()

    return {"status": "approved", "id": group_id}


@router.put("/research-groups/{group_id}/reject", response_model=Dict[str, Any])
async def reject_research_group(
    group_id: int, approval: ApprovalRequest, db: AsyncSession = Depends(get_db)
):
    """رد گروه تحقیقاتی"""
    result = await db.execute(select(ResearchGroup).where(ResearchGroup.id == group_id))
    group = result.scalar_one_or_none()

    if not group:
        raise HTTPException(404, "گروه یافت نشد")

    group.approval_status = ApprovalStatus.REJECTED
    group.approved_by_id = approval.approved_by_id
    group.approved_at = datetime.utcnow()

    await db.commit()

    return {"status": "rejected", "id": group_id}


# ============================================================
# Research Challenges Endpoints
# ============================================================
@router.get("/challenges", response_model=Dict[str, Any])
async def list_challenges(
    approved_only: bool = True, status: Optional[str] = None, db: AsyncSession = Depends(get_db)
):
    """لیست چالش‌های پژوهشی"""
    query = select(ResearchChallenge)
    if approved_only:
        query = query.where(ResearchChallenge.approval_status == ApprovalStatus.APPROVED)
    if status:
        query = query.where(ResearchChallenge.status == status)

    result = await db.execute(query)
    challenges = result.scalars().all()

    return {
        "count": len(challenges),
        "challenges": [
            {
                "id": c.id,
                "title": c.title,
                "description": c.description,
                "cover_image_url": c.cover_image_url,
                "research_area": c.research_area,
                "difficulty_level": c.difficulty_level,
                "start_date": c.start_date,
                "end_date": c.end_date,
                "prize_amount": c.prize_amount,
                "participant_count": c.participant_count,
                "status": c.status,
                "approval_status": c.approval_status.value,
                "created_at": c.created_at,
            }
            for c in challenges
        ],
    }


@router.post("/challenges", response_model=Dict[str, Any])
async def create_challenge(challenge: ResearchChallengeCreate, db: AsyncSession = Depends(get_db)):
    """ایجاد درخواست چالش پژوهشی"""
    new_challenge = ResearchChallenge(
        title=challenge.title,
        title_en=challenge.title_en,
        description=challenge.description,
        cover_image_url=challenge.cover_image_url,
        research_area=challenge.research_area,
        difficulty_level=challenge.difficulty_level,
        start_date=challenge.start_date,
        end_date=challenge.end_date,
        prize_description=challenge.prize_description,
        prize_amount=challenge.prize_amount,
        evaluation_criteria=challenge.evaluation_criteria,
        submitted_by_id=challenge.submitted_by_id,
        approval_status=ApprovalStatus.PENDING,
    )

    db.add(new_challenge)
    await db.commit()
    await db.refresh(new_challenge)

    return {
        "id": new_challenge.id,
        "status": "pending_approval",
        "message": "درخواست شما ثبت شد و پس از تایید مدیر نمایش داده خواهد شد",
    }


@router.put("/challenges/{challenge_id}/approve", response_model=IDResponse)
async def approve_challenge(
    challenge_id: int, approval: ApprovalRequest, db: AsyncSession = Depends(get_db)
):
    """تایید چالش پژوهشی"""
    result = await db.execute(select(ResearchChallenge).where(ResearchChallenge.id == challenge_id))
    challenge = result.scalar_one_or_none()

    if not challenge:
        raise HTTPException(404, "چالش یافت نشد")

    challenge.approval_status = ApprovalStatus.APPROVED
    challenge.approved_by_id = approval.approved_by_id
    challenge.approved_at = datetime.utcnow()

    await db.commit()

    return {"status": "approved", "id": challenge_id}


@router.put("/challenges/{challenge_id}/reject", response_model=Dict[str, Any])
async def reject_challenge(
    challenge_id: int, approval: ApprovalRequest, db: AsyncSession = Depends(get_db)
):
    """رد چالش پژوهشی"""
    result = await db.execute(select(ResearchChallenge).where(ResearchChallenge.id == challenge_id))
    challenge = result.scalar_one_or_none()

    if not challenge:
        raise HTTPException(404, "چالش یافت نشد")

    challenge.approval_status = ApprovalStatus.REJECTED
    challenge.approved_by_id = approval.approved_by_id
    challenge.approved_at = datetime.utcnow()

    await db.commit()

    return {"status": "rejected", "id": challenge_id}


# ============================================================
# Ancient Knowledge Endpoints
# ============================================================
@router.get("/ancient-knowledge", response_model=Dict[str, Any])
async def list_ancient_knowledge(
    category: Optional[str] = None, approved_only: bool = True, db: AsyncSession = Depends(get_db)
):
    """لیست دانشنامه کهن"""
    query = select(AncientKnowledge)
    if approved_only:
        query = query.where(AncientKnowledge.approval_status == ApprovalStatus.APPROVED)
    if category:
        query = query.where(AncientKnowledge.category == category)

    result = await db.execute(query)
    knowledge_items = result.scalars().all()

    return {
        "count": len(knowledge_items),
        "items": [
            {
                "id": k.id,
                "title": k.title,
                "description": k.description,
                "category": k.category,
                "subcategory": k.subcategory,
                "tags": k.tags,
                "origin_location": k.origin_location,
                "cover_image_url": k.cover_image_url,
                "historical_period": k.historical_period,
                "century": k.century,
                "civilization": k.civilization,
                "view_count": k.view_count,
                "rating_average": k.rating_average,
                "approval_status": k.approval_status.value,
                "created_at": k.created_at,
            }
            for k in knowledge_items
        ],
    }


@router.get("/ancient-knowledge/{knowledge_id}", response_model=Dict[str, Any])
async def get_ancient_knowledge(knowledge_id: int, db: AsyncSession = Depends(get_db)):
    """دریافت جزئیات یک مورد دانشنامه کهن"""
    result = await db.execute(select(AncientKnowledge).where(AncientKnowledge.id == knowledge_id))
    knowledge = result.scalar_one_or_none()

    if not knowledge:
        raise HTTPException(404, "مورد یافت نشد")

    # افزایش تعداد بازدید
    knowledge.view_count += 1
    await db.commit()

    return {
        "id": knowledge.id,
        "title": knowledge.title,
        "title_en": knowledge.title_en,
        "description": knowledge.description,
        "content": knowledge.content,
        "category": knowledge.category,
        "subcategory": knowledge.subcategory,
        "tags": knowledge.tags,
        "origin_location": knowledge.origin_location,
        "origin_latitude": knowledge.origin_latitude,
        "origin_longitude": knowledge.origin_longitude,
        "cover_image_url": knowledge.cover_image_url,
        "gallery_images": knowledge.gallery_images,
        "sources": knowledge.sources,
        "references": knowledge.references,
        "historical_period": knowledge.historical_period,
        "century": knowledge.century,
        "civilization": knowledge.civilization,
        "original_language": knowledge.original_language,
        "view_count": knowledge.view_count,
        "rating_average": knowledge.rating_average,
        "created_at": knowledge.created_at,
    }


@router.post("/ancient-knowledge", response_model=Dict[str, Any])
async def create_ancient_knowledge(
    knowledge: AncientKnowledgeCreate, db: AsyncSession = Depends(get_db)
):
    """ایجاد مورد جدید در دانشنامه کهن"""
    new_knowledge = AncientKnowledge(
        title=knowledge.title,
        title_en=knowledge.title_en,
        description=knowledge.description,
        content=knowledge.content,
        category=knowledge.category,
        subcategory=knowledge.subcategory,
        tags=knowledge.tags,
        origin_location=knowledge.origin_location,
        origin_latitude=knowledge.origin_latitude,
        origin_longitude=knowledge.origin_longitude,
        cover_image_url=knowledge.cover_image_url,
        gallery_images=knowledge.gallery_images,
        sources=knowledge.sources,
        references=knowledge.references,
        historical_period=knowledge.historical_period,
        century=knowledge.century,
        civilization=knowledge.civilization,
        original_language=knowledge.original_language,
        submitted_by_id=knowledge.submitted_by_id,
        approval_status=ApprovalStatus.PENDING,
    )

    db.add(new_knowledge)
    await db.commit()
    await db.refresh(new_knowledge)

    return {
        "id": new_knowledge.id,
        "status": "pending_approval",
        "message": "مورد دانشنامه کهن ثبت شد و پس از تایید مدیر نمایش داده خواهد شد",
    }


@router.put("/ancient-knowledge/{knowledge_id}/approve", response_model=IDResponse)
async def approve_ancient_knowledge(
    knowledge_id: int, approval: ApprovalRequest, db: AsyncSession = Depends(get_db)
):
    """تایید مورد دانشنامه کهن"""
    result = await db.execute(select(AncientKnowledge).where(AncientKnowledge.id == knowledge_id))
    knowledge = result.scalar_one_or_none()

    if not knowledge:
        raise HTTPException(404, "مورد یافت نشد")

    knowledge.approval_status = ApprovalStatus.APPROVED
    knowledge.approved_by_id = approval.approved_by_id
    knowledge.approved_at = datetime.utcnow()

    await db.commit()

    return {"status": "approved", "id": knowledge_id}


@router.put("/ancient-knowledge/{knowledge_id}/reject", response_model=Dict[str, Any])
async def reject_ancient_knowledge(
    knowledge_id: int, approval: ApprovalRequest, db: AsyncSession = Depends(get_db)
):
    """رد مورد دانشنامه کهن"""
    result = await db.execute(select(AncientKnowledge).where(AncientKnowledge.id == knowledge_id))
    knowledge = result.scalar_one_or_none()

    if not knowledge:
        raise HTTPException(404, "مورد یافت نشد")

    knowledge.approval_status = ApprovalStatus.REJECTED
    knowledge.approved_by_id = approval.approved_by_id
    knowledge.approved_at = datetime.utcnow()

    await db.commit()

    return {"status": "rejected", "id": knowledge_id}


@router.get("/ancient-knowledge/categories", response_model=Dict[str, Any])
async def list_ancient_knowledge_categories(db: AsyncSession = Depends(get_db)):
    """لیست دسته‌بندی‌های دانشنامه کهن"""
    result = await db.execute(select(AncientKnowledgeCategory))
    categories = result.scalars().all()

    return {
        "categories": [
            {
                "id": c.id,
                "name": c.name,
                "name_en": c.name_en,
                "description": c.description,
                "icon": c.icon,
                "color": c.color,
                "knowledge_count": c.knowledge_count,
            }
            for c in categories
        ]
    }


# ============================================================
# Pending Approvals (برای مدیر)
# ============================================================
@router.get("/pending-approvals", response_model=Dict[str, Any])
async def list_pending_approvals(db: AsyncSession = Depends(get_db)):
    """لیست تمام درخواست‌های در انتظار تایید"""
    # مکان‌های تحقیقاتی
    locations_result = await db.execute(
        select(ResearchLocation).where(ResearchLocation.approval_status == ApprovalStatus.PENDING)
    )
    pending_locations = locations_result.scalars().all()

    # گروه‌های تحقیقاتی
    groups_result = await db.execute(
        select(ResearchGroup).where(ResearchGroup.approval_status == ApprovalStatus.PENDING)
    )
    pending_groups = groups_result.scalars().all()

    # چالش‌ها
    challenges_result = await db.execute(
        select(ResearchChallenge).where(ResearchChallenge.approval_status == ApprovalStatus.PENDING)
    )
    pending_challenges = challenges_result.scalars().all()

    # دانشنامه کهن
    knowledge_result = await db.execute(
        select(AncientKnowledge).where(AncientKnowledge.approval_status == ApprovalStatus.PENDING)
    )
    pending_knowledge = knowledge_result.scalars().all()

    return {
        "locations": [
            {
                "id": loc.id,
                "type": "research_location",
                "name": loc.name,
                "description": loc.description,
                "image_url": loc.image_url,
                "submitted_at": loc.created_at,
            }
            for loc in pending_locations
        ],
        "groups": [
            {
                "id": g.id,
                "type": "research_group",
                "name": g.name,
                "description": g.description,
                "cover_image_url": g.cover_image_url,
                "submitted_at": g.created_at,
            }
            for g in pending_groups
        ],
        "challenges": [
            {
                "id": c.id,
                "type": "research_challenge",
                "title": c.title,
                "description": c.description,
                "cover_image_url": c.cover_image_url,
                "submitted_at": c.created_at,
            }
            for c in pending_challenges
        ],
        "ancient_knowledge": [
            {
                "id": k.id,
                "type": "ancient_knowledge",
                "title": k.title,
                "description": k.description,
                "category": k.category,
                "cover_image_url": k.cover_image_url,
                "submitted_at": k.created_at,
            }
            for k in pending_knowledge
        ],
        "total_count": len(pending_locations)
        + len(pending_groups)
        + len(pending_challenges)
        + len(pending_knowledge),
    }
