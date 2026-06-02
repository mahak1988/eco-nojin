from fastapi import APIRouter, Query, Body

router = APIRouter()

@router.get("/balance")
async def get_balance():
    return {"balance": 1250, "eco_coins": 1250, "currency": "ECO"}

@router.post("/mine")
async def mine(
    action_type: str = "green_action",
    amount: float = 10,
    location: str = "Iran",
    carbon_kg: float = 0,
    water_saved_liters: float = 0,
):
    from api.services.eco_miner import mine_natural_tokens

    result = mine_natural_tokens(
        action_type,
        amount,
        carbon_kg=carbon_kg,
        water_saved_liters=water_saved_liters,
        region=location.lower() if location else "global",
    )
    return {"success": True, "location": location, **result}

@router.get("/")
async def list_ecomining():
    return {"items": [], "total": 0, "module": "ecomining"}

@router.get("/{id}")
async def get_ecomining(id: str):
    return {"id": id, "name": "نمونه EcoCoin", "status": "active"}

@router.post("/")
async def create_ecomining(data: dict = Body(...)):
    return {"id": "new_123", "message": "با موفقیت ایجاد شد", **data}

@router.put("/{id}")
async def update_ecomining(id: str, data: dict = Body(...)):
    return {"id": id, "message": "با موفقیت به‌روز شد", **data}

@router.delete("/{id}")
async def delete_ecomining(id: str):
    return {"id": id, "message": "با موفقیت حذف شد"}
