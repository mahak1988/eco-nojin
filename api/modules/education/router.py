from api.core.schemas import SuccessResponse, IDResponse, StatsResponse, PaginatedResponse
from typing import Dict, Any
from fastapi import APIRouter, Body, Query

router = APIRouter()


@router.get("/", response_model=Dict[str, Any])
async def list_education():
    return {"items": [], "total": 0, "module": "education"}


@router.get("/{id}", response_model=Dict[str, Any])
async def get_education(id: str):
    return {"id": id, "name": "نمونه آموزش", "status": "active"}


@router.post("/", response_model=Dict[str, Any])
async def create_education(data: dict = Body(...)):
    return {"id": "new_123", "message": "با موفقیت ایجاد شد", **data}


@router.put("/{id}", response_model=IDResponse)
async def update_education(id: str, data: dict = Body(...)):
    return {"id": id, "message": "با موفقیت به‌روز شد", **data}


@router.delete("/{id}", response_model=SuccessResponse)
async def delete_education(id: str):
    return {"id": id, "message": "با موفقیت حذف شد"}
