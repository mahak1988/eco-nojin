from fastapi import APIRouter, Query, Body

router = APIRouter()

@router.get("/")
async def list_community():
    return {"items": [], "total": 0, "module": "community"}

@router.get("/{id}")
async def get_community(id: str):
    return {"id": id, "name": "نمونه جامعه", "status": "active"}

@router.post("/")
async def create_community(data: dict = Body(...)):
    return {"id": "new_123", "message": "با موفقیت ایجاد شد", **data}

@router.put("/{id}")
async def update_community(id: str, data: dict = Body(...)):
    return {"id": id, "message": "با موفقیت به‌روز شد", **data}

@router.delete("/{id}")
async def delete_community(id: str):
    return {"id": id, "message": "با موفقیت حذف شد"}
