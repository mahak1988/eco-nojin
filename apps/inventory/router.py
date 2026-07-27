"""Inventory API."""

from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, Query, status
from pydantic import BaseModel, Field
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from apps.inventory.models import InventoryItem
from apps.shared_core.database.session import get_db_session
from apps.shared_core.schemas.pagination import ListMeta, build_meta, page_to_offset

router = APIRouter(prefix="/api/v1/inventory", tags=["Inventory"])


class ItemIn(BaseModel):
    name: str = Field(..., min_length=1)
    category: str = Field(..., pattern="^(seed|fertilizer|pesticide|tool|other)$")
    sku: Optional[str] = None
    unit: str = "kg"
    quantity: float = 0
    min_stock: float = 0
    unit_cost: Optional[float] = None
    npk: Optional[str] = None
    active_ingredient: Optional[str] = None
    target_pest: Optional[str] = None
    farm_id: Optional[int] = None
    notes: Optional[str] = None


class ItemOut(ItemIn):
    id: int

    model_config = {"from_attributes": True}


class ItemList(BaseModel):
    data: list[ItemOut]
    meta: ListMeta


@router.get("/items", response_model=ItemList)
async def list_items(
    page: int = Query(1, ge=1),
    size: int = Query(50, ge=1, le=100),
    category: Optional[str] = None,
    session: AsyncSession = Depends(get_db_session),
):
    q = select(InventoryItem).where(InventoryItem.is_deleted.is_(False))
    cq = select(func.count()).select_from(InventoryItem).where(InventoryItem.is_deleted.is_(False))
    if category:
        q = q.where(InventoryItem.category == category)
        cq = cq.where(InventoryItem.category == category)
    total = int((await session.execute(cq)).scalar_one())
    rows = (
        await session.execute(q.order_by(InventoryItem.name).offset(page_to_offset(page, size)).limit(size))
    ).scalars().all()
    return ItemList(data=[ItemOut.model_validate(r) for r in rows], meta=build_meta(total, page, size))


@router.post("/items", response_model=ItemOut, status_code=status.HTTP_201_CREATED)
async def create_item(body: ItemIn, session: AsyncSession = Depends(get_db_session)):
    item = InventoryItem(**body.model_dump())
    session.add(item)
    await session.flush()
    await session.refresh(item)
    return ItemOut.model_validate(item)


@router.post("/seed-demo")
async def seed_inventory(session: AsyncSession = Depends(get_db_session)):
    count = int(
        (await session.execute(select(func.count()).select_from(InventoryItem).where(InventoryItem.is_deleted.is_(False)))).scalar_one()
    )
    if count > 0:
        return {"seeded": 0}
    demos = [
        ItemIn(name="Wheat seed (certified)", category="seed", quantity=500, unit="kg", min_stock=50, unit_cost=1.2),
        ItemIn(name="Urea 46%", category="fertilizer", quantity=1000, unit="kg", npk="46-0-0", unit_cost=0.4),
        ItemIn(name="NPK 20-20-20", category="fertilizer", quantity=400, unit="kg", npk="20-20-20", unit_cost=0.6),
        ItemIn(name="Imidacloprid 35% SC", category="pesticide", quantity=20, unit="L", active_ingredient="Imidacloprid", target_pest="Aphids"),
        ItemIn(name="Copper fungicide", category="pesticide", quantity=15, unit="kg", active_ingredient="Copper oxychloride", target_pest="Blight"),
        ItemIn(name="Drip tape 16mm", category="tool", quantity=2000, unit="m", unit_cost=0.15),
    ]
    for d in demos:
        session.add(InventoryItem(**d.model_dump()))
    await session.flush()
    return {"seeded": len(demos)}
