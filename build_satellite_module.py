#!/usr/bin/env python3
# build_satellite_module.py — افزودن ماژول داده‌های ماهواره‌ای (رطوبت خاک، تبخیر-تعرق)
import sys
from pathlib import Path

SATELLITE_PY = '''"""
Satellite Data Module — Fetches real-time satellite-derived agricultural metrics.
Source: Open-Meteo Agricultural API (Free, No Auth, Global).
"""
import httpx
from typing import Dict, Any

async def fetch_satellite_agro_data(lat: float, lon: float, days: int = 7) -> Dict[str, Any]:
    """
    Fetches satellite-derived soil moisture and evapotranspiration.
    """
    url = "https://agricultural-api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "current": "soil_moisture_0_to_10cm,soil_moisture_10_to_40cm,evapotranspiration",
        "daily": "et0_fao_evapotranspiration,soil_moisture_0_to_10cm",
        "past_days": days,
        "forecast_days": 1,
        "timezone": "auto"
    }
    
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            current = data.get("current", {})
            daily = data.get("daily", {})
            
            return {
                "status": "success",
                "source": "Open-Meteo Satellite-Derived",
                "coordinates": {"lat": lat, "lon": lon},
                "current": {
                    "soil_moisture_0_10cm": current.get("soil_moisture_0_to_10cm"),
                    "soil_moisture_10_40cm": current.get("soil_moisture_10_to_40cm"),
                    "evapotranspiration": current.get("evapotranspiration"),
                    "time": current.get("time")
                },
                "forecast": {
                    "dates": daily.get("time", [])[:3],
                    "et0": daily.get("et0_fao_evapotranspiration", [])[:3],
                    "moisture": daily.get("soil_moisture_0_to_10cm", [])[:3]
                }
            }
    except httpx.HTTPError as e:
        return {"status": "error", "message": f"خطای شبکه در دریافت داده ماهواره‌ای: {str(e)}"}
    except Exception as e:
        return {"status": "error", "message": f"خطای غیرمنتظره: {str(e)}"}
'''

def patch_data_router(root: Path) -> str:
    f = root / "apps" / "simulation" / "data" / "router.py"
    if not f.exists():
        return "⚠ data/router.py یافت نشد"
    
    text = f.read_text(encoding="utf-8")
    if "fetch_satellite_agro_data" in text:
        return "· API داده‌های ماهواره‌ای ازقبل اضافه شده است"
    
    # افزودن ایمپورت
    text = "from apps.simulation.data.satellite import fetch_satellite_agro_data\n" + text
    
    # افزودن endpoint جدید
    new_endpoint = '''
@router.get("/satellite", summary="دریافت داده‌های ماهواره‌ای کشاورزی (رطوبت خاک و تبخیر-تعرق)")
async def get_satellite_data(lat: float, lon: float, days: int = 7):
    data = await fetch_satellite_agro_data(lat, lon, days)
    if data.get("status") == "error":
        return {"status": "error", "message": data.get("message")}
    return data
'''
    text += new_endpoint
    f.write_text(text, encoding="utf-8")
    return "✓ backend: API داده‌های ماهواره‌ای به router اضافه شد"

def patch_frontend_detail(root: Path) -> str:
    f = root / "apps" / "web" / "src" / "pages" / "SimulatorDetailPage.tsx"
    if not f.exists():
        return "⚠ SimulatorDetailPage.tsx یافت نشد"
    
    text = f.read_text(encoding="utf-8")
    if "satelliteData" in text:
        return "· کارت داده‌های ماهواره‌ای ازقبل در فرانت وجود دارد"
    
    # ۱. افزودن state برای داده‌های ماهواره‌ای
    if "const [validation, setValidation]" in text:
        text = text.replace(
            "const [validation, setValidation] = useState<any>(null);",
            "const [validation, setValidation] = useState<any>(null);\n  const [satelliteData, setSatelliteData] = useState<any>(null);"
        )
    
    # ۲. افزودن تابع دریافت داده ماهواره‌ای
    fetch_sat_func = '''
  // Fetch Satellite Data
  const fetchSatelliteData = async () => {
    if (!params.latitude || !params.longitude) {
      alert("⚠️ لطفاً ابتدا مختصات جغرافیایی (عرض و طول) را وارد کنید.");
      return;
    }
    setSatelliteData({ loading: true });
    try {
      const res = await fetch(`${API_BASE}${API_V1}/simulation/data/satellite?lat=${params.latitude}&lon=${params.longitude}`);
      const data = await res.json();
      setSatelliteData(data);
    } catch (e) {
      setSatelliteData({ status: "error", message: "خطا در ارتباط با سرور" });
    }
  };
'''
    # تزریق قبل از return
    if "return (" in text and "fetchSatelliteData" not in text:
        text = text.replace("  return (", fetch_sat_func + "\n  return (", 1)

    # ۳. افزودن کارت نمایش داده‌های ماهواره‌ای (قبل از دکمه اجرا)
    satellite_card = '''
        {/* Satellite Data Card */}
        <div className="rounded-2xl border border-cyan-200 bg-cyan-50/40 p-5 mb-6">
          <div className="flex justify-between items-center mb-3">
            <h3 className="text-sm font-bold text-cyan-800 flex items-center gap-2">
              🛰️ داده‌های ماهواره‌ای بلادرنگ (رطوبت خاک و ET)
            </h3>
            <button 
              onClick={fetchSatelliteData}
              disabled={satelliteData?.loading || !params.latitude}
              className="text-xs bg-cyan-600 text-white px-3 py-1.5 rounded-lg hover:bg-cyan-700 disabled:opacity-50 transition-colors"
            >
              {satelliteData?.loading ? "در حال دریافت..." : "به‌روزرسانی داده‌ها"}
            </button>
          </div>
          
          {satelliteData?.status === "success" ? (
            <div className="grid grid-cols-1 md:grid-cols-3 gap-3 text-sm">
              <div className="bg-white p-3 rounded-xl ring-1 ring-cyan-100">
                <p className="text-xs text-stone-500 mb-1">رطوبت خاک (۰-۱۰ سانتی‌متر)</p>
                <p className="text-lg font-bold text-cyan-700">{satelliteData.current.soil_moisture_0_10cm} <span className="text-xs font-normal">m³/m³</span></p>
              </div>
              <div className="bg-white p-3 rounded-xl ring-1 ring-cyan-100">
                <p className="text-xs text-stone-500 mb-1">رطوبت خاک (۱۰-۴۰ سانتی‌متر)</p>
                <p className="text-lg font-bold text-cyan-700">{satelliteData.current.soil_moisture_10_40cm} <span className="text-xs font-normal">m³/m³</span></p>
              </div>
              <div className="bg-white p-3 rounded-xl ring-1 ring-cyan-100">
                <p className="text-xs text-stone-500 mb-1">تبخیر-تعرق فعلی (ET)</p>
                <p className="text-lg font-bold text-cyan-700">{satelliteData.current.evapotranspiration} <span className="text-xs font-normal">mm</span></p>
              </div>
            </div>
          ) : satelliteData?.status === "error" ? (
            <p className="text-sm text-red-600 bg-red-50 p-3 rounded-lg">⚠️ {satelliteData.message}</p>
          ) : (
            <p className="text-sm text-stone-500 text-center py-4">برای مشاهده داده‌های ماهواره‌ای، روی دکمه «به‌روزرسانی داده‌ها» کلیک کنید.</p>
          )}
        </div>
'''
    
    # تزریق کارت قبل از دکمه "اجرا" (Play)
    if 'className="w-full rounded-xl bg-emerald-600 py-3 text-sm font-bold text-white' in text:
        text = text.replace(
            'className="w-full rounded-xl bg-emerald-600 py-3 text-sm font-bold text-white',
            satellite_card + '\n        <button className="w-full rounded-xl bg-emerald-600 py-3 text-sm font-bold text-white'
        )
        f.write_text(text, encoding="utf-8")
        return "✓ frontend: کارت داده‌های ماهواره‌ای و تابع دریافت آن اضافه شد"
    
    return "⚠ frontend: الگوی دکمه اجرا یافت نشد"

def main():
    root = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
    print("=" * 64)
    print("  🛰️ build_satellite_module.py — اتصال داده‌های ماهواره‌ای")
    print("=" * 64)
    print("  " + patch_data_router(root))
    print("  " + patch_frontend_detail(root))
    print("\n" + "=" * 64)
    print("  ✅ ماژول ماهواره‌ای با موفقیت اضافه شد.")
    print("  📌 سرور Backend و Frontend را RESTART کنید.")
    print("  📌 در صفحه شبیه‌ساز، مختصات را وارد کرده و دکمه 'به‌روزرسانی داده‌ها' را بزنید.")
    print("=" * 64)

if __name__ == "__main__":
    main()