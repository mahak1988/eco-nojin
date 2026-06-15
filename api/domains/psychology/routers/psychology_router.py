"""Psychology Domain Router."""
from fastapi import APIRouter, Depends
from .schemas.psychology_schemas import TestSubmission, TestResultResponse
from .services.psychology_service import PsychologyService
from .repositories.psychology_repository import PsychologyRepository


router = APIRouter(prefix="/psychology", tags=["Psychology"])


def get_psychology_service() -> PsychologyService:
    repo = PsychologyRepository()
    return PsychologyService(repo)


@router.post("/submit")
async def submit_test(
    submission: TestSubmission,
    service: PsychologyService = Depends(get_psychology_service)
):
    """ثبت و تحلیل تست روانشناختی"""
    return await service.submit_test(
        submission.user_id,
        submission.test_id,
        submission.answers
    )
