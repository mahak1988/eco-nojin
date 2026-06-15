"""Pilot Domain Models"""
from dataclasses import dataclass, field
from typing import List, Optional, Dict
from datetime import datetime, timezone
from enum import Enum


class PilotStatus(str, Enum):
    REGISTERED = "registered"
    SENSORS_DEPLOYED = "sensors_deployed"
    COMMUNITY_ONBOARDED = "community_onboarded"
    FIRST_DATA_RECEIVED = "first_data_received"
    FIRST_MRV_COMPLETED = "first_mrv_completed"
    FIRST_PES_PAID = "first_pes_paid"
    FULLY_OPERATIONAL = "fully_operational"


@dataclass
class IoTDeployment:
    deployment_id: str
    pilot_site: str
    sensor_type: str
    sensor_id: str
    location_lat: float
    location_lon: float
    installation_date: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    status: str = "active"
    first_reading_at: Optional[datetime] = None


@dataclass
class CommunityMember:
    member_id: str
    pilot_site: str
    name: str
    role: str
    gender: str
    age_group: str
    phone: Optional[str] = None
    wallet_address: Optional[str] = None
    registered_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    training_completed: bool = False


@dataclass
class MRVCycle:
    cycle_id: str
    pilot_site: str
    period_start: datetime
    period_end: datetime
    soc_change_tCO2: float = 0.0
    biomass_sequestration_tCO2: float = 0.0
    water_saved_m3: float = 0.0
    verified: bool = False
    verification_date: Optional[datetime] = None
    blockchain_tx_hash: Optional[str] = None


@dataclass
class PESPayment:
    payment_id: str
    pilot_site: str
    mrv_cycle_id: str
    beneficiary_id: str
    amount_usd: float
    currency: str = "USD"
    blockchain_tx_hash: Optional[str] = None
    paid_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    status: str = "pending"