# scripts/seed_sensors.py
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from api.core.database import engine, async_session, Base
from api.modules.iot.models import Sensor


SENSORS = [
    {"sensor_code": "TDR-001", "sensor_type": "tdr", "location_name": "حوضه کشف‌رود ۱", "latitude": 36.305, "longitude": 59.612, "elevation_m": 1050, "structure_id": 1, "status": "active", "battery_level": 95.0},
    {"sensor_code": "TDR-002", "sensor_type": "tdr", "location_name": "حوضه کشف‌رود ۲", "latitude": 36.308, "longitude": 59.615, "elevation_m": 1045, "structure_id": 1, "status": "active", "battery_level": 88.0},
    {"sensor_code": "TDR-003", "sensor_type": "tdr", "location_name": "دشت کویر", "latitude": 33.520, "longitude": 54.510, "elevation_m": 850, "structure_id": 2, "status": "active", "battery_level": 72.0},
    {"sensor_code": "FLUME-001", "sensor_type": "flume", "location_name": "کانال اصلی", "latitude": 36.310, "longitude": 59.620, "elevation_m": 1040, "structure_id": 3, "status": "active", "battery_level": 92.0},
    {"sensor_code": "FLUME-002", "sensor_type": "flume", "location_name": "کانال فرعی", "latitude": 36.312, "longitude": 59.625, "elevation_m": 1038, "structure_id": 3, "status": "active", "battery_level": 85.0},
    {"sensor_code": "RAIN-001", "sensor_type": "rain", "location_name": "ایستگاه هواشناسی", "latitude": 36.300, "longitude": 59.600, "elevation_m": 1060, "status": "active", "battery_level": 98.0},
    {"sensor_code": "PIEZ-001", "sensor_type": "piez", "location_name": "چاه پیزومتر ۱", "latitude": 36.315, "longitude": 59.630, "elevation_m": 1035, "structure_id": 4, "status": "active", "battery_level": 78.0},
    {"sensor_code": "PIEZ-002", "sensor_type": "piez", "location_name": "چاه پیزومتر ۲", "latitude": 36.318, "longitude": 59.635, "elevation_m": 1032, "structure_id": 4, "status": "active", "battery_level": 65.0},
    {"sensor_code": "WEATHER-001", "sensor_type": "weather", "location_name": "ایستگاه کامل", "latitude": 36.302, "longitude": 59.605, "elevation_m": 1058, "status": "active", "battery_level": 90.0},
]


async def seed():
    print("🌱 Seeding sensors...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("✅ Tables created")
    
    async with async_session() as session:
        for data in SENSORS:
            session.add(Sensor(**data))
        await session.commit()
        print(f"✅ Inserted {len(SENSORS)} sensors")
    
    await engine.dispose()
    print("✅ Done!")


if __name__ == "__main__":
    asyncio.run(seed())
