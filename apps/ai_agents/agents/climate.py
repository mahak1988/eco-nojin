"""
Climate Agent (Upgraded with Data Assimilation)
=================================================

Climate analysis and weather forecasting agent with data assimilation.

Enhanced capabilities:
    - Kalman filter for sensor data fusion
    - Ensemble Kalman Filter for non-linear climate models
    - Multi-source data assimilation (stations + satellite + models)
    - Weather pattern analysis with uncertainty quantification

Examples:
    >>> from apps.shared_ai.ai.llm_factory import get_llm
    >>> llm = get_llm()
    >>> agent = ClimateAgent(llm)
    >>> response = await agent.chat("What's the 7-day precipitation forecast for Shiraz?")
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

import numpy as np
from langchain_core.tools import BaseTool

from apps.shared_ai.ai.base_agent import ModularAgentBuilder
from apps.shared_ai.ai.tools.rag_tools import (
    get_knowledge_base_stats,
    get_rag_context,
    search_knowledge_base,
    upload_document,
)
from apps.ai_agents.tools.registry import (
    calculate_irrigation,
    get_weather_data,
)

logger = logging.getLogger(__name__)

# =========================================================================
# System Prompt
# =========================================================================

CLIMATE_PROMPT: str = """
You are an expert climate analyst for the Econojin platform.

Your responsibilities:
1. Analyze weather and climate data for agricultural decision-making
2. Provide precipitation and temperature forecasts with uncertainty estimates
3. Calculate evapotranspiration (ET) and water balance
4. Assess climate risks and extreme weather events

Guidelines:
- Use get_weather_data tool for current and forecast weather data
- Use calculate_irrigation for precise water requirement estimates
- **Use get_rag_context to retrieve climate research and historical data**
- search_knowledge_base to find climate patterns and regional data
- Incorporate Data Assimilation results when provided by the system
- Always report uncertainty alongside predictions
- Use meteorological and climatological terminology appropriately
- If a tool returns an error, fall back to your general meteorological knowledge

Available tools:
- get_weather_data: Fetch weather forecast for a location
- calculate_irrigation: Calculate water requirements for a crop
- get_rag_context: Retrieve relevant climate documents
- search_knowledge_base: Search the document repository
- upload_document: Upload new climate reference documents

Note: When data assimilation results are provided, use them to improve
your forecasts and explicitly mention the assimilation technique used.
"""


class ClimateAgent:
    """Climate and weather analysis agent with data assimilation.

    Integrates weather data, climate models, and data assimilation
    techniques to provide scientifically grounded forecasts.

    Attributes:
        llm: The language model instance.
        tools: LangChain tools for the agent workflow.
        builder: ModularAgentBuilder for the LangGraph workflow.
        graph: Compiled execution graph.
    """

    def __init__(self, llm: Any) -> None:
        """Initialize the climate agent.

        Args:
            llm: A LangChain-compatible chat model.
        """
        self.llm: Any = llm
        self.tools: List[BaseTool] = [
            get_weather_data,
            calculate_irrigation,
            get_rag_context,
            search_knowledge_base,
            upload_document,
            get_knowledge_base_stats,
        ]

        self.builder: ModularAgentBuilder = ModularAgentBuilder(
            llm=self.llm,
            tools=self.tools,
            system_prompt=CLIMATE_PROMPT,
        )
        self.graph: Any = self.builder.build()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    async def chat(
        self,
        user_message: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Process a user message and return an AI response.

        Args:
            user_message: User's question or request.
            context: Optional context dict (e.g., location, farm data).

        Returns:
            Generated response string.
        """
        logger.info(
            "ClimateAgent: processing message (length=%d)", len(user_message)
        )

        result: str = await self.builder.run(user_message, context)

        if not result:
            logger.warning("ClimateAgent: empty response")
            return "I could not process your climate query. Please try again."

        return result

    # ------------------------------------------------------------------
    # Data Assimilation methods
    # ------------------------------------------------------------------

    async def assimilate_temperature(
        self,
        station_readings: List[float],
        satellite_estimate: float,
        model_forecast: float,
        station_variances: Optional[List[float]] = None,
        satellite_variance: float = 0.3,
        model_variance: float = 0.2,
    ) -> Dict[str, Any]:
        """Fuse multiple temperature sources via Kalman filtering.

        Args:
            station_readings: Temperature readings from ground stations.
            satellite_estimate: Satellite-derived temperature estimate.
            model_forecast: Numerical model forecast temperature.
            station_variances: Per-station variance estimates.
            satellite_variance: Uncertainty in satellite estimate.
            model_variance: Uncertainty in model forecast.

        Returns:
            Dict with fused temperature, uncertainty, and source contributions.
        """
        from apps.shared_ai.assimilation.data_fusion import DataFusionEngine

        engine: DataFusionEngine = DataFusionEngine(default_method="weighted_average")

        # Add station readings
        if station_variances is None:
            station_variances = [0.1] * len(station_readings)

        for i, (reading, var) in enumerate(
            zip(station_readings, station_variances)
        ):
            engine.add_source(
                name=f"station_{i + 1}",
                data=[reading],
                variance=[var],
                metadata={"type": "ground_station"},
            )

        # Add satellite
        engine.add_source(
            name="satellite",
            data=[satellite_estimate],
            variance=[satellite_variance],
            metadata={"type": "satellite"},
        )

        # Add model
        engine.add_source(
            name="nwp_model",
            data=[model_forecast],
            variance=[model_variance],
            metadata={"type": "numerical_model"},
        )

        result: Dict[str, Any] = engine.fuse()

        # Generate AI interpretation
        interpretation_question: str = (
            f"Temperature Data Assimilation Results:\n"
            f"Station readings: {station_readings}\n"
            f"Satellite estimate: {satellite_estimate}°C\n"
            f"Model forecast: {model_forecast}°C\n"
            f"Fused estimate: {result.get('fused_value')}°C\n"
            f"Uncertainty: ±{np.sqrt(result.get('variance', 0.0)):.2f}°C\n\n"
            f"Provide: 1) Interpretation of the fused result, "
            f"2) Which source had the most influence, "
            f"3) Confidence assessment, 4) Recommended actions."
        )

        interpretation: str = await self.chat(interpretation_question)

        return {
            **result,
            "ai_interpretation": interpretation,
            "assimilation_method": "inverse_variance_weighted_kalman",
            "sources_used": len(station_readings) + 2,  # stations + satellite + model
        }

    async def assimilate_precipitation_ensemble(
        self,
        ensemble_members: List[List[float]],
        observation: List[float],
        days: int = 7,
    ) -> Dict[str, Any]:
        """Assimilate precipitation observations into an ensemble forecast.

        Uses the Ensemble Kalman Filter for non-linear precipitation dynamics.

        Args:
            ensemble_members: List of ensemble forecast vectors (N_members x days).
            observation: Observed precipitation vector (days,).
            days: Number of forecast days.

        Returns:
            Dict with assimilated ensemble, statistics, and interpretation.
        """
        from apps.shared_ai.assimilation.ensemble import EnsembleKalmanFilter

        n_members: int = len(ensemble_members)

        enkf: EnsembleKalmanFilter = EnsembleKalmanFilter(
            state_dim=days,
            ensemble_size=n_members,
            measurement_dim=days,
            process_noise_std=0.5,
            measurement_noise_std=2.0,
            inflation_factor=1.02,
        )

        # Initialize ensemble with forecast members
        for i, member in enumerate(ensemble_members):
            enkf.X[:, i] = np.array(member, dtype=np.float64)

        # Update with observations
        assimilated_mean: np.ndarray = enkf.update(
            measurement=np.array(observation, dtype=np.float64)
        )
        assimilated_std: np.ndarray = np.std(enkf.X, axis=1)
        spread: float = enkf.ensemble_spread()

        # Generate interpretation
        interpretation_question: str = (
            f"Precipitation Ensemble Data Assimilation:\n"
            f"Original ensemble spread: {spread:.2f}\n"
            f"Assimilated mean (mm/day): {assimilated_mean.tolist()}\n"
            f"Assimilated std (mm/day): {assimilated_std.tolist()}\n\n"
            f"Provide: 1) Impact of assimilation on forecast uncertainty, "
            f"2) Key precipitation patterns, "
            f"3) Agricultural implications (flood/drought risk), "
            f"4) Recommended monitoring actions."
        )

        interpretation: str = await self.chat(interpretation_question)

        return {
            "assimilated_mean": assimilated_mean.tolist(),
            "assimilated_std": assimilated_std.tolist(),
            "ensemble_spread": spread,
            "ensemble_size": n_members,
            "assimilation_method": "ensemble_kalman_filter",
            "ai_interpretation": interpretation,
        }

    async def multi_source_climate_analysis(
        self,
        station_data: Dict[str, List[float]],
        satellite_data: Dict[str, List[float]],
        model_data: Dict[str, List[float]],
        variables: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Comprehensive multi-source climate data fusion.

        Fuses weather station, satellite, and model data for
        multiple climate variables simultaneously.

        Args:
            station_data: Dict of {variable: [values]} from ground stations.
            satellite_data: Dict of {variable: [values]} from satellite.
            model_data: Dict of {variable: [values]} from NWP model.
            variables: List of variables to fuse (default: all).

        Returns:
            Dict with fused values per variable and AI interpretation.
        """
        from apps.shared_ai.assimilation.data_fusion import DataFusionEngine

        vars_to_fuse: List[str] = variables or list(station_data.keys())
        variable_results: Dict[str, Any] = {}

        for var in vars_to_fuse:
            engine: DataFusionEngine = DataFusionEngine(
                default_method="weighted_average"
            )

            if var in station_data:
                for i, val in enumerate(station_data[var]):
                    engine.add_source(
                        name=f"station_{i + 1}_{var}",
                        data=[val],
                        variance=[0.1],
                        metadata={"type": "ground_station", "variable": var},
                    )

            if var in satellite_data:
                engine.add_source(
                    name=f"satellite_{var}",
                    data=[satellite_data[var][0]],
                    variance=[0.3],
                    metadata={"type": "satellite", "variable": var},
                )

            if var in model_data:
                engine.add_source(
                    name=f"model_{var}",
                    data=[model_data[var][0]],
                    variance=[0.2],
                    metadata={"type": "nwp_model", "variable": var},
                )

            if engine.sources:
                variable_results[var] = engine.fuse()

        # Generate AI synthesis
        synth_question: str = (
            f"Multi-source climate data fusion results:\n"
            f"Variables analyzed: {vars_to_fuse}\n"
            f"Fused results: {variable_results}\n\n"
            f"Provide: 1) Overall climate assessment, "
            f"2) Variable-by-variable confidence analysis, "
            f"3) Cross-variable consistency check, "
            f"4) Recommendations for agricultural planning."
        )

        synthesis: str = await self.chat(synth_question)

        return {
            "variable_results": variable_results,
            "variables_analyzed": vars_to_fuse,
            "assimilation_method": "multi_source_weighted_average",
            "ai_synthesis": synthesis,
        }

    # ------------------------------------------------------------------
    # Specialized analysis
    # ------------------------------------------------------------------

    async def drought_risk_assessment(
        self,
        latitude: float,
        longitude: float,
        historical_precip: Optional[List[float]] = None,
    ) -> Dict[str, Any]:
        """Assess drought risk using data assimilation and climate analysis.

        Args:
            latitude: Location latitude.
            longitude: Location longitude.
            historical_precip: Optional historical precipitation data (mm).

        Returns:
            Dict with risk assessment, drought indices, and recommendations.
        """
        weather: Any = await get_weather_data.ainvoke(
            {"latitude": latitude, "longitude": longitude, "days": 30}
        )

        context: str = ""
        if historical_precip:
            from apps.shared_ai.assimilation.kalman_filter import KalmanFilter

            kf: KalmanFilter = KalmanFilter(
                state_dim=1, measurement_dim=1,
                process_noise=0.5, measurement_noise=2.0,
            )

            for obs in historical_precip:
                kf.step(measurement=[obs])

            smoothed: np.ndarray = kf.get_state()
            trend: float = float(smoothed[0])
            context = (
                f"Kalman-smoothed precipitation trend: {trend:.1f} mm\n"
                f"Historical data points: {len(historical_precip)}\n"
            )

        assessment_question: str = (
            f"Drought risk assessment for location ({latitude}, {longitude}):\n"
            f"Weather forecast: {weather}\n"
            f"{context}\n"
            f"Provide: 1) SPI (Standardized Precipitation Index) estimate, "
            f"2) Soil moisture deficit forecast, "
            f"3) Crop water stress risk level (low/medium/high/extreme), "
            f"4) Mitigation recommendations, "
            f"5) Irrigation scheduling advice."
        )

        assessment: str = await self.chat(assessment_question)

        return {
            "location": {"latitude": latitude, "longitude": longitude},
            "weather_data": str(weather)[:500] if weather else "N/A",
            "assimilation_context": context,
            "assessment": assessment,
        }
