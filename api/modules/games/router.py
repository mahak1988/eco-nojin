# api/modules/games/router.py
from api.core.schemas import SuccessResponse, IDResponse, StatsResponse, PaginatedResponse
from typing import Dict, Any, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.core.database import get_db
from api.modules.games.models import EducationalGame, GameProgress

router = APIRouter(prefix="/games", tags=["Educational Games"])


class GameProgressUpdate(BaseModel):
    user_id: int
    game_id: int
    completed: bool = False
    score: Optional[int] = None
    time_spent_minutes: Optional[int] = None
    reflections: Optional[str] = None


@router.get("/list", response_model=Dict[str, Any])
async def get_games(
    category: Optional[str] = None,
    difficulty: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    """لیست بازیهای آموزشی"""
    try:
        query = select(EducationalGame).where(EducationalGame.is_active == True)

        if category and category != "all":
            query = query.where(EducationalGame.category == category)
        if difficulty:
            query = query.where(EducationalGame.difficulty == difficulty)

        result = await db.execute(query)
        games = result.scalars().all()

        return {
            "games": [
                {
                    "id": g.id,
                    "title": g.title,
                    "description": g.description,
                    "category": g.category,
                    "thumbnail_url": g.thumbnail_url,
                    "difficulty": g.difficulty,
                    "duration_minutes": g.duration_minutes,
                    "age_range": g.age_range,
                    "play_count": g.play_count or 0,
                    "rating_average": g.rating_average or 0,
                    "is_featured": g.is_featured,
                }
                for g in games
            ],
            "total": len(games),
        }
    except Exception as e:
        print(f"Error in get_games: {e}")
        return {"games": [], "total": 0}


@router.get("/categories", response_model=Dict[str, Any])
async def get_categories():
    """لیست دستهبندیها"""
    return {
        "categories": [
            {"id": "ENVIRONMENT", "name": "محیط زیست", "icon": "🌍", "color": "#10b981"},
            {"id": "AGRICULTURE", "name": "کشاورزی", "icon": "🌾", "color": "#84cc16"},
            {"id": "CLIMATE", "name": "تغییر اقلیم", "icon": "🌡️", "color": "#f59e0b"},
            {"id": "WATER", "name": "مدیریت آب", "icon": "💧", "color": "#3b82f6"},
            {"id": "PUZZLE", "name": "پازل و منطق", "icon": "🧩", "color": "#8b5cf6"},
            {"id": "SCIENCE", "name": "علوم پایه", "icon": "🔬", "color": "#ec4899"},
            {"id": "MATH", "name": "ریاضیات", "icon": "📐", "color": "#6366f1"},
            {"id": "STRATEGY", "name": "استراتی", "icon": "♟️", "color": "#f97316"},
        ]
    }


@router.get("/stats", response_model=Dict[str, Any])
async def get_stats(db: AsyncSession = Depends(get_db)):
    """آمار کلی بازیها - نسخه ساده و پایدار"""
    try:
        result = await db.execute(select(EducationalGame))
        all_games = result.scalars().all()

        total_games = len(all_games)
        total_plays = sum((g.play_count or 0) for g in all_games)

        return {"total_games": total_games, "total_plays": total_plays, "categories_count": 8}
    except Exception as e:
        print(f"Error in get_stats: {e}")
        return {"total_games": 0, "total_plays": 0, "categories_count": 8}


@router.get("/{game_id}", response_model=StatsResponse)
async def get_game_details(game_id: int, db: AsyncSession = Depends(get_db)):
    """جزئیات کامل یک بازی"""
    try:
        result = await db.execute(select(EducationalGame).where(EducationalGame.id == game_id))
        game = result.scalar_one_or_none()

        if not game:
            raise HTTPException(404, "بازی یافت نشد")

        game.play_count = (game.play_count or 0) + 1
        await db.commit()

        return {
            "game": {
                "id": game.id,
                "title": game.title,
                "title_en": game.title_en,
                "description": game.description,
                "category": game.category,
                "embed_url": game.embed_url,
                "thumbnail_url": game.thumbnail_url,
                "age_range": game.age_range,
                "duration_minutes": game.duration_minutes,
                "difficulty": game.difficulty,
                "educational_objectives": game.educational_objectives or [],
                "skills_developed": game.skills_developed or [],
                "play_count": game.play_count,
                "rating_average": game.rating_average,
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in get_game_details: {e}")
        raise HTTPException(500, str(e))


@router.post("/progress", response_model=Dict[str, Any])
async def update_progress(data: GameProgressUpdate, db: AsyncSession = Depends(get_db)):
    """ثبت پیشرفت کاربر در بازی"""
    try:
        result = await db.execute(
            select(GameProgress).where(
                (GameProgress.user_id == data.user_id) & (GameProgress.game_id == data.game_id)
            )
        )
        progress = result.scalar_one_or_none()

        if not progress:
            progress = GameProgress(user_id=data.user_id, game_id=data.game_id)
            db.add(progress)

        if data.completed is not None:
            progress.completed = data.completed
        if data.score is not None:
            progress.score = data.score
        if data.time_spent_minutes is not None:
            progress.time_spent_minutes = data.time_spent_minutes
        if data.reflections:
            progress.reflections = data.reflections

        await db.commit()

        return {"status": "success", "progress_id": progress.id}
    except Exception as e:
        print(f"Error in update_progress: {e}")
        return {"status": "error", "message": str(e)}
