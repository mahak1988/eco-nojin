"""Psychology Domain Service."""
from datetime import datetime
from .repositories.psychology_repository import PsychologyRepository
from .models.psychology_models import TestResult


class PsychologyService:
    def __init__(self, repository: PsychologyRepository):
        self.repo = repository
    
    async def score_test(
        self,
        test_id: str,
        answers: list
    ) -> float:
        """نمره‌دهی به تست"""
        return sum(answers) / len(answers)
    
    async def interpret_result(
        self,
        score: float
    ) -> dict:
        """تفسیر نتیجه"""
        if score < 3:
            return {
                "interpretation": "LOW",
                "recommendations": ["نیاز به حمایت بیشتر", "مشاوره تخصصی"]
            }
        elif score < 7:
            return {
                "interpretation": "MODERATE",
                "recommendations": ["پایش منظم", "فعالیت‌های تقویتی"]
            }
        else:
            return {
                "interpretation": "HIGH",
                "recommendations": ["حفظ وضعیت فعلی", "پیشگیری"]
            }
    
    async def submit_test(
        self,
        user_id: str,
        test_id: str,
        answers: list
    ) -> dict:
        """ثبت و تحلیل تست"""
        score = await self.score_test(test_id, answers)
        interpretation = await self.interpret_result(score)
        
        return {
            "user_id": user_id,
            "test_id": test_id,
            "score": score,
            "interpretation": interpretation["interpretation"],
            "recommendations": interpretation["recommendations"],
            "timestamp": datetime.now().isoformat()
        }
