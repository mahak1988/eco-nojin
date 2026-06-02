from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from api.core.database import get_db
from api.core.deps import require_write_auth
from api.modules.store import crud, schemas

router = APIRouter(tags=["Store"])


@router.get("/", response_model=schemas.StoreListResponse)
async def list_store(skip: int = 0, limit: int = 50, db: AsyncSession = Depends(get_db)):
    items, total = await crud.list_items(db, skip, limit)
    return schemas.StoreListResponse(items=items, total=total)


@router.get("/{item_id}", response_model=schemas.StoreItemResponse)
async def get_store(item_id: int, db: AsyncSession = Depends(get_db)):
    item = await crud.get_item(db, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item


@router.post("/", response_model=schemas.StoreItemResponse, status_code=status.HTTP_201_CREATED)
async def create_store(
    data: schemas.StoreItemCreate,
    db: AsyncSession = Depends(get_db),
    _user: str = Depends(require_write_auth),
):
    return await crud.create_item(db, data)


@router.put("/{item_id}", response_model=schemas.StoreItemResponse)
async def update_store(
    item_id: int,
    data: schemas.StoreItemUpdate,
    db: AsyncSession = Depends(get_db),
    _user: str = Depends(require_write_auth),
):
    item = await crud.update_item(db, item_id, data)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_store(
    item_id: int,
    db: AsyncSession = Depends(get_db),
    _user: str = Depends(require_write_auth),
):
    if not await crud.delete_item(db, item_id):
        raise HTTPException(status_code=404, detail="Item not found")
