"""ایجنت برنامه‌ریز: وظایف پیچیده را به subtasks تقسیم می‌کند"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

import asyncio
from typing import Any, Dict, List

import structlog
from pydantic import BaseModel, Field

logger = structlog.get_logger()


class Task(BaseModel):
    id: str
    description: str
    priority: int = Field(ge=1, le=5)
    dependencies: List[str] = []
    estimated_time: int
    required_tools: List[str] = []  # ابزارهای لازم برای این task


class PlannerAgent:
    """ایجنت برنامه‌ریز با قابلیت تشخیص ابزار"""

    def __init__(self, model_name: str = "gpt-4o-mini"):
        self.model_name = model_name
        self.logger = logger.bind(agent="planner")

    async def plan(self, user_request: str, context: Dict[str, Any] = None) -> List[Task]:
        """تقسیم درخواست کاربر به وظایف با ابزارهای مشخص"""
        self.logger.info("starting_planning", request=user_request[:100])

        # TODO: در آینده با LLM واقعی جایگزین می‌شود
        # فعلاً یک پلن هوشمند بر اساس کلمات کلیدی درخواست
        request_lower = user_request.lower()

        tasks = []

        # Task 1: تحلیل اولیه درخواست + پوشش گیاهی
        if any(kw in user_request for kw in ["ndvi", "پوشش گیاهی", "ماهواره", "sentinel"]):
            tasks.append(
                Task(
                    id="task_ndvi_analysis",
                    description="تحلیل شاخص پوشش گیاهی NDVI و شرایط خاک منطقه",
                    priority=5,
                    dependencies=[],
                    estimated_time=5,
                    required_tools=["gee_ndvi", "open_meteo", "soil_grids"],
                )
            )
        else:
            tasks.append(
                Task(
                    id="task_initial_analysis",
                    description="تحلیل اولیه درخواست کاربر و شرایط هواشناسی",
                    priority=5,
                    dependencies=[],
                    estimated_time=5,
                    required_tools=["open_meteo"],
                )
            )

        # Task 2: جمع‌آوری داده‌های محیطی
        if any(kw in user_request for kw in ["فرسایش", "خاک", "شیب", "rusle"]):
            tasks.append(
                Task(
                    id="task_erosion",
                    description="محاسبه نرخ فرسایش خاک با مدل RUSLE و ویژگی‌های خاک",
                    priority=4,
                    dependencies=["task_ndvi_analysis"],
                    estimated_time=10,
                    required_tools=["rusle", "soil_grids", "open_meteo"],
                )
            )
        else:
            tasks.append(
                Task(
                    id="task_data_collection",
                    description="جمع‌آوری داده‌های هواشناسی و محیطی منطقه برای تحلیل",
                    priority=4,
                    dependencies=[tasks[0].id],
                    estimated_time=10,
                    required_tools=["open_meteo", "soil_grids"],
                )
            )

        # Task 3: تحلیل پیشرفته و پیش‌بینی
        if any(kw in user_request for kw in ["محصول", "گندم", "کشت", "عملکرد", "aquacrop"]):
            tasks.append(
                Task(
                    id="task_crop_yield",
                    description="پیش‌بینی عملکرد محصول با مدل AquaCrop و تحلیل نیاز آبی",
                    priority=3,
                    dependencies=[tasks[1].id],
                    estimated_time=15,
                    required_tools=["aquacrop", "open_meteo"],
                )
            )
        else:
            tasks.append(
                Task(
                    id="task_final_analysis",
                    description="اجرای محاسبات پیشرفته و تحلیل جامع نتایج",
                    priority=3,
                    dependencies=[tasks[1].id],
                    estimated_time=15,
                    required_tools=["rusle", "aquacrop", "open_meteo"],
                )
            )

        self.logger.info("planning_complete", task_count=len(tasks))
        return tasks


async def main():
    planner = PlannerAgent()

    test_requests = [
        "تحلیل داده‌های ماهواره‌ای NDVI برای منطقه خراسان در ۶ ماه گذشته",
        "آیا منطقه گرگان برای کشت گندم مناسب است؟",
        "بررسی فرسایش خاک در دشت مشهد",
    ]

    for req in test_requests:
        print(f"\n📝 Request: {req}")
        tasks = await planner.plan(req)
        print("📋 Generated Tasks:")
        for t in tasks:
            print(f"  [{t.priority}] {t.id}: {t.description}")
            print(f"      🛠️ Tools: {', '.join(t.required_tools)}")


if __name__ == "__main__":
    asyncio.run(main())
