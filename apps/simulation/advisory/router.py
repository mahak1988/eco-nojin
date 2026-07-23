"""
Advisory API Router — analysis + recommendations + scenarios for a simulator run.
"""
from typing import Any
from fastapi import APIRouter
from pydantic import BaseModel

from apps.simulation.advisory.engine import generate_advisory

router = APIRouter(prefix="/api/v1/simulation", tags=["🧠 Advisory"])


class AdvisoryRequest(BaseModel):
    simulator_id: str
    metrics: dict[str, Any] = {}
    parameters: dict[str, Any] = {}


@router.post("/advisory", summary="Generate analysis, recommendations & scenarios")
async def advisory(req: AdvisoryRequest):
    return generate_advisory(req.simulator_id, req.metrics, req.parameters)
