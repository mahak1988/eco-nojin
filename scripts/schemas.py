"""
Pydantic schemas برای Econojin API
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class RegionEnum(str, Enum):
    khorasan = "خراسان"
    mashhad = "مشهد"
    gorgan = "گرگان"
    tehran = "تهران"
    isfahan = "اصفهان"
    shiraz = "شیراز"


class AnalysisRequest(BaseModel):
    """درخواست تحلیل"""

    query: str = Field(..., min_length=5, max_length=500, description="درخواست کاربر به زبان طبیعی")
    region: RegionEnum = Field(default=RegionEnum.khorasan, description="منطقه جغرافیایی")
    include_tools: List[str] = Field(
        default=["gee_ndvi", "open_meteo", "soil_grids", "rusle", "aquacrop"],
        description="ابزارهای مورد استفاده",
    )

    class Config:
        json_schema_extra = {
            "example": {
                "query": "تحلیل داده‌های ماهواره‌ای NDVI برای منطقه خراسان در ۶ ماه گذشته",
                "region": "خراسان",
                "include_tools": ["gee_ndvi", "open_meteo", "soil_grids"],
            }
        }


class NodeStatus(str, Enum):
    started = "started"
    completed = "completed"
    failed = "failed"
    skipped = "skipped"


class StreamEvent(BaseModel):
    """رویداد streaming برای WebSocket"""

    event_type: str  # node_start, node_complete, tool_executed, final
    node_name: Optional[str] = None
    status: NodeStatus = NodeStatus.completed
    data: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.now)
    message: Optional[str] = None


class TaskResult(BaseModel):
    """نتیجه یک task"""

    task_id: str
    description: str
    status: str
    output: str
    tools_used: List[str] = []
    location: Optional[Dict[str, float]] = None
    execution_time_ms: float = 0.0


class AnalysisResponse(BaseModel):
    """پاسخ نهایی تحلیل"""

    session_id: str
    request: AnalysisRequest
    summary: Dict[str, Any]
    tasks: List[TaskResult]
    final_response: str
    quality_score: float
    total_execution_time_ms: float
    timestamp: datetime = Field(default_factory=datetime.now)


class ErrorResponse(BaseModel):
    """پاسخ خطا"""

    error: str
    detail: str
    session_id: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)
