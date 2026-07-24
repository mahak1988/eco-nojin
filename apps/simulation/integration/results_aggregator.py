"""
Results Aggregator for Multi-Model Simulations
===============================================
Aggregates and analyzes results from multiple simulation models.
"""

import logging
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
from datetime import datetime
import statistics

logger = logging.getLogger(__name__)


@dataclass
class AggregatedResults:
    """Aggregated results from multiple models."""
    
    aggregation_id: str
    created_at: datetime
    models_included: List[str]
    
    # Carbon metrics
    total_soc_change_tc_ha: float = 0.0
    soc_sequestration_rate_tc_ha_year: float = 0.0
    co2_equivalent_tco2_ha: float = 0.0
    
    # Water metrics
    water_yield_mm_year: float = 0.0
    evapotranspiration_mm_year: float = 0.0
    runoff_mm_year: float = 0.0
    
    # Crop metrics
    avg_yield_kg_ha: float = 0.0
    biomass_total_kg_ha: float = 0.0
    
    # Economic metrics
    carbon_credit_value_usd_ha: float = 0.0
    crop_revenue_usd_ha: float = 0.0
    total_ecosystem_value_usd_ha: float = 0.0
    
    # Uncertainty estimates
    uncertainty_ranges: Dict[str, Dict[str, float]] = field(default_factory=dict)
    
    # Model agreement scores
    model_agreement: Dict[str, float] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "aggregation_id": self.aggregation_id,
            "created_at": self.created_at.isoformat(),
            "models_included": self.models_included,
            "carbon_metrics": {
                "soc_change_tc_ha": self.total_soc_change_tc_ha,
                "sequestration_rate_tc_ha_year": self.soc_sequestration_rate_tc_ha_year,
                "co2_equivalent_tco2_ha": self.co2_equivalent_tco2_ha
            },
            "water_metrics": {
                "water_yield_mm_year": self.water_yield_mm_year,
                "evapotranspiration_mm_year": self.evapotranspiration_mm_year,
                "runoff_mm_year": self.runoff_mm_year
            },
            "crop_metrics": {
                "avg_yield_kg_ha": self.avg_yield_kg_ha,
                "biomass_total_kg_ha": self.biomass_total_kg_ha
            },
            "economic_metrics": {
                "carbon_credit_value_usd_ha": self.carbon_credit_value_usd_ha,
                "crop_revenue_usd_ha": self.crop_revenue_usd_ha,
                "total_ecosystem_value_usd_ha": self.total_ecosystem_value_usd_ha
            },
            "uncertainty": self.uncertainty_ranges,
            "model_agreement": self.model_agreement
        }


class ResultsAggregator:
    """
    Aggregates results from multiple simulation models.
    
    Combines outputs from RothC, SWAT, APSIM, and DSSAT to provide
    comprehensive assessment of ecosystem services.
    """
    
    def __init__(self):
        """Initialize results aggregator."""
        logger.info("ResultsAggregator initialized")
    
    def aggregate(
        self,
        model_results: Dict[str, Any],
        area_ha: float = 1.0
    ) -> AggregatedResults:
        """
        Aggregate results from multiple models.
        
        Args:
            model_results: Dictionary of {model_name: result_object}
            area_ha: Area in hectares for scaling
            
        Returns:
            AggregatedResults object
        """
        logger.info(f"Aggregating results from {len(model_results)} models")
        
        aggregation_id = f"agg_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        models_included = list(model_results.keys())
        
        # Extract metrics from each model
        carbon_metrics = self._extract_carbon_metrics(model_results)
        water_metrics = self._extract_water_metrics(model_results)
        crop_metrics = self._extract_crop_metrics(model_results)
        economic_metrics = self._calculate_economic_metrics(
            carbon_metrics, crop_metrics
        )
        
        # Calculate uncertainty
        uncertainty = self._calculate_uncertainty(model_results)
        
        # Calculate model agreement
        agreement = self._calculate_model_agreement(model_results)
        
        aggregated = AggregatedResults(
            aggregation_id=aggregation_id,
            created_at=datetime.now(),
            models_included=models_included,
            total_soc_change_tc_ha=carbon_metrics.get('soc_change', 0.0),
            soc_sequestration_rate_tc_ha_year=carbon_metrics.get('sequestration_rate', 0.0),
            co2_equivalent_tco2_ha=carbon_metrics.get('co2_equivalent', 0.0),
            water_yield_mm_year=water_metrics.get('water_yield', 0.0),
            evapotranspiration_mm_year=water_metrics.get('et', 0.0),
            runoff_mm_year=water_metrics.get('runoff', 0.0),
            avg_yield_kg_ha=crop_metrics.get('avg_yield', 0.0),
            biomass_total_kg_ha=crop_metrics.get('biomass', 0.0),
            carbon_credit_value_usd_ha=economic_metrics.get('carbon_credits', 0.0),
            crop_revenue_usd_ha=economic_metrics.get('crop_revenue', 0.0),
            total_ecosystem_value_usd_ha=economic_metrics.get('total_value', 0.0),
            uncertainty_ranges=uncertainty,
            model_agreement=agreement
        )
        
        logger.info(f"Aggregation complete: {aggregation_id}")
        return aggregated
    
    def _extract_carbon_metrics(
        self, 
        model_results: Dict[str, Any]
    ) -> Dict[str, float]:
        """Extract carbon-related metrics from model results."""
        metrics = {}
        soc_values = []
        
        # RothC provides SOC change directly
        if 'rothc' in model_results:
            rothc_result = model_results['rothc']
            if hasattr(rothc_result, 'to_dict'):
                rothc_result = rothc_result.to_dict()
            
            soc_change = rothc_result.get('carbon_stocks', {}).get('soc_change_t_ha', 0.0)
            soc_values.append(soc_change)
            
            sequestration_rate = rothc_result.get('sequestration', {}).get(
                'rate_t_ha_year', 0.0
            )
            metrics['sequestration_rate'] = sequestration_rate
        
        # APSIM/DSSAT provide biomass which can be converted to C
        for model_name in ['apsim', 'dssat']:
            if model_name in model_results:
                result = model_results[model_name]
                if hasattr(result, 'to_dict'):
                    result = result.to_dict()
                
                biomass = result.get('crop_performance', {}).get('biomass_total', 0.0)
                # Assume 40% carbon content in biomass
                carbon_input = biomass * 0.4 / 1000.0  # kg/ha to t/ha
                soc_values.append(carbon_input * 0.3)  # 30% retention
        
        if soc_values:
            metrics['soc_change'] = sum(soc_values) / len(soc_values)
            # Convert C to CO2 equivalent (1 tC = 3.67 tCO2)
            metrics['co2_equivalent'] = metrics['soc_change'] * 3.67
        else:
            metrics['soc_change'] = 0.0
            metrics['co2_equivalent'] = 0.0
        
        return metrics
    
    def _extract_water_metrics(
        self,
        model_results: Dict[str, Any]
    ) -> Dict[str, float]:
        """Extract water-related metrics from model results."""
        metrics = {}
        
        # SWAT provides comprehensive water balance
        if 'swat' in model_results:
            swat_result = model_results['swat']
            if hasattr(swat_result, 'to_dict'):
                swat_result = swat_result.to_dict()
            
            hydrology = swat_result.get('hydrology', {})
            metrics['water_yield'] = hydrology.get('water_yield', 0.0)
            metrics['runoff'] = hydrology.get('surface_runoff', 0.0)
            
            et = hydrology.get('evapotranspiration', {})
            metrics['et'] = et.get('actual_et_mm', 0.0)
        
        return metrics
    
    def _extract_crop_metrics(
        self,
        model_results: Dict[str, Any]
    ) -> Dict[str, float]:
        """Extract crop-related metrics from model results."""
        metrics = {}
        yields = []
        biomass_values = []
        
        for model_name in ['apsim', 'dssat']:
            if model_name in model_results:
                result = model_results[model_name]
                if hasattr(result, 'to_dict'):
                    result = result.to_dict()
                
                crop_perf = result.get('crop_performance', {})
                
                yield_val = crop_perf.get('grain_yield', 0.0)
                if yield_val > 0:
                    yields.append(yield_val)
                
                biomass = crop_perf.get('biomass_total', 0.0)
                if biomass > 0:
                    biomass_values.append(biomass)
        
        if yields:
            metrics['avg_yield'] = sum(yields) / len(yields)
        else:
            metrics['avg_yield'] = 0.0
        
        if biomass_values:
            metrics['biomass'] = sum(biomass_values) / len(biomass_values)
        else:
            metrics['biomass'] = 0.0
        
        return metrics
    
    def _calculate_economic_metrics(
        self,
        carbon_metrics: Dict[str, float],
        crop_metrics: Dict[str, float]
    ) -> Dict[str, float]:
        """Calculate economic value of ecosystem services."""
        metrics = {}
        
        # Carbon credits (assuming $15-25 per tCO2)
        carbon_price = 20.0  # USD per tCO2
        carbon_credits = carbon_metrics.get('co2_equivalent', 0.0) * carbon_price
        metrics['carbon_credits'] = carbon_credits
        
        # Crop revenue (assuming $200 per ton of grain)
        crop_price = 0.2  # USD per kg
        crop_revenue = crop_metrics.get('avg_yield', 0.0) * crop_price
        metrics['crop_revenue'] = crop_revenue
        
        # Total ecosystem service value
        total_value = carbon_credits + crop_revenue
        
        # Add water regulation value (simplified)
        water_value = 5.0  # USD per mm of water yield
        metrics['total_value'] = total_value
        
        return metrics
    
    def _calculate_uncertainty(
        self,
        model_results: Dict[str, Any]
    ) -> Dict[str, Dict[str, float]]:
        """Calculate uncertainty ranges from multi-model ensemble."""
        uncertainty = {}
        
        # Collect SOC predictions from all models
        soc_predictions = []
        for model_name, result in model_results.items():
            if hasattr(result, 'to_dict'):
                result = result.to_dict()
            
            # Try to extract SOC or equivalent
            if 'carbon_stocks' in result:
                soc = result['carbon_stocks'].get('final_soc_t_ha', 0.0)
                if soc > 0:
                    soc_predictions.append(soc)
        
        if len(soc_predictions) >= 2:
            mean_soc = statistics.mean(soc_predictions)
            std_soc = statistics.stdev(soc_predictions)
            
            uncertainty['soc'] = {
                'mean': mean_soc,
                'std': std_soc,
                'min': min(soc_predictions),
                'max': max(soc_predictions),
                'confidence_95_lower': mean_soc - 1.96 * std_soc,
                'confidence_95_upper': mean_soc + 1.96 * std_soc
            }
        
        return uncertainty
    
    def _calculate_model_agreement(
        self,
        model_results: Dict[str, Any]
    ) -> Dict[str, float]:
        """Calculate agreement between models."""
        agreement = {}
        
        # Simple agreement metric: coefficient of variation
        soc_values = []
        for model_name, result in model_results.items():
            if hasattr(result, 'to_dict'):
                result = result.to_dict()
            
            if 'carbon_stocks' in result:
                soc = result['carbon_stocks'].get('final_soc_t_ha', 0.0)
                if soc > 0:
                    soc_values.append(soc)
        
        if len(soc_values) >= 2:
            mean_val = statistics.mean(soc_values)
            std_val = statistics.stdev(soc_values)
            
            # CV < 0.1 = high agreement, > 0.3 = low agreement
            cv = std_val / mean_val if mean_val > 0 else 1.0
            agreement_score = max(0, 1 - cv)
            
            agreement['carbon_stocks'] = agreement_score
        
        return agreement
    
    def generate_summary_report(
        self,
        aggregated: AggregatedResults
    ) -> str:
        """Generate human-readable summary report."""
        report = f"""
╔══════════════════════════════════════════════════════════╗
║       ECO NOZHIN - Simulation Results Summary           ║
╠══════════════════════════════════════════════════════════╣

Aggregation ID: {aggregated.aggregation_id}
Models Used: {', '.join(aggregated.models_included)}
Generated: {aggregated.created_at.strftime('%Y-%m-%d %H:%M')}

───────────────────────────────────────────────────────────
CARBON SEQUESTRATION
───────────────────────────────────────────────────────────
  SOC Change:          {aggregated.total_soc_change_tc_ha:>8.2f} tC/ha
  Sequestration Rate:  {aggregated.soc_sequestration_rate_tc_ha_year:>8.2f} tC/ha/year
  CO₂ Equivalent:      {aggregated.co2_equivalent_tco2_ha:>8.2f} tCO₂/ha
  
───────────────────────────────────────────────────────────
WATER BALANCE
───────────────────────────────────────────────────────────
  Water Yield:         {aggregated.water_yield_mm_year:>8.2f} mm/year
  Evapotranspiration:  {aggregated.evapotranspiration_mm_year:>8.2f} mm/year
  Surface Runoff:      {aggregated.runoff_mm_year:>8.2f} mm/year

───────────────────────────────────────────────────────────
CROP PRODUCTION
───────────────────────────────────────────────────────────
  Average Yield:       {aggregated.avg_yield_kg_ha:>8.2f} kg/ha
  Total Biomass:       {aggregated.biomass_total_kg_ha:>8.2f} kg/ha

───────────────────────────────────────────────────────────
ECONOMIC VALUE
───────────────────────────────────────────────────────────
  Carbon Credits:      ${aggregated.carbon_credit_value_usd_ha:>8.2f} USD/ha
  Crop Revenue:        ${aggregated.crop_revenue_usd_ha:>8.2f} USD/ha
  Total Value:         ${aggregated.total_ecosystem_value_usd_ha:>8.2f} USD/ha

───────────────────────────────────────────────────────────
MODEL AGREEMENT
───────────────────────────────────────────────────────────
"""
        
        for metric, score in aggregated.model_agreement.items():
            report += f"  {metric:<20} {score*100:>6.1f}%\n"
        
        report += "\n╚══════════════════════════════════════════════════════════╝\n"
        
        return report
