from fastapi import APIRouter, Query, Body

router = APIRouter()

@router.get("/")
async def list_desktop():
    return {"items": [], "total": 0, "module": "desktop"}

@router.get("/{id}")
async def get_desktop(id: str):
    return {"id": id, "name": "نمونه میزکار", "status": "active"}

@router.post("/")
async def create_desktop(data: dict = Body(...)):
    return {"id": "new_123", "message": "با موفقیت ایجاد شد", **data}

@router.put("/{id}")
async def update_desktop(id: str, data: dict = Body(...)):
    return {"id": id, "message": "با موفقیت به‌روز شد", **data}

@router.delete("/{id}")
async def delete_desktop(id: str):
    return {"id": id, "message": "با موفقیت حذف شد"}
