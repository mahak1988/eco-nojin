from fastapi import APIRouter, Query, Body

router = APIRouter()

@router.get("/")
async def list_education():
    return {"items": [], "total": 0, "module": "education"}

@router.get("/{id}")
async def get_education(id: str):
    return {"id": id, "name": "نمونه آموزش", "status": "active"}

@router.post("/")
async def create_education(data: dict = Body(...)):
    return {"id": "new_123", "message": "با موفقیت ایجاد شد", **data}

@router.put("/{id}")
async def update_education(id: str, data: dict = Body(...)):
    return {"id": id, "message": "با موفقیت به‌روز شد", **data}

@router.delete("/{id}")
async def delete_education(id: str):
    return {"id": id, "message": "با موفقیت حذف شد"}
