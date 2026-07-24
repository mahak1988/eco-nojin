"""
Verification and Carbon Credit Calculation for RothC Model
===========================================================
Implements verification methodologies for VERRA, Gold Standard, and Plan Vivo.
"""

import logging
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)


class VerificationStandard(Enum):
    """Supported carbon credit verification standards."""
    VERRA = "VERRA"
    GOLD_STANDARD = "GOLD_STANDARD"
    PLAN_VIVO = "PLAN_VIVO"
    AMERICA_CARBON = "AMERICA_CARBON"


@dataclass
class VerificationResult:
    """Results from carbon credit verification."""
    
    standard: str
    verified: bool
    verification_date: datetime
    
    # Carbon metrics
    total_sequestration_tc: float
    co2e_sequestered_tco2: float
    eligible_credits_tco2: float
    
    # Quality factors
    permanence_score: float  # 0-1
    additionality_score: float  # 0-1
    leakage_factor: float  # 0-1
    
    # Financial
    estimated_credit_value_usd: float
    price_per_credit_usd: float
    
    # Metadata
    methodology_version: str
    validation_notes: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "standard": self.standard,
            "verified": self.verified,
            "verification_date": self.verification_date.isoformat(),
            "carbon_metrics": {
                "total_sequestration_tc": self.total_sequestration_tc,
                "co2e_sequestered_tco2": self.co2e_sequestered_tco2,
                "eligible_credits_tco2": self.eligible_credits_tco2
            },
            "quality_scores": {
                "permanence": self.permanence_score,
                "additionality": self.additionality_score,
                "leakage_factor": self.leakage_factor
            },
            "financial": {
                "estimated_value_usd": self.estimated_credit_value_usd,
                "price_per_credit_usd": self.price_per_credit_usd
            },
            "methodology": self.methodology_version,
            "notes": self.validation_notes
        }


class BaseVerifier:
    """Base class for carbon credit verifiers."""
    
    def __init__(self, standard: VerificationStandard):
        self.standard = standard
        logger.info(f"{standard.value} verifier initialized")
    
    def calculate_permanence_score(
        self,
        simulation_years: int,
        soc_trend: List[float]
    ) -> float:
        """
        Calculate permanence score based on sequestration stability.
        
        Args:
            simulation_years: Length of simulation
            soc_trend: Time series of SOC values
            
        Returns:
            Permanence score (0-1)
        """
        if len(soc_trend) < 2:
            return 0.5
        
        # Check if SOC is consistently increasing or stable
        increases = sum(1 for i in range(1, len(soc_trend)) 
                       if soc_trend[i] >= soc_trend[i-1])
        
        increase_ratio = increases / (len(soc_trend) - 1)
        
        # Longer simulations get higher scores
        year_factor = min(simulation_years / 30.0, 1.0)
        
        permanence = increase_ratio * 0.7 + year_factor * 0.3
        
        return min(max(permanence, 0.0), 1.0)
    
    def calculate_additionality_score(
        self,
        baseline_soc: float,
        project_soc: float,
        management_intensity: str
    ) -> float:
        """
        Calculate additionality (is this beyond business-as-usual?).
        
        Args:
            baseline_soc: SOC under baseline scenario
            project_soc: SOC under project scenario
            management_intensity: low, medium, high
            
        Returns:
            Additionality score (0-1)
        """
        # Calculate improvement over baseline
        if baseline_soc > 0:
            improvement_ratio = (project_soc - baseline_soc) / baseline_soc
        else:
            improvement_ratio = 0.5
        
        # Management intensity factor
        intensity_factors = {
            "low": 0.6,
            "medium": 0.8,
            "high": 1.0
        }
        intensity_factor = intensity_factors.get(management_intensity, 0.8)
        
        additionality = min(improvement_ratio * 2.0, 1.0) * intensity_factor
        
        return min(max(additionality, 0.0), 1.0)
    
    def calculate_leakage_factor(
        self,
        project_area_ha: float,
        buffer_area_ha: float,
        displacement_risk: str
    ) -> float:
        """
        Calculate leakage (emissions displaced elsewhere).
        
        Args:
            project_area_ha: Project area
            buffer_area_ha: Buffer zone area
            displacement_risk: low, medium, high
            
        Returns:
            Leakage factor (0-1, lower is better)
        """
        # Buffer ratio reduces leakage
        if project_area_ha > 0:
            buffer_ratio = buffer_area_ha / project_area_ha
        else:
            buffer_ratio = 0
        
        buffer_factor = min(buffer_ratio, 0.2)  # Cap at 20% reduction
        
        # Displacement risk
        risk_factors = {
            "low": 0.05,
            "medium": 0.10,
            "high": 0.20
        }
        base_leakage = risk_factors.get(displacement_risk, 0.10)
        
        leakage = max(base_leakage - buffer_factor, 0.02)
        
        return leakage
    
    def verify(
        self,
        soc_change: float,
        simulation_years: int,
        soc_time_series: List[float],
        **kwargs
    ) -> VerificationResult:
        """
        Perform full verification.
        
        Must be implemented by subclasses.
        """
        raise NotImplementedError


class VerraVerifier(BaseVerifier):
    """
    VERRA (Verified Carbon Standard) verifier.
    
    Implements VM0042 Methodology for Soil Carbon Sequestration.
    """
    
    METHODOLOGY_VERSION = "VM0042 v1.0"
    
    def __init__(self):
        super().__init__(VerificationStandard.VERRA)
    
    def verify(
        self,
        soc_change: float,
        simulation_years: int,
        soc_time_series: List[float],
        baseline_soc: Optional[float] = None,
        project_area_ha: float = 100.0,
        buffer_area_ha: float = 15.0,
        management_intensity: str = "medium",
        displacement_risk: str = "medium",
        carbon_price_usd: float = 15.0
    ) -> VerificationResult:
        """
        Verify carbon credits under VERRA standard.
        
        Args:
            soc_change: Total SOC change (tC/ha)
            simulation_years: Simulation duration
            soc_time_series: Annual SOC values
            baseline_soc: Baseline SOC for additionality
            project_area_ha: Project area
            buffer_area_ha: Buffer zone
            management_intensity: Management level
            displacement_risk: Risk of activity displacement
            carbon_price_usd: Price per tCO2 credit
            
        Returns:
            Verification result
        """
        logger.info("Running VERRA verification")
        
        # Convert C to CO2e (1 tC = 3.67 tCO2)
        total_sequestration_tc = soc_change * project_area_ha
        co2e_sequestered = total_sequestration_tc * 3.67
        
        # Calculate quality scores
        permanence = self.calculate_permanence_score(
            simulation_years, soc_time_series
        )
        
        baseline = baseline_soc or soc_time_series[0] * 0.9  # Default baseline
        additionality = self.calculate_additionality_score(
            baseline, soc_time_series[-1], management_intensity
        )
        
        leakage = self.calculate_leakage_factor(
            project_area_ha, buffer_area_ha, displacement_risk
        )
        
        # Apply discounts
        discount_factor = permanence * additionality * (1 - leakage)
        eligible_credits = co2e_sequestered * discount_factor
        
        # VERRA-specific adjustments
        # Conservative approach: use lower bound of confidence interval
        conservative_factor = 0.85  # 15% buffer pool contribution
        eligible_credits *= conservative_factor
        
        # Estimated value
        estimated_value = eligible_credits * carbon_price_usd
        
        # Verification decision
        verified = (
            permanence > 0.5 and
            additionality > 0.3 and
            simulation_years >= 10
        )
        
        notes = []
        if permanence < 0.7:
            notes.append("Permanence could be improved with longer commitment")
        if additionality < 0.5:
            notes.append("Additionality marginal - document baseline carefully")
        if leakage > 0.1:
            notes.append("Consider expanding buffer zones")
        
        result = VerificationResult(
            standard=self.standard.value,
            verified=verified,
            verification_date=datetime.now(),
            total_sequestration_tc=total_sequestration_tc,
            co2e_sequestered_tco2=co2e_sequestered,
            eligible_credits_tco2=eligible_credits,
            permanence_score=permanence,
            additionality_score=additionality,
            leakage_factor=leakage,
            estimated_credit_value_usd=estimated_value,
            price_per_credit_usd=carbon_price_usd,
            methodology_version=self.METHODOLOGY_VERSION,
            validation_notes="; ".join(notes) if notes else "All criteria met"
        )
        
        logger.info(
            f"VERRA verification complete: {eligible_credits:.2f} tCO2 eligible"
        )
        
        return result


class GoldStandardVerifier(BaseVerifier):
    """
    Gold Standard verifier.
    
    Focuses on sustainable development co-benefits.
    """
    
    METHODOLOGY_VERSION = "GS AFOLU v2.0"
    
    def __init__(self):
        super().__init__(VerificationStandard.GOLD_STANDARD)
    
    def verify(
        self,
        soc_change: float,
        simulation_years: int,
        soc_time_series: List[float],
        baseline_soc: Optional[float] = None,
        project_area_ha: float = 100.0,
        buffer_area_ha: float = 20.0,
        management_intensity: str = "high",
        displacement_risk: str = "low",
        carbon_price_usd: float = 20.0,
        sdg_benefits: Optional[List[str]] = None
    ) -> VerificationResult:
        """
        Verify carbon credits under Gold Standard.
        
        Args:
            See VerraVerifier.verify()
            sdg_benefits: List of SDG categories addressed
            
        Returns:
            Verification result
        """
        logger.info("Running Gold Standard verification")
        
        # Similar calculations to VERRA but with GS-specific factors
        total_sequestration_tc = soc_change * project_area_ha
        co2e_sequestered = total_sequestration_tc * 3.67
        
        permanence = self.calculate_permanence_score(
            simulation_years, soc_time_series
        )
        
        baseline = baseline_soc or soc_time_series[0] * 0.85
        additionality = self.calculate_additionality_score(
            baseline, soc_time_series[-1], management_intensity
        )
        
        leakage = self.calculate_leakage_factor(
            project_area_ha, buffer_area_ha, displacement_risk
        )
        
        # Gold Standard typically has higher requirements but better prices
        discount_factor = permanence * additionality * (1 - leakage)
        eligible_credits = co2e_sequestered * discount_factor
        
        # GS premium for sustainable development
        sdg_multiplier = 1.0
        if sdg_benefits:
            sdg_multiplier = 1.0 + (len(sdg_benefits) * 0.05)  # 5% per SDG
            sdg_multiplier = min(sdg_multiplier, 1.25)  # Cap at 25%
        
        eligible_credits *= sdg_multiplier
        
        # Higher price assumption for GS
        gs_price_premium = 1.2
        adjusted_price = carbon_price_usd * gs_price_premium
        estimated_value = eligible_credits * adjusted_price
        
        verified = (
            permanence > 0.6 and
            additionality > 0.5 and
            simulation_years >= 15
        )
        
        notes = []
        if sdg_benefits:
            notes.append(f"SDG co-benefits identified: {', '.join(sdg_benefits)}")
        else:
            notes.append("Consider documenting SDG co-benefits for premium pricing")
        
        result = VerificationResult(
            standard=self.standard.value,
            verified=verified,
            verification_date=datetime.now(),
            total_sequestration_tc=total_sequestration_tc,
            co2e_sequestered_tco2=co2e_sequestered,
            eligible_credits_tco2=eligible_credits,
            permanence_score=permanence,
            additionality_score=additionality,
            leakage_factor=leakage,
            estimated_credit_value_usd=estimated_value,
            price_per_credit_usd=adjusted_price,
            methodology_version=self.METHODOLOGY_VERSION,
            validation_notes="; ".join(notes)
        )
        
        logger.info(
            f"Gold Standard verification complete: {eligible_credits:.2f} tCO2 eligible"
        )
        
        return result


class PlanVivoVerifier(BaseVerifier):
    """
    Plan Vivo verifier.
    
    Focuses on smallholder and community projects.
    """
    
    METHODOLOGY_VERSION = "Plan Vivo v3.0"
    
    def __init__(self):
        super().__init__(VerificationStandard.PLAN_VIVO)
    
    def verify(
        self,
        soc_change: float,
        simulation_years: int,
        soc_time_series: List[float],
        baseline_soc: Optional[float] = None,
        project_area_ha: float = 50.0,
        buffer_area_ha: float = 5.0,
        management_intensity: str = "medium",
        displacement_risk: str = "low",
        carbon_price_usd: float = 12.0,
        community_benefits: bool = True
    ) -> VerificationResult:
        """
        Verify carbon credits under Plan Vivo.
        
        Args:
            See other verifiers
            community_benefits: Whether community benefits are documented
            
        Returns:
            Verification result
        """
        logger.info("Running Plan Vivo verification")
        
        total_sequestration_tc = soc_change * project_area_ha
        co2e_sequestered = total_sequestration_tc * 3.67
        
        permanence = self.calculate_permanence_score(
            simulation_years, soc_time_series
        )
        
        baseline = baseline_soc or soc_time_series[0] * 0.9
        additionality = self.calculate_additionality_score(
            baseline, soc_time_series[-1], management_intensity
        )
        
        leakage = self.calculate_leakage_factor(
            project_area_ha, buffer_area_ha, displacement_risk
        )
        
        discount_factor = permanence * additionality * (1 - leakage)
        eligible_credits = co2e_sequestered * discount_factor
        
        # Plan Vivo is more accessible but has lower prices
        pv_accessibility_factor = 0.9  # Slightly more lenient
        eligible_credits *= pv_accessibility_factor
        
        # Community benefit bonus
        if community_benefits:
            community_bonus = 1.1
            notes = "Community benefits documented"
        else:
            community_bonus = 1.0
            notes = "Consider documenting community benefits"
        
        estimated_value = eligible_credits * carbon_price_usd * community_bonus
        
        # More accessible verification
        verified = (
            permanence > 0.4 and
            additionality > 0.3 and
            simulation_years >= 5
        )
        
        result = VerificationResult(
            standard=self.standard.value,
            verified=verified,
            verification_date=datetime.now(),
            total_sequestration_tc=total_sequestration_tc,
            co2e_sequestered_tco2=co2e_sequestered,
            eligible_credits_tco2=eligible_credits,
            permanence_score=permanence,
            additionality_score=additionality,
            leakage_factor=leakage,
            estimated_credit_value_usd=estimated_value,
            price_per_credit_usd=carbon_price_usd,
            methodology_version=self.METHODOLOGY_VERSION,
            validation_notes=notes
        )
        
        logger.info(
            f"Plan Vivo verification complete: {eligible_credits:.2f} tCO2 eligible"
        )
        
        return result


def get_verifier(standard: str) -> BaseVerifier:
    """
    Factory function to get appropriate verifier.
    
    Args:
        standard: Standard name (VERRA, GOLD_STANDARD, PLAN_VIVO)
        
    Returns:
        Appropriate verifier instance
    """
    verifiers = {
        "VERRA": VerraVerifier,
        "GOLD_STANDARD": GoldStandardVerifier,
        "PLAN_VIVO": PlanVivoVerifier
    }
    
    if standard.upper() not in verifiers:
        raise ValueError(
            f"Unknown standard: {standard}. "
            f"Available: {list(verifiers.keys())}"
        )
    
    return verifiers[standard.upper()]()
