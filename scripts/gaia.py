# -*- coding: utf-8 -*-
"""
Gaia API Router - REST endpoints برای اتصال به Gaia Protocol
"""

import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional

from fastapi import APIRouter, BackgroundTasks, HTTPException, status
from pydantic import BaseModel, Field

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from core.gaia.calculator import ActivityType, CarbonCalculator, ClimateData, Location, TreeSpecies
from core.gaia.certificates import CertificateGenerator
from core.gaia.oracle import GaiaOracle
from core.gaia.verification import ScientificVerifier

from scripts.core.logger import UnifiedLogger

logger = UnifiedLogger.get_logger(__name__)

router = APIRouter(
    prefix="/gaia", tags=["Gaia Protocol"], responses={404: {"description": "Not found"}}
)

# نمونه‌های سراسری
calculator = CarbonCalculator()
oracle = GaiaOracle()  # در production با پارامترهای واقعی
cert_gen = CertificateGenerator()
verifier = ScientificVerifier()


# ============================================================================
# Pydantic Models
# ============================================================================


class CalculateCarbonRequest(BaseModel):
    """درخواست محاسبه کربن"""

    activity_type: str = Field(..., example="tree_planting")
    latitude: float = Field(..., example=35.6892)
    longitude: float = Field(..., example=51.3890)
    area_hectares: float = Field(1.0, ge=0.01)
    tree_count: Optional[int] = None
    species: str = Field("quercus_persica", example="quercus_persica")
    annual_rainfall_mm: float = Field(400, ge=0)
    avg_temperature_c: float = Field(18, ge=-50, le=60)
    duration_years: int = Field(10, ge=1, le=100)


class CarbonResultResponse(BaseModel):
    """پاسخ محاسبه کربن"""

    activity_type: str
    carbon_absorbed_kg: float
    carbon_absorbed_tons: float
    annual_sequestration_rate: float
    projection_10y_tons: float
    projection_50y_tons: float
    confidence: float
    methodology: str
    seed_tokens_earned: float
    estimated_gaia_value_usd: float


class RegisterActivityRequest(BaseModel):
    """ثبت فعالیت اکوسیستمی"""

    miner_address: str = Field(..., example="0x1234...abcd")
    activity_type: str
    latitude: float
    longitude: float
    area_hectares: float
    species: Optional[str] = None
    evidence_data: Dict = Field(default_factory=dict)


class RegisterActivityResponse(BaseModel):
    """پاسخ ثبت فعالیت"""

    success: bool
    proof_id: str
    carbon_kg: float
    seed_tokens: float
    certificate_token_id: int
    tx_hash: Optional[str] = None
    verified: bool
    confidence: float


class CertificateResponse(BaseModel):
    """پاسخ گواهی"""

    token_id: int
    owner: str
    activity_type: str
    species: Optional[str]
    carbon_kg: float
    health_score: float
    growth_stage: str
    verified_sources: List[str]
    metadata: Dict


class PortfolioResponse(BaseModel):
    """پاسخ پورتفولیو"""

    owner: str
    total_certificates: int
    total_carbon_kg: float
    total_carbon_tons: float
    estimated_value_usd: float
    certificates: List[CertificateResponse]


# ============================================================================
# Endpoints
# ============================================================================


@router.post("/calculate", response_model=CarbonResultResponse)
async def calculate_carbon(request: CalculateCarbonRequest):
    """
    محاسبه کربن جذب شده برای یک فعالیت اکوسیستمی

    از مدل‌های علمی RothC، AquaCrop و IPCC استفاده می‌کند
    """
    try:
        location = Location(
            latitude=request.latitude,
            longitude=request.longitude,
        )

        climate = ClimateData(
            annual_rainfall_mm=request.annual_rainfall_mm,
            avg_temperature_c=request.avg_temperature_c,
            min_temperature_c=request.avg_temperature_c - 10,
            max_temperature_c=request.avg_temperature_c + 10,
        )

        try:
            activity = ActivityType(request.activity_type)
        except ValueError:
            raise HTTPException(400, f"Invalid activity type: {request.activity_type}")

        try:
            species = TreeSpecies(request.species)
        except ValueError:
            species = TreeSpecies.OAK_PERSIAN

        result = calculator.calculate(
            activity_type=activity,
            location=location,
            climate=climate,
            area_hectares=request.area_hectares,
            tree_count=request.tree_count,
            species=species,
            duration_years=request.duration_years,
        )

        return CarbonResultResponse(
            activity_type=result.activity_type.value,
            carbon_absorbed_kg=result.carbon_absorbed_kg,
            carbon_absorbed_tons=result.carbon_absorbed_tons,
            annual_sequestration_rate=result.annual_sequestration_rate,
            projection_10y_tons=result.projection_10y_tons,
            projection_50y_tons=result.projection_50y_tons,
            confidence=result.confidence,
            methodology=result.methodology,
            seed_tokens_earned=result.to_seed_tokens(),
            estimated_gaia_value_usd=result.to_gaia_value(),
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Calculation failed: {e}")
        raise HTTPException(500, f"Calculation failed: {e}")


@router.post("/register-activity", response_model=RegisterActivityResponse)
async def register_activity(request: RegisterActivityRequest, background_tasks: BackgroundTasks):
    """
    ثبت یک فعالیت اکوسیستمی واقعی

    شامل:
    1. محاسبه علمی کربن
    2. اعتبارسنجی چندلایه
    3. ایجاد Proof برای blockchain
    4. تولید NFT certificate
    """
    try:
        # 1) محاسبه کربن
        location_dict = {
            "lat": request.latitude,
            "lng": request.longitude,
        }
        location = Location(request.latitude, request.longitude)
        climate = ClimateData(400, 18, 8, 28)

        try:
            activity = ActivityType(request.activity_type)
        except ValueError:
            raise HTTPException(400, f"Invalid activity: {request.activity_type}")

        carbon_result = calculator.calculate(
            activity_type=activity,
            location=location,
            climate=climate,
            area_hectares=request.area_hectares,
        )

        # 2) اعتبارسنجی
        verification = await verifier.verify_activity(
            activity_type=request.activity_type,
            location=location_dict,
            claimed_carbon_kg=carbon_result.carbon_absorbed_kg,
            evidence_data=request.evidence_data,
        )

        if not verification.verified:
            raise HTTPException(
                400, f"Activity not verified. Confidence: {verification.confidence:.2f}"
            )

        # 3) ایجاد Proof
        proof = oracle.create_proof(
            miner_address=request.miner_address,
            activity_type=request.activity_type,
            location=location_dict,
            carbon_kg=carbon_result.carbon_absorbed_kg,
            confidence=verification.confidence,
            methodology=carbon_result.methodology,
            evidence_data={
                "carbon_result": {
                    "kg": carbon_result.carbon_absorbed_kg,
                    "methodology": carbon_result.methodology,
                },
                "verification": {
                    "sources": verification.sources,
                    "evidence": verification.evidence,
                },
                "user_evidence": request.evidence_data,
            },
        )

        # 4) امضای Proof
        oracle.sign_proof(proof)

        # 5) ارسال به blockchain (در background)
        background_tasks.add_task(oracle.submit_to_blockchain, proof)

        # 6) تولید NFT Certificate
        cert = cert_gen.generate_certificate(
            owner=request.miner_address,
            activity_type=request.activity_type,
            location=location_dict,
            carbon_kg=carbon_result.carbon_absorbed_kg,
            proof_id=proof.proof_id,
            species=request.species,
        )

        return RegisterActivityResponse(
            success=True,
            proof_id=proof.proof_id,
            carbon_kg=carbon_result.carbon_absorbed_kg,
            seed_tokens=carbon_result.to_seed_tokens(),
            certificate_token_id=cert.token_id,
            tx_hash=None,  # در background پر می‌شود
            verified=verification.verified,
            confidence=verification.confidence,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Registration failed: {e}")
        raise HTTPException(500, f"Registration failed: {e}")


@router.get("/certificate/{token_id}", response_model=CertificateResponse)
async def get_certificate(token_id: int):
    """دریافت اطلاعات یک گواهی NFT"""
    cert = cert_gen.get_certificate(token_id)
    if not cert:
        raise HTTPException(404, f"Certificate #{token_id} not found")

    verified_sources = []
    if cert.satellite_verified:
        verified_sources.append("satellite")
    if cert.iot_verified:
        verified_sources.append("iot")
    if cert.community_verified:
        verified_sources.append("community")

    return CertificateResponse(
        token_id=cert.token_id,
        owner=cert.owner,
        activity_type=cert.activity_type,
        species=cert.species,
        carbon_kg=cert.current_carbon_kg,
        health_score=cert.health_score,
        growth_stage=cert.growth_stage,
        verified_sources=verified_sources,
        metadata=cert.to_metadata().to_dict(),
    )


@router.get("/portfolio/{owner_address}", response_model=PortfolioResponse)
async def get_portfolio(owner_address: str):
    """دریافت پورتفولیو NFT های یک کاربر"""
    certs = cert_gen.list_certificates(owner=owner_address)

    if not certs:
        return PortfolioResponse(
            owner=owner_address,
            total_certificates=0,
            total_carbon_kg=0,
            total_carbon_tons=0,
            estimated_value_usd=0,
            certificates=[],
        )

    total_carbon = sum(c.current_carbon_kg for c in certs)

    cert_responses = []
    for cert in certs:
        verified_sources = []
        if cert.satellite_verified:
            verified_sources.append("satellite")
        if cert.iot_verified:
            verified_sources.append("iot")
        if cert.community_verified:
            verified_sources.append("community")

        cert_responses.append(
            CertificateResponse(
                token_id=cert.token_id,
                owner=cert.owner,
                activity_type=cert.activity_type,
                species=cert.species,
                carbon_kg=cert.current_carbon_kg,
                health_score=cert.health_score,
                growth_stage=cert.growth_stage,
                verified_sources=verified_sources,
                metadata=cert.to_metadata().to_dict(),
            )
        )

    return PortfolioResponse(
        owner=owner_address,
        total_certificates=len(certs),
        total_carbon_kg=total_carbon,
        total_carbon_tons=total_carbon / 1000,
        estimated_value_usd=(total_carbon / 1000) * 50,
        certificates=cert_responses,
    )


@router.get("/stats")
async def get_global_stats():
    """آمار کلی پلتفرم Gaia"""
    all_certs = cert_gen.list_certificates()

    total_carbon = sum(c.current_carbon_kg for c in all_certs)

    by_activity = {}
    for cert in all_certs:
        by_activity.setdefault(
            cert.activity_type,
            {
                "count": 0,
                "carbon_kg": 0,
            },
        )
        by_activity[cert.activity_type]["count"] += 1
        by_activity[cert.activity_type]["carbon_kg"] += cert.current_carbon_kg

    return {
        "total_activities": len(all_certs),
        "total_carbon_kg": total_carbon,
        "total_carbon_tons": total_carbon / 1000,
        "equivalent_trees": int(total_carbon / 22),  # 22 kg/tree/year
        "estimated_value_usd": (total_carbon / 1000) * 50,
        "by_activity": by_activity,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
