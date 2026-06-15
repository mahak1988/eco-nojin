"""Financial Domain Router."""
from fastapi import APIRouter, Depends
from .schemas.financial_schemas import (
    ProjectBudgetRequest,
    EconomicIndicatorResponse
)
from .services.financial_service import FinancialService
from .repositories.financial_repository import FinancialRepository


router = APIRouter(prefix="/financial", tags=["Financial"])


def get_financial_service() -> FinancialService:
    repo = FinancialRepository()
    return FinancialService(repo)


@router.post("/budget")
async def create_budget(
    request: ProjectBudgetRequest,
    service: FinancialService = Depends(get_financial_service)
):
    """ایجاد بودجه پروژه"""
    return {"status": "created", "project_id": request.project_id}


@router.get("/evaluate/{project_id}")
async def evaluate_project(
    project_id: str,
    service: FinancialService = Depends(get_financial_service)
):
    """ارزیابی اقتصادی پروژه"""
    return await service.evaluate_project(project_id)
