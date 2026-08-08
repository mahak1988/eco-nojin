"""
TEK API Router
==============
Earth Memory Layer API endpoints for historical pattern matching.
"""

import logging

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from apps.shared_core.database.session import get_db_session
from apps.shared_knowledge.knowledge.tek_matcher import format_recommendation, match_pattern
from apps.shared_knowledge.knowledge.tek_models import HistoricalPattern

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/tek", tags=["earth-memory"])


@router.get("/patterns")
async def list_patterns(
    problem_category: str | None = Query(None),
    is_active: bool = True,
    session: AsyncSession = Depends(get_db_session),
):
    """List all available historical TEK patterns with optional filtering."""
    query = select(HistoricalPattern)
    if is_active:
        query = query.where(HistoricalPattern.is_active == True)
    if problem_category:
        query = query.where(HistoricalPattern.problem_category == problem_category)
    query = query.order_by(HistoricalPattern.age_years.desc())
    result = await session.execute(query)
    patterns = result.scalars().all()
    return {
        "total": len(patterns),
        "patterns": [
            {
                "pattern_id": p.pattern_id,
                "name": p.name,
                "name_fa": p.name_fa,
                "civilization": p.civilization,
                "civilization_fa": p.civilization_fa,
                "region": p.region,
                "age_years": p.age_years,
                "problem_category": p.problem_category,
                "solution_type": p.solution_type,
                "climate_zones": p.climate_zones,
                "success_score": p.success_score,
                "sustainability_index": p.sustainability_index,
            }
            for p in patterns
        ],
    }


@router.get("/patterns/{pattern_id}")
async def get_pattern(
    pattern_id: str,
    session: AsyncSession = Depends(get_db_session),
):
    """Get full details of a specific TEK pattern including formulas and principles."""
    result = await session.execute(
        select(HistoricalPattern).where(HistoricalPattern.pattern_id == pattern_id)
    )
    pattern = result.scalar_one_or_none()
    if not pattern:
        raise HTTPException(404, f"Pattern '{pattern_id}' not found")
    return {
        "pattern_id": pattern.pattern_id,
        "name": pattern.name,
        "name_fa": pattern.name_fa,
        "civilization": pattern.civilization,
        "civilization_fa": pattern.civilization_fa,
        "region": pattern.region,
        "age_years": pattern.age_years,
        "problem_category": pattern.problem_category,
        "solution_type": pattern.solution_type,
        "climate_zones": pattern.climate_zones,
        "principles": pattern.principles,
        "applicability_conditions": pattern.applicability_conditions,
        "formulas": pattern.formulas,
        "recommendation_template": pattern.recommendation_template,
        "recommendation_template_fa": pattern.recommendation_template_fa,
        "success_score": pattern.success_score,
        "sustainability_index": pattern.sustainability_index,
    }


@router.post("/match")
async def match_conditions(
    climate_zone: str = Query(..., description="Koppen climate zone, e.g. BWk"),
    latitude: float = Query(...),
    longitude: float = Query(...),
    annual_rainfall_mm: float | None = Query(None),
    groundwater_depth_m: float | None = Query(None),
    elevation_m: float | None = Query(None),
    soil_organic_carbon_pct: float | None = Query(None),
    frost_risk: bool | None = Query(None),
    top_n: int = Query(5, ge=1, le=20),
    session: AsyncSession = Depends(get_db_session),
):
    """Match current environmental conditions against historical TEK patterns."""
    result = await session.execute(
        select(HistoricalPattern).where(HistoricalPattern.is_active == True)
    )
    patterns = result.scalars().all()

    if not patterns:
        raise HTTPException(404, "No TEK patterns available in database")

    matches = []
    for pattern in patterns:
        score, components = match_pattern(
            climate_zone=climate_zone,
            annual_rainfall_mm=annual_rainfall_mm,
            groundwater_depth_m=groundwater_depth_m,
            elevation_m=elevation_m,
            soil_organic_carbon_pct=soil_organic_carbon_pct,
            frost_risk=frost_risk,
            pattern_climate_zones=pattern.climate_zones,
            pattern_conditions=pattern.applicability_conditions,
            pattern_age_years=pattern.age_years,
        )

        rec = format_recommendation(
            template=pattern.recommendation_template_fa or pattern.recommendation_template,
            pattern_name=pattern.name,
            civilization=pattern.civilization,
            age_years=pattern.age_years,
            score=score,
            climate_zone=climate_zone,
        )

        matches.append(
            {
                "pattern_id": pattern.pattern_id,
                "name": pattern.name,
                "name_fa": pattern.name_fa,
                "civilization": pattern.civilization_fa,
                "age_years": pattern.age_years,
                "match_score": round(score, 3),
                "score_components": {k: round(v, 3) for k, v in components.items()},
                "problem_category": pattern.problem_category,
                "solution_type": pattern.solution_type,
                "recommendation": rec,
                "principles": pattern.principles,
            }
        )

    matches.sort(key=lambda m: m["match_score"], reverse=True)

    return {
        "query": {
            "climate_zone": climate_zone,
            "latitude": latitude,
            "longitude": longitude,
            "annual_rainfall_mm": annual_rainfall_mm,
        },
        "total_matches": len(matches),
        "top_matches": matches[:top_n],
        "match_threshold_note": "Scores above 0.5 indicate relevant patterns. Scores above 0.7 are strong matches.",
    }


@router.get("/recommendations")
async def get_top_recommendations(
    problem_category: str | None = Query(None),
    session: AsyncSession = Depends(get_db_session),
):
    """Get top TEK recommendations, optionally filtered by problem category."""
    query = select(HistoricalPattern).where(HistoricalPattern.is_active == True)
    if problem_category:
        query = query.where(HistoricalPattern.problem_category == problem_category)
    query = query.order_by(
        HistoricalPattern.success_score.desc(), HistoricalPattern.age_years.desc()
    )
    result = await session.execute(query)
    patterns = result.scalars().all()

    return {
        "recommendations": [
            {
                "pattern_id": p.pattern_id,
                "name_fa": p.name_fa,
                "civilization_fa": p.civilization_fa,
                "problem_category": p.problem_category,
                "recommendation": p.recommendation_template_fa or p.recommendation_template,
                "success_score": p.success_score,
            }
            for p in patterns
        ]
    }
