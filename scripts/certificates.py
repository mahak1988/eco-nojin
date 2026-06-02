# -*- coding: utf-8 -*-
"""
Certificate Generator - تولید NFT گواهی فعالیت اکوسیستمی
هر فعالیت یک Living NFT منحصربه‌فرد دریافت می‌کند
"""

import json
import hashlib
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional
from datetime import datetime, timezone
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from scripts.core.logger import UnifiedLogger

logger = UnifiedLogger.get_logger(__name__)


@dataclass
class NFTMetadata:
    """متادیتای NFT بر اساس استاندارد ERC-721"""
    name: str
    description: str
    image: str  # IPFS URL
    animation_url: Optional[str] = None
    external_url: str = "https://econojin.com"
    
    # Gaia-specific attributes
    attributes: List[Dict] = field(default_factory=list)
    
    # Scientific data
    scientific_data: Dict = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "description": self.description,
            "image": self.image,
            "animation_url": self.animation_url,
            "external_url": self.external_url,
            "attributes": self.attributes,
            "scientific_data": self.scientific_data,
        }


@dataclass
class LivingCertificate:
    """گواهی زنده که با رشد فعالیت به‌روز می‌شود"""
    token_id: int
    owner: str
    activity_type: str
    species: Optional[str]
    planted_date: datetime
    location: Dict
    
    # Growth data (updated periodically)
    current_carbon_kg: float
    health_score: float  # 0-1
    last_update: datetime
    
    # Visual representation
    growth_stage: str  # seedling, young, mature, old
    image_version: int
    
    # Verification
    proof_id: str
    satellite_verified: bool
    iot_verified: bool
    community_verified: bool
    
    def to_metadata(self) -> NFTMetadata:
        """تبدیل به NFT metadata"""
        
        attributes = [
            {"trait_type": "Activity", "value": self.activity_type},
            {"trait_type": "Species", "value": self.species or "N/A"},
            {"trait_type": "Carbon Absorbed (kg)", "value": round(self.current_carbon_kg, 2)},
            {"trait_type": "Health Score", "value": f"{int(self.health_score * 100)}%"},
            {"trait_type": "Growth Stage", "value": self.growth_stage},
            {"trait_type": "Location", "value": self.location.get("region", "Unknown")},
            {"trait_type": "Satellite Verified", "value": self.satellite_verified},
            {"trait_type": "IoT Verified", "value": self.iot_verified},
            {"trait_type": "Planting Date", "value": self.planted_date.strftime("%Y-%m-%d")},
        ]
        
        scientific_data = {
            "proof_id": self.proof_id,
            "methodology": "IPCC + RothC + Econojin",
            "verification_sources": {
                "satellite": self.satellite_verified,
                "iot": self.iot_verified,
                "community": self.community_verified,
            },
            "last_updated": self.last_update.isoformat(),
        }
        
        return NFTMetadata(
            name=f"Gaia #{self.token_id} - {self.species or self.activity_type}",
            description=(
                f"Living NFT representing a real {self.activity_type} activity. "
                f"This NFT grows as the actual ecosystem grows. "
                f"Currently absorbing {self.current_carbon_kg:.2f} kg CO2."
            ),
            image=f"ipfs://gaia-nft/{self.token_id}/v{self.image_version}.png",
            attributes=attributes,
            scientific_data=scientific_data,
        )


class CertificateGenerator:
    """تولیدکننده گواهی‌های NFT"""
    
    GROWTH_STAGES = {
        "tree_planting": ["seedling", "sapling", "young", "mature", "old"],
        "soil_regeneration": ["initial", "improving", "healthy", "rich", "mature"],
        "mangrove_planting": ["propagule", "seedling", "young", "mature", "old"],
    }
    
    def __init__(self, ipfs_gateway: str = "https://ipfs.io/ipfs/"):
        self.ipfs_gateway = ipfs_gateway
        self.certificates: Dict[int, LivingCertificate] = {}
        self.next_token_id = 1
    
    def generate_certificate(
        self,
        owner: str,
        activity_type: str,
        location: Dict,
        carbon_kg: float,
        proof_id: str,
        species: Optional[str] = None,
        planted_date: Optional[datetime] = None,
    ) -> LivingCertificate:
        """ایجاد گواهی جدید"""
        
        token_id = self.next_token_id
        self.next_token_id += 1
        
        cert = LivingCertificate(
            token_id=token_id,
            owner=owner,
            activity_type=activity_type,
            species=species,
            planted_date=planted_date or datetime.now(timezone.utc),
            location=location,
            current_carbon_kg=carbon_kg,
            health_score=1.0,
            last_update=datetime.now(timezone.utc),
            growth_stage="seedling",
            image_version=1,
            proof_id=proof_id,
            satellite_verified=False,
            iot_verified=False,
            community_verified=False,
        )
        
        self.certificates[token_id] = cert
        logger.info(f"Certificate generated: #{token_id} for {owner}")
        
        return cert
    
    def update_certificate(
        self,
        token_id: int,
        new_carbon_kg: Optional[float] = None,
        health_score: Optional[float] = None,
        satellite_verified: Optional[bool] = None,
        iot_verified: Optional[bool] = None,
        community_verified: Optional[bool] = None,
    ) -> Optional[LivingCertificate]:
        """به‌روزرسانی گواهی (با رشد فعالیت واقعی)"""
        
        if token_id not in self.certificates:
            logger.warning(f"Certificate #{token_id} not found")
            return None
        
        cert = self.certificates[token_id]
        
        if new_carbon_kg is not None:
            cert.current_carbon_kg = new_carbon_kg
        
        if health_score is not None:
            cert.health_score = health_score
        
        if satellite_verified is not None:
            cert.satellite_verified = satellite_verified
        
        if iot_verified is not None:
            cert.iot_verified = iot_verified
        
        if community_verified is not None:
            cert.community_verified = community_verified
        
        # محاسبه growth stage بر اساس کربن
        cert.growth_stage = self._calculate_growth_stage(
            cert.activity_type,
            cert.current_carbon_kg
        )
        
        cert.last_update = datetime.now(timezone.utc)
        cert.image_version += 1  # تصویر جدید با رشد
        
        logger.info(
            f"Certificate #{token_id} updated: {cert.current_carbon_kg:.2f} kg, "
            f"stage: {cert.growth_stage}"
        )
        
        return cert
    
    def _calculate_growth_stage(self, activity_type: str, carbon_kg: float) -> str:
        """محاسبه مرحله رشد"""
        
        stages = self.GROWTH_STAGES.get(activity_type, self.GROWTH_STAGES["tree_planting"])
        
        # آستانه‌های کربن برای هر مرحله
        thresholds = [10, 50, 200, 500]  # kg CO2
        
        if carbon_kg < thresholds[0]:
            return stages[0]
        elif carbon_kg < thresholds[1]:
            return stages[1]
        elif carbon_kg < thresholds[2]:
            return stages[2]
        elif carbon_kg < thresholds[3]:
            return stages[3]
        else:
            return stages[4]
    
    def export_metadata(self, token_id: int) -> Optional[str]:
        """خروجی metadata به صورت JSON"""
        if token_id not in self.certificates:
            return None
        
        cert = self.certificates[token_id]
        metadata = cert.to_metadata()
        return json.dumps(metadata.to_dict(), indent=2, ensure_ascii=False)
    
    def get_certificate(self, token_id: int) -> Optional[LivingCertificate]:
        """دریافت گواهی"""
        return self.certificates.get(token_id)
    
    def list_certificates(self, owner: Optional[str] = None) -> List[LivingCertificate]:
        """لیست گواهی‌ها"""
        certs = list(self.certificates.values())
        if owner:
            certs = [c for c in certs if c.owner == owner]
        return certs
    
    def generate_portfolio_report(self, owner: str) -> Dict:
        """گزارش پورتفولیو NFT های یک کاربر"""
        
        user_certs = [c for c in self.certificates.values() if c.owner == owner]
        
        if not user_certs:
            return {"total_certificates": 0, "total_carbon_kg": 0}
        
        total_carbon = sum(c.current_carbon_kg for c in user_certs)
        avg_health = sum(c.health_score for c in user_certs) / len(user_certs)
        
        by_activity = {}
        for cert in user_certs:
            by_activity.setdefault(cert.activity_type, []).append(cert)
        
        return {
            "owner": owner,
            "total_certificates": len(user_certs),
            "total_carbon_kg": total_carbon,
            "total_carbon_tons": total_carbon / 1000,
            "average_health": avg_health,
            "by_activity": {
                k: {
                    "count": len(v),
                    "carbon_kg": sum(c.current_carbon_kg for c in v),
                }
                for k, v in by_activity.items()
            },
            "verified_count": sum(
                1 for c in user_certs 
                if c.satellite_verified or c.iot_verified
            ),
            "estimated_value_usd": (total_carbon / 1000) * 50,  # $50/ton
        }