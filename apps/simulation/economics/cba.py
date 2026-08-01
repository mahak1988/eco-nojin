"""
CBA Cost-Benefit Analysis Model — Economic evaluation of projects and policies.
This is a skeleton implementation that will be replaced with real CBA model when available.

Current status: skeleton
Has real Python model?: Possible with custom implementation or libraries like numpy-financial
Implementation needed: Custom CBA implementation with NPV, IRR, and sensitivity analysis
"""
import logging
import math
import time
from typing import Any

from apps.simulation.base import (
    BaseSimulator, SimulationParameter, SimulationResult,
    SimulationRegistry, SimulationStatus,
)

logger = logging.getLogger(__name__)

@SimulationRegistry.register
class CBASimulator(BaseSimulator):
    @property
    def id(self) -> str: return "cba"
    @property
    def name(self) -> str: return "Cost-Benefit Analysis Model"
    @property
    def category(self) -> str: return "economics"
    @property
    def description(self) -> str: return "Cost-benefit analysis model for evaluating economic viability of projects and policies. Current skeleton implementation."
    @property
    def version(self) -> str: return "1.0.0-skeleton"

    def get_parameters(self) -> list[SimulationParameter]:
        return [
            SimulationParameter(name="project_type", label="Project Type", type="select", 
                              options=["infrastructure", "environmental", "agricultural", "energy", "social"], 
                              default="infrastructure", description="Type of project to evaluate", required=True),
            SimulationParameter(name="initial_investment", label="Initial Investment", type="float", 
                              default=1000000.0, min_value=1000.0, max_value=1000000000.0, unit="$", 
                              description="Initial investment cost", required=True),
            SimulationParameter(name="annual_costs", label="Annual Operating Costs", type="float", 
                              default=50000.0, min_value=0.0, max_value=100000000.0, unit="$", 
                              description="Annual operating and maintenance costs", required=True),
            SimulationParameter(name="annual_benefits", label="Annual Benefits", type="float", 
                              default=150000.0, min_value=0.0, max_value=100000000.0, unit="$", 
                              description="Annual benefits from the project", required=True),
            SimulationParameter(name="project_lifetime", label="Project Lifetime", type="int", 
                              default=20, min_value=1, max_value=100, unit="years", 
                              description="Expected lifetime of the project", required=True),
            SimulationParameter(name="discount_rate", label="Discount Rate", type="float", 
                              default=0.05, min_value=0.0, max_value=0.5, 
                              description="Discount rate for present value calculations", required=True),
            SimulationParameter(name="inflation_rate", label="Inflation Rate", type="float", 
                              default=0.02, min_value=0.0, max_value=0.3, 
                              description="Expected inflation rate", required=True),
        ]

    async def run(self, parameters: dict[str, Any]) -> SimulationResult:
        start = time.time()
        errors = self.validate(parameters)
        if errors:
            return SimulationResult(simulator_id=self.id, simulator_name=self.name,
                status=SimulationStatus.FAILED, parameters=parameters, error="; ".join(errors))
        
        try:
            # This is a skeleton - in the real implementation, we would run the CBA model
            outputs = self._run_skeleton_simulation(parameters)
            elapsed = (time.time() - start) * 1000
            return SimulationResult(simulator_id=self.id, simulator_name=self.name,
                status=SimulationStatus.COMPLETED, parameters=parameters, outputs=outputs,
                metrics=self._calculate_metrics(outputs), charts=self._generate_charts(outputs),
                execution_time_ms=elapsed)
        except Exception as e:
            elapsed = (time.time() - start) * 1000
            return SimulationResult(simulator_id=self.id, simulator_name=self.name,
                status=SimulationStatus.FAILED, parameters=parameters, error=str(e),
                execution_time_ms=elapsed)

    def _run_skeleton_simulation(self, params: dict[str, Any]) -> dict:
        """
        Skeleton implementation - this will be replaced with real CBA model
        """
        initial_investment = params.get("initial_investment", 1000000.0)
        annual_costs = params.get("annual_costs", 50000.0)
        annual_benefits = params.get("annual_benefits", 150000.0)
        project_lifetime = params.get("project_lifetime", 20)
        discount_rate = params.get("discount_rate", 0.05)
        inflation_rate = params.get("inflation_rate", 0.02)
        project_type = params.get("project_type", "infrastructure")
        
        # Calculate net annual benefits
        net_annual_benefit = annual_benefits - annual_costs
        
        # Calculate present value of costs and benefits
        pv_initial_cost = initial_investment
        pv_annual_costs = 0.0
        pv_annual_benefits = 0.0
        pv_net_benefits = []
        
        # Calculate present values for each year
        for year in range(1, project_lifetime + 1):
            # Adjust for inflation
            cost_adj = annual_costs * ((1 + inflation_rate) ** year)
            benefit_adj = annual_benefits * ((1 + inflation_rate) ** year)
            
            # Discount to present value
            pv_cost = cost_adj / ((1 + discount_rate) ** year)
            pv_benefit = benefit_adj / ((1 + discount_rate) ** year)
            
            pv_annual_costs += pv_cost
            pv_annual_benefits += pv_benefit
            
            # Net present value up to this year
            npv = pv_benefit - pv_cost - initial_investment
            pv_net_benefits.append(round(npv, 2))
        
        # Total present values
        pv_total_costs = pv_initial_cost + pv_annual_costs
        pv_total_benefits = pv_annual_benefits
        npv = pv_total_benefits - pv_total_costs
        
        # Calculate Benefit-Cost Ratio
        bcr = pv_total_benefits / pv_total_costs if pv_total_costs > 0 else 0
        
        # Calculate payback period (approximate)
        cumulative_cash_flow = -initial_investment
        payback_period = project_lifetime  # Default if never paid back
        for year in range(1, project_lifetime + 1):
            annual_net = net_annual_benefit * ((1 + inflation_rate) ** year) / ((1 + discount_rate) ** year)
            cumulative_cash_flow += annual_net
            if cumulative_cash_flow >= 0 and payback_period == project_lifetime:
                payback_period = year
                break
        
        # Calculate IRR (Internal Rate of Return) - simplified approximation
        # For a more accurate calculation, a numerical method would be needed
        irr_guess = (net_annual_benefit / initial_investment) * 2  # Rough estimate
        
        # Sensitivity analysis: calculate NPV at different discount rates
        sensitivity_discounts = [0.02, 0.05, 0.08, 0.10, 0.12]
        sensitivity_npvs = []
        
        for disc_rate in sensitivity_discounts:
            pv_benefits = 0.0
            pv_costs = initial_investment
            
            for year in range(1, project_lifetime + 1):
                annual_net = net_annual_benefit * ((1 + inflation_rate) ** year) / ((1 + disc_rate) ** year)
                pv_costs += annual_costs * ((1 + inflation_rate) ** year) / ((1 + disc_rate) ** year)
                pv_benefits += annual_benefits * ((1 + inflation_rate) ** year) / ((1 + disc_rate) ** year)
            
            sensitivity_npvs.append(round(pv_benefits - pv_costs, 2))
        
        return {
            "series": [
                {"key": "npv_timeline", "label": "Net Present Value Over Time ($)", "color": "#10b981", 
                 "values": pv_net_benefits, "kind": "line", "fill": True},
                {"key": "sensitivity_analysis", "label": "NPV Sensitivity Analysis ($)", "color": "#f59e0b", 
                 "values": sensitivity_npvs, "kind": "bar", "fill": True},
            ],
            "metrics": {
                "project_type": project_type,
                "initial_investment": initial_investment,
                "annual_costs": annual_costs,
                "annual_benefits": annual_benefits,
                "project_lifetime_years": project_lifetime,
                "discount_rate_applied": discount_rate,
                "inflation_rate_applied": inflation_rate,
                "net_present_value": round(npv, 2),
                "benefit_cost_ratio": round(bcr, 3),
                "payback_period_years": payback_period,
                "internal_rate_of_return_estimate": round(irr_guess, 3),
                "net_annual_benefit": round(net_annual_benefit, 2),
            },
        }

    def _calculate_metrics(self, outputs: dict) -> dict[str, float]:
        return {k: float(v) for k, v in outputs.get("metrics", {}).items() if isinstance(v, (int, float))}

    def _generate_charts(self, outputs: dict) -> dict[str, list]:
        return {s["key"]: s["values"] for s in outputs.get("series", [])}
