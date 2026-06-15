"""Training API Router"""
from fastapi import APIRouter
from .services.training_service import TrainingService


router = APIRouter(prefix="/training", tags=["Training"])


def get_training_service() -> TrainingService:
    return TrainingService()


@router.get("/modules")
async def get_all_modules(service: TrainingService = get_training_service()):
    return {"modules": service.modules, "count": len(service.modules)}


@router.get("/modules/pilot/{pilot_site}")
async def get_modules_by_pilot(pilot_site: str, service: TrainingService = get_training_service()):
    modules = service.get_modules_by_pilot(pilot_site)
    return {"pilot_site": pilot_site, "modules": modules, "count": len(modules)}
