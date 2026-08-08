"""Inventory API + analytics + RBAC."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from apps.inventory.models import InventoryItem
from apps.shared_core.database.session import get_db_session
from apps.shared_core.rbac import require_permission
from apps.shared_core.schemas.pagination import ListMeta, build_meta, page_to_offset

router = APIRouter(prefix="/api/v1/inventory", tags=["Inventory"])


class ItemIn(BaseModel):
    name: str = Field(..., min_length=1)
    category: str = Field(..., pattern="^(seed|fertilizer|pesticide|tool|other)$")
    sku: str | None = None
    unit: str = "kg"
    quantity: float = 0
    min_stock: float = 0
    unit_cost: float | None = None
    npk: str | None = None
    active_ingredient: str | None = None
    target_pest: str | None = None
    farm_id: int | None = None
    notes: str | None = None


class ItemOut(ItemIn):
    id: int

    model_config = {"from_attributes": True}


class ItemList(BaseModel):
    data: list[ItemOut]
    meta: ListMeta


@router.get("/items", response_model=ItemList)
@router.get("/resources", response_model=ItemList)
async def list_items(
    page: int = Query(1, ge=1),
    size: int = Query(50, ge=1, le=100),
    category: str | None = None,
    session: AsyncSession = Depends(get_db_session),
):
    q = select(InventoryItem).where(InventoryItem.is_deleted.is_(False))
    cq = select(func.count()).select_from(InventoryItem).where(InventoryItem.is_deleted.is_(False))
    if category:
        q = q.where(InventoryItem.category == category)
        cq = cq.where(InventoryItem.category == category)
    total = int((await session.execute(cq)).scalar_one())
    rows = (
        (
            await session.execute(
                q.order_by(InventoryItem.name).offset(page_to_offset(page, size)).limit(size)
            )
        )
        .scalars()
        .all()
    )
    return ItemList(
        data=[ItemOut.model_validate(r) for r in rows], meta=build_meta(total, page, size)
    )


@router.get("/usage-analytics")
async def usage_analytics(session: AsyncSession = Depends(get_db_session)):
    rows = (
        (await session.execute(select(InventoryItem).where(InventoryItem.is_deleted.is_(False))))
        .scalars()
        .all()
    )
    by_cat: dict[str, float] = {}
    value = 0.0
    low = []
    for r in rows:
        by_cat[r.category] = by_cat.get(r.category, 0) + float(r.quantity or 0)
        if r.unit_cost:
            value += float(r.quantity or 0) * float(r.unit_cost)
        if (r.quantity or 0) <= (r.min_stock or 0):
            low.append(
                {"id": r.id, "name": r.name, "quantity": r.quantity, "min_stock": r.min_stock}
            )
    return {
        "by_category_qty": by_cat,
        "stock_value_estimate": round(value, 2),
        "reorder_candidates": low,
        "item_count": len(rows),
    }


@router.get("/cost-report")
async def cost_report(session: AsyncSession = Depends(get_db_session)):
    rows = (
        (await session.execute(select(InventoryItem).where(InventoryItem.is_deleted.is_(False))))
        .scalars()
        .all()
    )
    lines = []
    total = 0.0
    for r in rows:
        line = float(r.quantity or 0) * float(r.unit_cost or 0)
        total += line
        lines.append(
            {
                "id": r.id,
                "name": r.name,
                "category": r.category,
                "quantity": r.quantity,
                "unit_cost": r.unit_cost,
                "line_value": round(line, 2),
            }
        )
    return {"lines": lines, "total_value": round(total, 2)}


@router.post("/reorder-alert")
async def reorder_alert(
    item_id: int = Query(...),
    min_stock: float = Query(..., ge=0),
    session: AsyncSession = Depends(get_db_session),
    _: object = Depends(require_permission("inventory:write")),
):
    r = (
        await session.execute(
            select(InventoryItem).where(
                InventoryItem.id == item_id, InventoryItem.is_deleted.is_(False)
            )
        )
    ).scalar_one_or_none()
    if not r:
        raise HTTPException(404, "Item not found")
    r.min_stock = min_stock
    await session.flush()
    return {"id": r.id, "min_stock": r.min_stock, "needs_reorder": (r.quantity or 0) <= min_stock}


@router.post("/items", response_model=ItemOut, status_code=status.HTTP_201_CREATED)
async def create_item(
    body: ItemIn,
    session: AsyncSession = Depends(get_db_session),
    _: object = Depends(require_permission("inventory:write")),
):
    item = InventoryItem(**body.model_dump())
    session.add(item)
    await session.flush()
    await session.refresh(item)
    return ItemOut.model_validate(item)


@router.post("/seed-demo")
async def seed_inventory(
    session: AsyncSession = Depends(get_db_session),
    _: object = Depends(require_permission("inventory:write")),
):
    count = int(
        (
            await session.execute(
                select(func.count())
                .select_from(InventoryItem)
                .where(InventoryItem.is_deleted.is_(False))
            )
        ).scalar_one()
    )
    if count > 0:
        return {"seeded": 0}
    demos = [
        ItemIn(
            name="Wheat seed (certified)",
            category="seed",
            quantity=500,
            unit="kg",
            min_stock=50,
            unit_cost=1.2,
        ),
        ItemIn(
            name="Urea 46%",
            category="fertilizer",
            quantity=1000,
            unit="kg",
            npk="46-0-0",
            unit_cost=0.4,
        ),
        ItemIn(
            name="NPK 20-20-20",
            category="fertilizer",
            quantity=400,
            unit="kg",
            npk="20-20-20",
            unit_cost=0.6,
        ),
        ItemIn(
            name="Imidacloprid 35% SC",
            category="pesticide",
            quantity=20,
            unit="L",
            active_ingredient="Imidacloprid",
            target_pest="Aphids",
        ),
        ItemIn(
            name="Copper fungicide",
            category="pesticide",
            quantity=15,
            unit="kg",
            active_ingredient="Copper oxychloride",
            target_pest="Blight",
        ),
        ItemIn(name="Drip tape 16mm", category="tool", quantity=2000, unit="m", unit_cost=0.15),
    ]
    for d in demos:
        session.add(InventoryItem(**d.model_dump()))
    await session.flush()
    return {"seeded": len(demos)}
