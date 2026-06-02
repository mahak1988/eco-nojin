from fastapi import APIRouter, Query, Body

router = APIRouter()

@router.get("/")
async def list_games():
    return {"items": [], "total": 0, "module": "games"}

@router.get("/{id}")
async def get_games(id: str):
    return {"id": id, "name": "نمونه بازی", "status": "active"}

@router.post("/")
async def create_games(data: dict = Body(...)):
    return {"id": "new_123", "message": "با موفقیت ایجاد شد", **data}

@router.put("/{id}")
async def update_games(id: str, data: dict = Body(...)):
    return {"id": id, "message": "با موفقیت به‌روز شد", **data}

@router.delete("/{id}")
async def delete_games(id: str):
    return {"id": id, "message": "با موفقیت حذف شد"}
