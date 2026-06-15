"""LogFrame Service - GCF/GEF IRMF Aligned"""
from typing import List, Dict
from datetime import datetime, timezone
from .models.logframe_models import (
    LogFrameEntry, Indicator, LogFrameLevel, SDGTarget, NDCContribution
)


class LogFrameService:
    """سرویس مدیریت LogFrame منطبق با IRMF GCF/GEF"""
    
    def __init__(self):
        self.logframe: List[LogFrameEntry] = []
        self.indicators: Dict[str, Indicator] = {}
        self._initialize_gcf_gef_logframe()
    
    def _initialize_gcf_gef_logframe(self):
        """مقداردهی اولیه LogFrame مطابق چارچوب GCF/GEF IRMF"""
        
        # ===== IMPACT LEVEL =====
        impact = LogFrameEntry(
            entry_id="IMP-001",
            level=LogFrameLevel.IMPACT,
            statement="گذار به مدیریت یکپارچه و پایدار مناظر خشک‌زار در ایران با ارتقای تاب‌آوری اقلیمی و امنیت معیشتی",
            statement_en="Transition to integrated and sustainable dryland landscape management in Iran with enhanced climate resilience and livelihood security",
            assumptions=[
                "ثبات سیاسی و حمایت سیاستی بلندمدت",
                "همکاری بین‌بخشی دستگاه‌ها",
                "تداوم دسترسی به منابع مالی بین‌المللی"
            ]
        )
        self.logframe.append(impact)
        
        # ===== OUTCOME LEVEL =====
        
        # R1: Water Security
        outcome_r1 = LogFrameEntry(
            entry_id="OUT-R1",
            level=LogFrameLevel.OUTCOME,
            statement="افزایش امنیت آبی پایدار از طریق ارتقای بهره‌وری و توازن در مقیاس منظر و حوضه",
            statement_en="Enhanced sustainable water security through improved efficiency and balance at landscape and watershed scale",
            responsible_entity="وزارت نیرو + وزارت جهاد کشاورزی",
            pilot_sites=["dishmok", "behbahan", "rodbar_talesh", "snow_mountain"]
        )
        
        outcome_r1.indicators = [
            Indicator(
                indicator_id="R1-IND-01",
                name="بهره‌وری آب در تولید کشاورزی",
                name_en="Water Use Efficiency (WUE)",
                level=LogFrameLevel.OUTCOME,
                sdg_targets=[SDGTarget.SDG_6],
                baseline_value=0.8,
                target_value=1.8,
                unit="kg/m3",
                frequency="سالانه",
                data_source="IoT + AquaCrop",
                methodology="FAO-56",
                gef_core=True,
                gcf_core=True
            ),
            Indicator(
                indicator_id="R1-IND-02",
                name="حجم آب ذخیره/صرفه‌جویی‌شده",
                name_en="Volume of water saved/stored",
                level=LogFrameLevel.OUTCOME,
                sdg_targets=[SDGTarget.SDG_6],
                baseline_value=0,
                target_value=5000000,
                unit="m3/year",
                frequency="سالانه",
                data_source="SWAT + IoT",
                methodology="SWAT Model + Flow meters",
                gcf_core=True
            ),
            Indicator(
                indicator_id="R1-IND-03",
                name="شاخص تنش آبی (SDG 6.4.2)",
                name_en="Water Stress Index (SDG 6.4.2)",
                level=LogFrameLevel.OUTCOME,
                sdg_targets=[SDGTarget.SDG_6],
                baseline_value=0.72,
                target_value=0.55,
                unit="ratio",
                frequency="سالانه",
                data_source="WEAP",
                methodology="UN SDG 6.4.2",
                gef_core=True,
                gcf_core=True,
                ndc_aligned=True
            )
        ]
        self.logframe.append(outcome_r1)
        
        # R2: Land/Soil
        outcome_r2 = LogFrameEntry(
            entry_id="OUT-R2",
            level=LogFrameLevel.OUTCOME,
            statement="توقف و معکوس‌سازی تخریب خاک و سرزمین و پیشرفت به‌سوی خنثی‌سازی تخریب سرزمین (LDN)",
            statement_en="Halt and reverse land degradation and progress towards Land Degradation Neutrality (LDN)",
            responsible_entity="سازمان جنگل‌ها + وزارت جهاد",
            pilot_sites=["dishmok", "behbahan", "rodbar_talesh", "snow_mountain"]
        )
        
        outcome_r2.indicators = [
            Indicator(
                indicator_id="R2-IND-01",
                name="کربن آلی خاک (SOC)",
                name_en="Soil Organic Carbon (SOC)",
                level=LogFrameLevel.OUTCOME,
                sdg_targets=[SDGTarget.SDG_15, SDGTarget.SDG_13],
                baseline_value=1.2,
                target_value=2.5,
                unit="percent",
                frequency="دوسالانه",
                data_source="Sentinel-2 + Field sampling",
                methodology="IPCC AFOLU Tier 2",
                gef_core=True,
                gcf_core=True,
                ndc_aligned=True
            ),
            Indicator(
                indicator_id="R2-IND-02",
                name="نرخ فرسایش خاک",
                name_en="Soil erosion rate (RUSLE)",
                level=LogFrameLevel.OUTCOME,
                sdg_targets=[SDGTarget.SDG_15],
                baseline_value=18.5,
                target_value=8.0,
                unit="t/ha/year",
                frequency="سالانه",
                data_source="RUSLE Model",
                methodology="RUSLE + GIS",
                gef_core=True
            ),
            Indicator(
                indicator_id="R2-IND-03",
                name="سطح تحت مدیریت پایدار زمین (SLM/LDN)",
                name_en="Area under SLM/LDN (SDG 15.3.1)",
                level=LogFrameLevel.OUTCOME,
                sdg_targets=[SDGTarget.SDG_15],
                baseline_value=0,
                target_value=26000,
                unit="hectares",
                frequency="سالانه",
                data_source="GIS + Sentinel",
                methodology="UNCCD LDN Indicator",
                gef_core=True,
                gcf_core=True,
                ndc_aligned=True
            )
        ]
        self.logframe.append(outcome_r2)
        
        # R3: Ecosystem
        outcome_r3 = LogFrameEntry(
            entry_id="OUT-R3",
            level=LogFrameLevel.OUTCOME,
            statement="احیای کارکردهای اکوسیستمی و تنوع زیستی در مناظر هدف",
            statement_en="Restoration of ecosystem functions and biodiversity in target landscapes",
            responsible_entity="سازمان محیط زیست",
            pilot_sites=["rodbar_talesh", "snow_mountain"]
        )
        
        outcome_r3.indicators = [
            Indicator(
                indicator_id="R3-IND-01",
                name="شاخص پوشش گیاهی (NDVI)",
                name_en="Vegetation Index (NDVI)",
                level=LogFrameLevel.OUTCOME,
                sdg_targets=[SDGTarget.SDG_15],
                baseline_value=0.25,
                target_value=0.50,
                unit="index",
                frequency="فصلی",
                data_source="Sentinel-2",
                methodology="Remote Sensing",
                gef_core=True
            ),
            Indicator(
                indicator_id="R3-IND-02",
                name="سطح جنگل‌کاری و آگروفارستری",
                name_en="Afforestation/Agroforestry area",
                level=LogFrameLevel.OUTCOME,
                sdg_targets=[SDGTarget.SDG_15, SDGTarget.SDG_13],
                baseline_value=0,
                target_value=5000,
                unit="hectares",
                frequency="سالانه",
                data_source="GIS",
                methodology="FAO FRA",
                ndc_aligned=True
            )
        ]
        self.logframe.append(outcome_r3)
        
        # R4: Livelihoods
        outcome_r4 = LogFrameEntry(
            entry_id="OUT-R4",
            level=LogFrameLevel.OUTCOME,
            statement="تقویت معیشت، امنیت غذایی و تنوع درآمدی جوامع محلی با برابری جنسیتی",
            statement_en="Enhanced livelihoods, food security and income diversity with gender equity",
            responsible_entity="وزارت جهاد + توسعه روستایی",
            pilot_sites=["dishmok", "behbahan", "rodbar_talesh", "snow_mountain"]
        )
        
        outcome_r4.indicators = [
            Indicator(
                indicator_id="R4-IND-01",
                name="درآمد خانوار",
                name_en="Household income",
                level=LogFrameLevel.OUTCOME,
                sdg_targets=[SDGTarget.SDG_2, SDGTarget.SDG_8],
                baseline_value=100,
                target_value=180,
                unit="index (base=100)",
                frequency="سالانه",
                data_source="PRA + Survey",
                methodology="World Bank LSMS",
                gcf_core=True
            ),
            Indicator(
                indicator_id="R4-IND-02",
                name="شاخص امنیت غذایی (FCS)",
                name_en="Food Consumption Score (FCS)",
                level=LogFrameLevel.OUTCOME,
                sdg_targets=[SDGTarget.SDG_2],
                baseline_value=42,
                target_value=65,
                unit="score",
                frequency="سالانه",
                data_source="WFP FCS Survey",
                methodology="WFP FCS",
                gcf_core=True
            ),
            Indicator(
                indicator_id="R4-IND-03",
                name="تنوع معیشت (Simpson Index)",
                name_en="Livelihood Diversity (Simpson Index)",
                level=LogFrameLevel.OUTCOME,
                sdg_targets=[SDGTarget.SDG_8],
                baseline_value=0.35,
                target_value=0.65,
                unit="index",
                frequency="سالانه",
                data_source="Survey",
                methodology="Simpson Diversity Index",
                gef_core=True
            ),
            Indicator(
                indicator_id="R4-IND-04",
                name="زنان ذی‌نفع در پروژه",
                name_en="Women beneficiaries",
                level=LogFrameLevel.OUTCOME,
                sdg_targets=[SDGTarget.SDG_8],
                baseline_value=0,
                target_value=2560,
                unit="women",
                frequency="سالانه",
                data_source="Project records",
                methodology="GCF Gender Policy",
                gcf_core=True
            )
        ]
        self.logframe.append(outcome_r4)
        
        # R5: Carbon & Climate
        outcome_r5 = LogFrameEntry(
            entry_id="OUT-R5",
            level=LogFrameLevel.OUTCOME,
            statement="افزایش ترسیب کربن و کاهش شدت انتشار هم‌سو با NDC و SDG 13",
            statement_en="Increased carbon sequestration and reduced emission intensity aligned with NDC and SDG 13",
            responsible_entity="سازمان محیط زیست + وزارت نیرو",
            pilot_sites=["dishmok", "behbahan", "rodbar_talesh", "snow_mountain"]
        )
        
        outcome_r5.indicators = [
            Indicator(
                indicator_id="R5-IND-01",
                name="ترسیب کربن (tCO2e)",
                name_en="Carbon sequestered (tCO2e)",
                level=LogFrameLevel.OUTCOME,
                sdg_targets=[SDGTarget.SDG_13],
                baseline_value=0,
                target_value=500000,
                unit="tCO2e/year",
                frequency="سالانه",
                data_source="IPCC AFOLU Tier 2",
                methodology="IPCC 2019 Refinement",
                gef_core=True,
                gcf_core=True,
                ndc_aligned=True
            ),
            Indicator(
                indicator_id="R5-IND-02",
                name="خانوارهای تاب‌آور به اقلیم",
                name_en="Climate-resilient households",
                level=LogFrameLevel.OUTCOME,
                sdg_targets=[SDGTarget.SDG_13],
                baseline_value=0,
                target_value=6955,
                unit="households",
                frequency="سالانه",
                data_source="Survey",
                methodology="GCF Adaptation Indicator",
                gcf_core=True,
                ndc_aligned=True
            )
        ]
        self.logframe.append(outcome_r5)
        
        # R6: Governance
        outcome_r6 = LogFrameEntry(
            entry_id="OUT-R6",
            level=LogFrameLevel.OUTCOME,
            statement="ارتقای حکمرانی چندسطحی و مشارکتی برای مدیریت پایدار منظر",
            statement_en="Enhanced multi-level participatory governance for sustainable landscape management",
            responsible_entity="کمیته راهبری ملی",
            pilot_sites=["dishmok", "behbahan", "rodbar_talesh", "snow_mountain"]
        )
        
        outcome_r6.indicators = [
            Indicator(
                indicator_id="R6-IND-01",
                name="کارگروه‌های محلی فعال",
                name_en="Active local working groups",
                level=LogFrameLevel.OUTCOME,
                sdg_targets=[SDGTarget.SDG_8],
                baseline_value=0,
                target_value=48,
                unit="groups",
                frequency="فصلی",
                data_source="Project records",
                methodology="GCF Stakeholder Engagement",
                gcf_core=True
            )
        ]
        self.logframe.append(outcome_r6)
    
    def get_logframe(self) -> Dict:
        """دریافت LogFrame کامل"""
        return {
            "total_entries": len(self.logframe),
            "impact": len([e for e in self.logframe if e.level == LogFrameLevel.IMPACT]),
            "outcomes": len([e for e in self.logframe if e.level == LogFrameLevel.OUTCOME]),
            "entries": [
                {
                    "entry_id": e.entry_id,
                    "level": e.level.value,
                    "statement": e.statement,
                    "statement_en": e.statement_en,
                    "indicators_count": len(e.indicators),
                    "pilot_sites": e.pilot_sites
                }
                for e in self.logframe
            ]
        }
    
    def get_indicators_by_sdg(self, sdg: str) -> List[Dict]:
        """دریافت شاخص‌ها بر اساس SDG"""
        sdg_map = {
            "2": SDGTarget.SDG_2,
            "6": SDGTarget.SDG_6,
            "8": SDGTarget.SDG_8,
            "13": SDGTarget.SDG_13,
            "15": SDGTarget.SDG_15
        }
        
        target = sdg_map.get(sdg)
        if not target:
            return []
        
        result = []
        for entry in self.logframe:
            for ind in entry.indicators:
                if target in ind.sdg_targets:
                    result.append({
                        "indicator_id": ind.indicator_id,
                        "name": ind.name,
                        "name_en": ind.name_en,
                        "baseline": ind.baseline_value,
                        "target": ind.target_value,
                        "unit": ind.unit,
                        "gef_core": ind.gef_core,
                        "gcf_core": ind.gcf_core,
                        "ndc_aligned": ind.ndc_aligned
                    })
        
        return result
    
    def get_gef_core_indicators(self) -> List[Dict]:
        """دریافت شاخص‌های Core GEF"""
        result = []
        for entry in self.logframe:
            for ind in entry.indicators:
                if ind.gef_core:
                    result.append({
                        "indicator_id": ind.indicator_id,
                        "name": ind.name,
                        "name_en": ind.name_en,
                        "baseline": ind.baseline_value,
                        "target": ind.target_value,
                        "unit": ind.unit,
                        "methodology": ind.methodology
                    })
        return result
    
    def get_gcf_core_indicators(self) -> List[Dict]:
        """دریافت شاخص‌های Core GCF"""
        result = []
        for entry in self.logframe:
            for ind in entry.indicators:
                if ind.gcf_core:
                    result.append({
                        "indicator_id": ind.indicator_id,
                        "name": ind.name,
                        "name_en": ind.name_en,
                        "baseline": ind.baseline_value,
                        "target": ind.target_value,
                        "unit": ind.unit,
                        "methodology": ind.methodology
                    })
        return result
    
    def generate_ndc_report(self, project_id: str, year: int) -> Dict:
        """تولید گزارش NDC برای UNFCCC"""
        total_mitigation = 0
        total_beneficiaries = 0
        
        for entry in self.logframe:
            for ind in entry.indicators:
                if ind.ndc_aligned:
                    if "tCO2e" in ind.unit:
                        total_mitigation += ind.target_value
                    elif "households" in ind.unit:
                        total_beneficiaries += int(ind.target_value)
        
        return {
            "project_id": project_id,
            "reporting_year": year,
            "sector": "AFOLU",
            "methodology": "IPCC AFOLU Tier 2",
            "mitigation_contribution": {
                "total_tCO2e": total_mitigation,
                "per_year": total_mitigation / 10,
                "sectors": ["Soil Carbon", "Biomass", "Agroforestry"]
            },
            "adaptation_contribution": {
                "beneficiaries": total_beneficiaries,
                "women_beneficiaries": 2560,
                "resilient_livelihoods": 6955
            },
            "co_benefits": {
                "sdgs_addressed": ["SDG 2", "SDG 6", "SDG 8", "SDG 13", "SDG 15"],
                "ldn_contribution_ha": 26000,
                "water_saved_m3": 5000000
            },
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "status": "ready_for_unfccc_submission"
        }
