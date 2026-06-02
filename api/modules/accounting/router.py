from fastapi import APIRouter

router = APIRouter()

@router.get("/summary")
async def get_summary():
    return {
        "total_income": 112400000,
        "total_expense": 48700000,
        "net_profit": 63700000,
        "currency": "IRR",
        "period": "1403/01-03"
    }

@router.get("/transactions")
async def get_transactions(limit: int = 10):
    return {
        "transactions": [
            {"id": i, "type": "income" if i % 2 == 0 else "expense", "amount": 1000000 * (i + 1), "date": f"1403/03/{i+1:02d}"}
            for i in range(limit)
        ]
    }
