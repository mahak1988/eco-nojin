# apps/backend-api/app/land_soil_water/schemas.py (افزودن به انتهای فایل)

class FinalizeAnalysisResponse(BaseModel):
    status: AnalysisStatus
    on_chain_requested: bool = False


class ExportMetadata(BaseModel):
    analysis_id: str
    land_unit_id: str
    scenario_type: ScenarioType
    period_start: Optional[date]
    period_end: Optional[date]
    indicators_avg: Dict[IndicatorCode, float]
    generated_at: datetime
    version: str = "1.0.0"
    ldn_reference: Optional[str] = Field(
        default="SDG 15.3.1, UNCCD Good Practice Guidance v2",
        description="ارجاع به راهنمای UNCCD برای گزارش‌ SDG 15.3.1.",
    )