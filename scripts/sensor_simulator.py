# scripts/sensor_simulator.py
"""
شبیه‌ساز سنسورهای IoT برای تست سیستم
این اسکریپت داده‌های واقع‌گرایانه تولید و به MQTT Broker ارسال می‌کند
"""
import asyncio
import json
import random
import time
from datetime import datetime, timezone
import sys

# تنظیمات
MQTT_BROKER = "localhost"
MQTT_PORT = 1883
INTERVAL = 5  # ثانیه

# تعریف سنسورها
SENSORS = [
    {"code": "TDR-001", "type": "tdr", "location": "حوضه کشف‌رود - ایستگاه ۱", "base_value": 35},
    {"code": "TDR-002", "type": "tdr", "location": "حوضه کشف‌رود - ایستگاه ۲", "base_value": 42},
    {"code": "TDR-003", "type": "tdr", "location": "دشت کویر - زون A", "base_value": 18},
    {"code": "FLUME-001", "type": "flume", "location": "کانال اصلی - ایستگاه ۱", "base_value": 1.2},
    {"code": "FLUME-002", "type": "flume", "location": "کانال فرعی - ایستگاه ۲", "base_value": 0.8},
    {"code": "RAIN-001", "type": "rain", "location": "ایستگاه هواشناسی مرکزی", "base_value": 0},
    {"code": "PIEZ-001", "type": "piez", "location": "چاه پیزومتر ۱", "base_value": 5.5},
    {"code": "PIEZ-002", "type": "piez", "location": "چاه پیزومتر ۲", "base_value": 7.2},
    {"code": "WEATHER-001", "type": "weather", "location": "ایستگاه هواشناسی", "base_value": 25},
]


def generate_reading(sensor: dict) -> dict:
    """تولید یک خوانش واقع‌گرایانه"""
    sensor_type = sensor["type"]
    base = sensor["base_value"]
    
    # افزودن نویز و روند زمانی
    noise = random.gauss(0, base * 0.05)  # نویز گوسی ۵٪
    daily_cycle = 0.1 * base * (0.5 + 0.5 * (datetime.now().hour / 24))  # سیکل روزانه
    
    if sensor_type == "tdr":
        value = base + noise + daily_cycle
        value = max(5, min(95, value))  # محدود به ۵-۹۵٪
        unit = "%"
        value_secondary = 15 + random.gauss(0, 3)  # دمای خاک
    elif sensor_type == "flume":
        value = base + noise + daily_cycle * 0.5
        value = max(0, value)
        unit = "m3/s"
        value_secondary = None
    elif sensor_type == "rain":
        # بارش به صورت رگباری شبیه‌سازی می‌شود
        if random.random() < 0.1:  # ۱۰٪ احتمال بارش
            value = random.expovariate(1/5)  # توزیع نمایی
        else:
            value = 0
        unit = "mm/hr"
        value_secondary = None
    elif sensor_type == "piez":
        value = base + noise * 0.5
        value = max(0, value)
        unit = "m"
        value_secondary = None
    elif sensor_type == "weather":
        value = base + noise + daily_cycle
        unit = "°C"
        value_secondary = random.uniform(30, 80)  # رطوبت نسبی
    else:
        value = base + noise
        unit = ""
        value_secondary = None
    
    # گاهی اوقات کیفیت داده بد باشد
    quality = "good"
    if random.random() < 0.02:
        quality = "suspicious"
    elif random.random() < 0.005:
        quality = "bad"
    
    return {
        "sensor_code": sensor["code"],
        "sensor_type": sensor_type,
        "location": sensor["location"],
        "value": round(value, 2),
        "value_secondary": round(value_secondary, 2) if value_secondary else None,
        "unit": unit,
        "battery": round(random.uniform(70, 100), 1),
        "rssi": random.randint(-95, -45),
        "quality": quality,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


async def run_simulator():
    """اجرای شبیه‌ساز"""
    print("🎭 Econojin Sensor Simulator")
    print("=" * 60)
    print(f"📡 Broker: {MQTT_BROKER}:{MQTT_PORT}")
    print(f"🔢 Sensors: {len(SENSORS)}")
    print(f"⏱️  Interval: {INTERVAL}s")
    print("=" * 60)
    
    try:
        import aiomqtt
        
        async with aiomqtt.Client(MQTT_BROKER, port=MQTT_PORT) as client:
            print("✅ Connected to MQTT Broker")
            
            while True:
                for sensor in SENSORS:
                    reading = generate_reading(sensor)
                    topic = f"econojin/sensors/{sensor['code']}/data"
                    
                    await client.publish(
                        topic,
                        json.dumps(reading),
                        qos=1
                    )
                    
                    # نمایش در کنسول
                    status = "🟢" if reading["quality"] == "good" else "🟡" if reading["quality"] == "suspicious" else "🔴"
                    print(f"{status} {reading['timestamp'][:19]} | {sensor['code']:12} | {reading['value']:6.2f} {reading['unit']:6} | Bat: {reading['battery']:.0f}%")
                
                await asyncio.sleep(INTERVAL)
                
    except ImportError:
        print("⚠️  aiomqtt not installed. Running in API mode...")
        print("📡 Sending data to FastAPI endpoint instead...")
        
        import httpx
        
        async with httpx.AsyncClient() as http_client:
            while True:
                for sensor in SENSORS:
                    reading = generate_reading(sensor)
                    
                    try:
                        response = await http_client.post(
                            "http://localhost:8000/api/v1/iot/ingest",
                            json=reading,
                            timeout=5.0
                        )
                        
                        status = "🟢" if reading["quality"] == "good" else "🟡"
                        print(f"{status} {reading['timestamp'][:19]} | {sensor['code']:12} | {reading['value']:6.2f} {reading['unit']:6}")
                        
                    except Exception as e:
                        print(f"❌ Error: {e}")
                
                await asyncio.sleep(INTERVAL)
    
    except KeyboardInterrupt:
        print("\n🛑 Simulator stopped")
    except Exception as e:
        print(f"❌ Error: {e}")
        print("💡 Make sure FastAPI is running on localhost:8000")


if __name__ == "__main__":
    try:
        asyncio.run(run_simulator())
    except KeyboardInterrupt:
        print("\n🛑 Simulator stopped by user")
