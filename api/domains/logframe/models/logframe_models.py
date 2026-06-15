"""LogFrame Domain Models - Aligned with GCF/GEF IRMF"""
from dataclasses import dataclass, field
from typing import List, Optional, Dict
from datetime import datetime, timezone
from enum import Enum


class LogFrameLevel(str, Enum):
    IMPACT = "impact"
    OUTCOME = "outcome"
    OUTPUT = "output"
    ACTIVITY = "activity"


class SDGTarget(str, Enum):
    SDG_2 = "SDG2_ZeroHunger"
    SDG_6 = "SDG6_CleanWater"
    SDG_8 = "SDG8_DecentWork"
    SDG_13 = "SDG13_ClimateAction"
    SDG_15 = "SDG15_LifeOnLand"


@dataclass
class Indicator:
    indicator_id: str
    name: str
    name_en: str
    level: LogFrameLevel
    sdg_targets: List[SDGTarget]
    baseline_value: float
    target_value: float
    unit: str
    frequency: str
    data_source: str
    methodology: str
    gef_core: bool = False
    gcf_core: bool = False
    ndc_aligned: bool = False
    current_value: Optional[float] = None
    progress_percent: Optional[float] = None


@dataclass
class LogFrameEntry:
    entry_id: str
    level: LogFrameLevel
    statement: str
    statement_en: str
    indicators: List[Indicator] = field(default_factory=list)
    assumptions: List[str] = field(default_factory=list)
    risks: List[str] = field(default_factory=list)
    responsible_entity: str = ""
    pilot_sites: List[str] = field(default_factory=list)


@dataclass
class NDCContribution:
    contribution_id: str
    project_id: str
    sector: str
    mitigation_tCO2e: float
    adaptation_beneficiaries: int
    reporting_period: str
    methodology: str = "IPCC AFOLU Tier 2"
    verified: bool = False
    submitted_to_unfccc: bool = False
