"""
Executor Agent واقعی برای Econojin
ابزارهای Domain-Specific را بر اساس نوع task اجرا می‌کند
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from typing import Dict, Any, Optional, List
import structlog
import asyncio

from agents.core.planner_agent import Task
from agents.tools import (
    OpenMeteoTool, GEENdviTool, RUSLETool, AquaCropTool,
    SoilGridsTool, ToolResult, get_tool
)
from agents.policies.policy_engine import PolicyEngine, PolicyAction

logger = structlog.get_logger()


class ExecutorAgent:
    """ایجنت اجرای واقعی ابزارهای Domain-Specific"""

    # نگاشت ابزارها به کلمات کلیدی در task (fallback)
    TOOL_KEYWORDS = {
        "gee_ndvi": ["ndvi", "پوشش گیاهی", "ماهواره", "sentinel", "شاخص گیاهی", "vegetation"],
        "open_meteo": ["هوا", "بارش", "دما", "weather", "rainfall", "temperature", "آب و هوا", "اقلیم"],
        "rusle": ["فرسایش", "erosion", "خاک", "شیب", "sediment"],
        "aquacrop": ["محصول", "crop", "عملکرد", "yield", "گندم", "wheat", "کشت"],
        "soil_grids": ["خاک", "soil", "بافت", "کربن", "ph"]
    }

    # موقعیت‌های پیش‌فرض برای مناطق ایران
    DEFAULT_LOCATIONS = {
        "خراسان": {"lat": 36.2972, "lon": 59.6067},
        "مشهد": {"lat": 36.2972, "lon": 59.6067},
        "گرگان": {"lat": 36.8389, "lon": 54.4347},
        "تهران": {"lat": 35.6892, "lon": 51.3890},
        "اصفهان": {"lat": 32.6546, "lon": 51.6680},
        "شیراز": {"lat": 29.5916, "lon": 52.5837},
    }

    def __init__(self):
        self.policy_engine = PolicyEngine()
        self.logger = logger.bind(agent="executor")
        self.tools = {
            "open_meteo": OpenMeteoTool(),
            "gee_ndvi": GEENdviTool(),
            "rusle": RUSLETool(),
            "aquacrop": AquaCropTool(),
            "soil_grids": SoilGridsTool()
        }

    def _detect_location(self, text: str) -> Dict[str, float]:
        """تشخیص موقعیت جغرافیایی از متن"""
        text_lower = text.lower()
        for name, coords in self.DEFAULT_LOCATIONS.items():
            if name in text or name in text_lower:
                return coords
        return {"lat": 35.6892, "lon": 51.3890}  # تهران پیش‌فرض

    def _detect_tools(self, task: Task) -> List[str]:
        """تشخیص ابزارهای مورد نیاز بر اساس شرح task (fallback)"""
        desc = task.description.lower()
        detected = []

        for tool_name, keywords in self.TOOL_KEYWORDS.items():
            for keyword in keywords:
                if keyword.lower() in desc:
                    detected.append(tool_name)
                    break

        return detected or ["open_meteo"]

    async def execute_task(self, task: Task, user_request: str,
                           context: List[Dict] = None) -> ToolResult:
        """اجرای یک task با ابزارهای مرتبط"""

        location = self._detect_location(user_request)

        # اولویت ۱: استفاده از required_tools تعیین شده توسط Planner
        if task.required_tools:
            tool_names = [t for t in task.required_tools if t in self.tools]
            self.logger.info("using_planner_tools", tools=tool_names)
        else:
            # اولویت ۲: تشخیص خودکار از description
            tool_names = self._detect_tools(task)

        self.logger.info("executing_task",
                         task_id=task.id,
                         tools=tool_names,
                         location=location)

        results = {}
        for tool_name in tool_names:
            # بررسی Policy
            action = self.policy_engine.validate_tool_call(
                tool_name,
                {"task": task.description, "location": location}
            )

            if action == PolicyAction.DENY:
                self.logger.warning("tool_blocked_by_policy", tool=tool_name)
                results[tool_name] = {
                    "success": False,
                    "error": "Blocked by policy"
                }
                continue

            # اجرای ابزار با پارامترهای مناسب
            tool = self.tools[tool_name]

            try:
                if tool_name == "open_meteo":
                    result = tool.execute(
                        latitude=location["lat"],
                        longitude=location["lon"],
                        days=30,
                        historical=True
                    )
                elif tool_name == "gee_ndvi":
                    result = tool.execute(
                        latitude=location["lat"],
                        longitude=location["lon"],
                        ecosystem="cropland"
                    )
                elif tool_name == "rusle":
                    rainfall = 250
                    if "open_meteo" in results and results["open_meteo"].get("success"):
                        try:
                            precip = results["open_meteo"]["data"]["weather"]["precipitation_sum"]
                            rainfall = sum(precip) * 12
                        except:
                            pass

                    result = tool.execute(
                        annual_rainfall_mm=rainfall,
                        slope_percent=8,
                        soil_type="loam",
                        land_cover="cropland"
                    )
                elif tool_name == "aquacrop":
                    rainfall = 250
                    if "open_meteo" in results and results["open_meteo"].get("success"):
                        try:
                            precip = results["open_meteo"]["data"]["weather"]["precipitation_sum"]
                            rainfall = sum(precip) * 12
                        except:
                            pass

                    result = tool.execute(
                        crop="wheat",
                        rainfall_mm=rainfall,
                        temperature_avg=18
                    )
                elif tool_name == "soil_grids":
                    result = tool.execute(
                        latitude=location["lat"],
                        longitude=location["lon"]
                    )
                else:
                    continue

                results[tool_name] = {
                    "success": result.success,
                    "data": result.data,
                    "error": result.error,
                    "execution_time_ms": result.execution_time_ms
                }

                self.logger.info("tool_executed",
                                 tool=tool_name,
                                 success=result.success,
                                 exec_ms=round(result.execution_time_ms, 2))

            except Exception as e:
                self.logger.error("tool_error", tool=tool_name, error=str(e))
                results[tool_name] = {
                    "success": False,
                    "error": str(e)
                }

        # خلاصه‌سازی نتایج
        summary = self._summarize_results(task, results, location)

        return ToolResult(
            success=all(r.get("success", False) for r in results.values()),
            tool_name="executor_aggregate",
            data={
                "task_id": task.id,
                "task_description": task.description,
                "location": location,
                "tools_used": tool_names,
                "results": results,
                "summary": summary
            }
        )

    def _summarize_results(self, task: Task, results: Dict, location: Dict) -> str:
        """تولید خلاصه فارسی از نتایج"""
        parts = []

        if "open_meteo" in results and results["open_meteo"].get("success"):
            w = results["open_meteo"]["data"]["weather"]
            if "precipitation_sum" in w:
                total_rain = sum(w["precipitation_sum"])
                parts.append(f"📊 مجموع بارش ۳۰ روز گذشته: {total_rain:.1f} میلی‌متر")

        if "gee_ndvi" in results and results["gee_ndvi"].get("success"):
            ndvi = results["gee_ndvi"]["data"]
            parts.append(f"🛰️ شاخص پوشش گیاهی (NDVI): {ndvi['ndvi']['average']} - وضعیت {ndvi['health_fa']}")

        if "rusle" in results and results["rusle"].get("success"):
            r = results["rusle"]["data"]
            parts.append(f"🌍 نرخ فرسایش خاک: {r['erosion_rate_t_ha_y']} تن/هکتار/سال ({r['severity_fa']})")
            for rec in r.get("recommendations", []):
                parts.append(f"💡 {rec}")

        if "aquacrop" in results and results["aquacrop"].get("success"):
            a = results["aquacrop"]["data"]
            parts.append(f"🌾 عملکرد پیش‌بینی‌شده {a['crop']}: {a['yield_t_ha']} تن/هکتار")
            parts.append(f"💧 نیاز به آبیاری: {a['irrigation_needed_mm']} میلی‌متر")

        if "soil_grids" in results and results["soil_grids"].get("success"):
            s = results["soil_grids"]["data"]
            parts.append(f"🔬 بافت خاک: {s['soil_type']}, pH: {s['ph']}, کربن آلی: {s['organic_carbon_pct']}%")

        return "\n".join(parts) if parts else "نتیجه‌ای تولید نشد"


async def test_executor():
    """تست Executor واقعی"""
    print("\n" + "="*70)
    print("🤖 تست Executor Agent واقعی - Econojin")
    print("="*70 + "\n")

    executor = ExecutorAgent()

    task = Task(
        id="task_ndvi",
        description="تحلیل داده‌های ماهواره‌ای NDVI و هواشناسی برای منطقه خراسان",
        priority=5,
        dependencies=[],
        estimated_time=15,
        required_tools=["gee_ndvi", "open_meteo", "soil_grids"]
    )

    user_request = "تحلیل داده‌های ماهواره‌ای NDVI برای منطقه خراسان در ۶ ماه گذشته"

    print(f"📝 درخواست کاربر: {user_request}\n")
    print(f"🎯 Task: {task.description}\n")

    result = await executor.execute_task(task, user_request)

    print("="*70)
    print("📊 نتایج اجرای Executor:")
    print("="*70)

    if result.success:
        data = result.data
        print(f"\n📍 موقعیت تشخیص‌داده‌شده: {data['location']}")
        print(f"🛠️ ابزارهای استفاده‌شده: {', '.join(data['tools_used'])}")
        print(f"\n{data['summary']}")
    else:
        print(f"❌ خطا در اجرا")

    print("\n" + "="*70)


if __name__ == "__main__":
    asyncio.run(test_executor())