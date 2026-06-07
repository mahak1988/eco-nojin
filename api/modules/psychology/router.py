# api/modules/psychology/router.py
from api.core.schemas import SuccessResponse, IDResponse, StatsResponse, PaginatedResponse
from typing import Dict, Any, List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.core.database import get_db
from api.modules.psychology.engine import TEST_REGISTRY, calculate_result
from api.modules.psychology.models import (
    EcoPsychProfile,
    PsychOption,
    PsychQuestion,
    PsychResult,
    PsychTest,
)


def get_detailed_analysis(test_code: str, total_score: float):
    """دریافت تحلیل دقیق بر اساس بازه نمره"""
    meta = INTERPRETATION_DB.get(test_code)
    if not meta:
        return {
            "level": "نامشخص",
            "analysis": "تحلیل در دسترس نیست",
            "advice": "",
            "color": "#64748b",
        }

    # یافتن بازه مناسب
    for (min_score, max_score), data in meta["ranges"].items():
        if min_score <= total_score <= max_score:
            return {
                "level": data["level"],
                "analysis": data["analysis"],
                "advice": data["advice"],
                "color": CATEGORY_COLORS.get(meta.get("category", "CLINICAL"), "#64748b"),
                "max_score": meta["max_score"],
            }
    return {"level": "خارج از محدوده", "analysis": "", "advice": "", "color": "#64748b"}


router = APIRouter(prefix="/psychology", tags=["Advanced Psychology"])


class AnswerSubmit(BaseModel):
    user_id: int
    test_code: str
    answers: List[dict]  # [{"question_id": 1, "score_value": 4}]


@router.get("/tests", response_model=Dict[str, Any])
async def get_tests(category: Optional[str] = None, db: AsyncSession = Depends(get_db)):
    query = select(PsychTest).where(PsychTest.is_active == True)
    if category:
        query = query.where(PsychTest.category == category)
    result = await db.execute(query)
    tests = result.scalars().all()
    return {
        "tests": [
            {
                "code": t.code,
                "title": t.title,
                "category": t.category.value,
                "duration_minutes": t.duration_minutes,
            }
            for t in tests
        ]
    }


@router.get("/tests/{test_code}", response_model=Dict[str, Any])
async def get_test_details(test_code: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(PsychTest).where(PsychTest.code == test_code))
    test = result.scalar_one_or_none()
    if not test:
        raise HTTPException(404, "آزمون یافت نشد")

    q_result = await db.execute(
        select(PsychQuestion)
        .where(PsychQuestion.test_id == test.id)
        .order_by(PsychQuestion.question_number)
    )
    questions = q_result.scalars().all()

    questions_data = []
    for q in questions:
        opt_result = await db.execute(select(PsychOption).where(PsychOption.question_id == q.id))
        options = [
            {"id": o.id, "label": o.label, "score_value": o.score_value}
            for o in opt_result.scalars().all()
        ]
        questions_data.append(
            {
                "id": q.id,
                "text": q.text,
                "subscale": q.subscale_code,
                "is_reverse_scored": q.is_reverse_scored,
                "options": options,
            }
        )

    return {
        "test": {"code": test.code, "title": test.title, "description": test.description},
        "questions": questions_data,
    }


@router.post("/submit", response_model=Dict[str, Any])
async def submit_test(data: AnswerSubmit, db: AsyncSession = Depends(get_db)):
    test_result = await db.execute(select(PsychTest).where(PsychTest.code == data.test_code))
    test = test_result.scalar_one_or_none()
    if not test:
        raise HTTPException(404, "آزمون نامعتبر است")

    q_result = await db.execute(
        select(PsychQuestion)
        .where(PsychQuestion.test_id == test.id)
        .order_by(PsychQuestion.question_number)
    )
    questions_meta = [
        {"subscale_code": q.subscale_code, "is_reverse_scored": q.is_reverse_scored}
        for q in q_result.scalars().all()
    ]

    raw_result = calculate_result(data.test_code, data.answers, questions_meta)
    detailed_analysis = get_detailed_analysis(data.test_code, raw_result["total_score"])
    interpretation = {**raw_result, **detailed_analysis}

    result_db = PsychResult(
        user_id=data.user_id,
        test_code=data.test_code,
        raw_scores=interpretation["subscale_scores"],
        interpretation=interpretation,
    )
    db.add(result_db)
    await db.commit()

    return {"status": "success", "result": interpretation}


@router.get("/profile/{user_id}", response_model=IDResponse)
async def get_profile(user_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(EcoPsychProfile).where(EcoPsychProfile.user_id == user_id))
    profile = result.scalar_one_or_none()
    if not profile:
        profile = EcoPsychProfile(user_id=user_id)
        db.add(profile)
        await db.commit()
    return {
        "profile": {
            "eco_identity": profile.eco_identity_score,
            "resilience": profile.climate_resilience_score,
            "cooperation": profile.cooperation_score,
        }
    }
