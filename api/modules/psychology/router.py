from fastapi import APIRouter, Query, Body

router = APIRouter()

@router.get("/")
async def list_psychology():
    return {"items": [], "total": 0, "module": "psychology"}

@router.get("/{id}")
async def get_psychology(id: str):
    return {"id": id, "name": "نمونه روانشناسی", "status": "active"}

@router.post("/")
async def create_psychology(data: dict = Body(...)):
    return {"id": "new_123", "message": "با موفقیت ایجاد شد", **data}

@router.put("/{id}")
async def update_psychology(id: str, data: dict = Body(...)):
    return {"id": id, "message": "با موفقیت به‌روز شد", **data}

@router.delete("/{id}")
async def delete_psychology(id: str):
    return {"id": id, "message": "با موفقیت حذف شد"}
