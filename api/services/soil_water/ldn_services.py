"""
Services for Land & Soil-Water module (LDN, indicators, basic analysis).
"""

from typing import Literal, TypedDict, List, Dict, Optional
from dataclasses import dataclass


LDNStatusLiteral = Literal["good", "warning", "critical"]


class LDNStatus(TypedDict):
    status: LDNStatusLiteral
    ldn_index: float
    message: str


class LDNInput(TypedDict):
    soil_organic_carbon: float   # SOC درصد 0-100
    vegetation_cover: float      # پوشش گیاهی درصد 0-100
    erosion_risk: float          # ریسک فرسایش درصد 0-100


class LDNAnalysisResult(TypedDict):
    inputs: LDNInput
    ldn: LDNStatus
    components: Dict[str, float]


@dataclass
class LDNWeights:
    soc_weight: float = 0.4
    vegetation_weight: float = 0.4
    erosion_weight: float = 0.2

    def normalized(self) -> "LDNWeights":
        total = self.soc_weight + self.vegetation_weight + self.erosion_weight
        if total <= 0:
            return LDNWeights(0.4, 0.4, 0.2)
        return LDNWeights(
            soc_weight=self.soc_weight / total,
            vegetation_weight=self.vegetation_weight / total,
            erosion_weight=self.erosion_weight / total,
        )


def _normalize_percentage(value: float) -> float:
    return max(0.0, min(value, 100.0)) / 100.0


def compute_ldn_index(
    soil_organic_carbon: float,
    vegetation_cover: float,
    erosion_risk: float,
    weights: Optional[LDNWeights] = None,
) -> LDNStatus:
    w = (weights or LDNWeights()).normalized()

    soc_norm = _normalize_percentage(soil_organic_carbon)
    veg_norm = _normalize_percentage(vegetation_cover)
    ero_norm = _normalize_percentage(erosion_risk)

    ldn_index = (
        w.soc_weight * soc_norm
        + w.vegetation_weight * veg_norm
        + w.erosion_weight * (1.0 - ero_norm)
    )

    if ldn_index >= 0.7:
        status: LDNStatusLiteral = "good"
        message = "وضعیت سرزمین مطلوب است."
    elif ldn_index >= 0.4:
        status = "warning"
        message = "وضعیت سرزمین در محدوده‌ی هشدار است."
    else:
        status = "critical"
        message = "وضعیت سرزمین بحرانی است و نیاز به مداخله دارد."

    return {
        "status": status,
        "ldn_index": round(ldn_index, 3),
        "message": message,
    }


def analyze_ldn(inputs: LDNInput) -> LDNAnalysisResult:
    soc = _normalize_percentage(inputs["soil_organic_carbon"])
    veg = _normalize_percentage(inputs["vegetation_cover"])
    ero = _normalize_percentage(inputs["erosion_risk"])

    ldn_status = compute_ldn_index(
        soil_organic_carbon=inputs["soil_organic_carbon"],
        vegetation_cover=inputs["vegetation_cover"],
        erosion_risk=inputs["erosion_risk"],
    )

    return {
        "inputs": inputs,
        "ldn": ldn_status,
        "components": {
            "soc_normalized": round(soc, 3),
            "vegetation_normalized": round(veg, 3),
            "erosion_normalized": round(ero, 3),
        },
    }


def batch_analyze_ldn(items: List[LDNInput]) -> Dict[str, object]:
    results: List[LDNAnalysisResult] = []
    indices: List[float] = []

    for item in items:
        res = analyze_ldn(item)
        results.append(res)
        indices.append(res["ldn"]["ldn_index"])

    avg_index = round(sum(indices) / len(indices), 3) if indices else 0.0

    return {
        "count": len(items),
        "average_ldn_index": avg_index,
        "items": results,
    }