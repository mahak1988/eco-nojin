# api/modules/water/service.py

import logging
from datetime import date
from typing import Iterable, List

from sqlalchemy.orm import Session

from api.modules.soil import models as soil_models
from api.modules.water import models as water_models
from api.modules.water.schemas import DailyInput

# مسیر هسته را با ساختار واقعی پروژه هماهنگ کن
# مثال:
# from api.services.soilwatercore import SoilWaterCoreService
from apiservicessoilwatercore import SoilWaterCoreService  # TODO: adjust

logger = logging.getLogger(__name__)


class WaterSimulationService:
    """
    Application service for soil–water balance simulations.

    Responsibilities:
    - Load soil domain entities
    - Call scientific core
    - Persist results into WaterBalance
    - Emit structured logs for observability
    """

    def __init__(self, db: Session, model_version: str = "v1") -> None:
        self.db = db
        self.core = SoilWaterCoreService()
        self.model_version = model_version

    # ---------- Load soil domain objects ----------

    def get_soil_profile_with_layers(
        self,
        soil_profile_id: int,
    ) -> tuple[soil_models.SoilProfile, List[soil_models.SoilLayer]]:
        profile = (
            self.db.query(soil_models.SoilProfile)
            .filter(soil_models.SoilProfile.id == soil_profile_id)
            .first()
        )
        if profile is None:
            logger.warning(
                "soil_profile_not_found",
                extra={"soil_profile_id": soil_profile_id},
            )
            raise ValueError("soil_profile_not_found")

        layers = (
            self.db.query(soil_models.SoilLayer)
            .filter(soil_models.SoilLayer.profile_id == soil_profile_id)
            .order_by(soil_models.SoilLayer.depth_top_cm)
            .all()
        )

        logger.info(
            "soil_profile_loaded",
            extra={
                "soil_profile_id": soil_profile_id,
                "layers_count": len(layers),
            },
        )
        return profile, layers

    # ---------- Run core model ----------

    def run_simulation(
        self,
        scenario_id: int,
        soil_profile_id: int,
        daily_inputs: Iterable[DailyInput],
    ) -> List[water_models.WaterBalance]:
        """
        High-level use case:
        - Load soil profile + layers
        - Invoke core model
        - Persist results into WaterBalance
        - Return persistent entities
        """

        inputs_list = list(daily_inputs)
        days_count = len(inputs_list)

        logger.info(
            "water_simulation_start",
            extra={
                "scenario_id": scenario_id,
                "soil_profile_id": soil_profile_id,
                "days_count": days_count,
                "model_version": self.model_version,
            },
        )

        profile, layers = self.get_soil_profile_with_layers(soil_profile_id)

        core_inputs = [
            {
                "date": d.date,
                "precipitation": d.precipitation or 0.0,
                "irrigation": d.irrigation or 0.0,
                "evapotranspiration": d.evapotranspiration or 0.0,
            }
            for d in inputs_list
        ]

        results = self.core.run_simulation(
            soil_profile=profile,
            soil_layers=layers,
            daily_inputs=core_inputs,
            scenario_id=scenario_id,
            model_version=self.model_version,
        )
        # انتظار: list[dict] با کلیدهای date, precipitation, irrigation, evapotranspiration, runoff, deep_drainage, soil_moisture

        if not isinstance(results, list):
            logger.error(
                "core_invalid_output_type",
                extra={
                    "scenario_id": scenario_id,
                    "soil_profile_id": soil_profile_id,
                    "returned_type": type(results).__name__,
                },
            )
            raise RuntimeError("invalid_core_output")

        logger.info(
            "core_simulation_completed",
            extra={
                "scenario_id": scenario_id,
                "soil_profile_id": soil_profile_id,
                "result_rows": len(results),
            },
        )

        # remove previous rows for idempotency
        deleted = (
            self.db.query(water_models.WaterBalance)
            .filter(
                water_models.WaterBalance.scenario_id == scenario_id,
                water_models.WaterBalance.model_version == self.model_version,
            )
            .delete()
        )
        self.db.flush()

        logger.info(
            "water_balance_deleted_previous",
            extra={
                "scenario_id": scenario_id,
                "model_version": self.model_version,
                "deleted_rows": deleted,
            },
        )

        entities: List[water_models.WaterBalance] = []
        for r in results:
            row = water_models.WaterBalance(
                scenario_id=scenario_id,
                soil_profile_id=soil_profile_id,
                date=self._ensure_date(r["date"]),
                precipitation=r.get("precipitation"),
                irrigation=r.get("irrigation"),
                evapotranspiration=r.get("evapotranspiration"),
                runoff=r.get("runoff"),
                deep_drainage=r.get("deep_drainage"),
                soil_moisture=r.get("soil_moisture"),
                model_version=self.model_version,
            )
            self.db.add(row)
            entities.append(row)

        self.db.commit()
        for e in entities:
            self.db.refresh(e)

        logger.info(
            "water_simulation_persisted",
            extra={
                "scenario_id": scenario_id,
                "soil_profile_id": soil_profile_id,
                "rows_inserted": len(entities),
                "model_version": self.model_version,
            },
        )

        return entities

    @staticmethod
    def _ensure_date(value) -> date:
        if isinstance(value, date):
            return value
        return date.fromisoformat(str(value))