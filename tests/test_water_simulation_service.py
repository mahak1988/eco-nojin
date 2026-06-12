# tests/test_water_simulation_service.py

from datetime import date

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from api.core.database import Base
from api.modules.soil import models as soil_models
from api.modules.water import models as water_models
from api.modules.water.schemas import DailyInput
from api.modules.water.service import WaterSimulationService


class FakeCore:
    """
    Fake implementation of SoilWaterCoreService for deterministic tests.
    """

    def run_simulation(self, soil_profile, soil_layers, daily_inputs, scenario_id, model_version):
        results = []
        for d in daily_inputs:
            # runoff = 10% of precipitation + 5% of irrigation
            runoff = 0.1 * d["precipitation"] + 0.05 * d["irrigation"]
            deep_drainage = 0.02 * (d["precipitation"] + d["irrigation"])
            soil_moisture = 100.0  # ثابت برای تست

            results.append(
                {
                    "date": d["date"],
                    "precipitation": d["precipitation"],
                    "irrigation": d["irrigation"],
                    "evapotranspiration": d["evapotranspiration"],
                    "runoff": runoff,
                    "deep_drainage": deep_drainage,
                    "soil_moisture": soil_moisture,
                }
            )
        return results


def create_in_memory_session() -> Session:
    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return TestingSessionLocal()


def seed_soil_profile(db: Session) -> int:
    profile = soil_models.SoilProfile(
        project_id=1,
        name="Test profile",
        description="Unit test profile",
    )
    db.add(profile)
    db.flush()

    layer = soil_models.SoilLayer(
        profile_id=profile.id,
        depth_top_cm=0.0,
        depth_bottom_cm=30.0,
        bulk_density=1.3,
        field_capacity=0.25,
        wilting_point=0.1,
        saturated_hydraulic_conductivity=10.0,
        organic_carbon=1.5,
    )
    db.add(layer)
    db.commit()
    db.refresh(profile)
    return profile.id


def test_run_simulation_persists_results():
    db = create_in_memory_session()
    soil_profile_id = seed_soil_profile(db)

    # inject fake core
    service = WaterSimulationService(db=db, model_version="test-v1")
    service.core = FakeCore()

    daily_inputs = [
        DailyInput(
            date=date(2026, 6, 1),
            precipitation=10.0,
            irrigation=5.0,
            evapotranspiration=4.0,
        ),
        DailyInput(
            date=date(2026, 6, 2),
            precipitation=0.0,
            irrigation=8.0,
            evapotranspiration=3.0,
        ),
    ]

    entities = service.run_simulation(
        scenario_id=42,
        soil_profile_id=soil_profile_id,
        daily_inputs=daily_inputs,
    )

    assert len(entities) == 2
    # check model_version
    assert all(e.model_version == "test-v1" for e in entities)

    # check deterministic runoff formula for first day
    first = entities[0]
    assert first.runoff == 0.1 * 10.0 + 0.05 * 5.0
    assert first.deep_drainage == 0.02 * (10.0 + 5.0)
    assert first.soil_moisture == 100.0

    # check data actually persisted
    rows = (
        db.query(water_models.WaterBalance)
        .filter(water_models.WaterBalance.scenario_id == 42)
        .all()
    )
    assert len(rows) == 2