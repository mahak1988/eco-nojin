import logging

logger = logging.getLogger(__name__)
from typing import Any


def generate_advisory(
    simulator_id: str, metrics: dict[str, Any], parameters: dict[str, Any]
) -> dict[str, Any]:
    """
    Main entry point for generating advisory content.
    """
    analysis = ""
    recommendations = []
    scenarios = []
    references = []
    tek_insights = []

    if simulator_id == "rothc":
        final_soc = metrics.get("final_soc", 0)
        total_sequestered = metrics.get("total_sequestered", 0)
        annual_rate = total_sequestered / max(1, parameters.get("years", 5))

        analysis = f"Soil organic carbon changed to {final_soc:.2f} t/ha. Total sequestration: {total_sequestered:.2f} t/ha over the simulation period. "
        if annual_rate > 2.0:
            analysis += (
                "Excellent carbon sequestration rate. Soil qualifies for carbon credit programs."
            )
            recommendations.append(
                {
                    "level": "success",
                    "icon": "leaf",
                    "text": f"Annual sequestration rate of {annual_rate:.2f} t/ha/yr is excellent. Eligible for carbon credit certification under Verra VM0042 methodology.",
                    "source": "Coleman K. & Jenkinson D.S. (2014). RothC-26.3 Model.",
                }
            )
        elif annual_rate < 0.5:
            analysis += "Carbon sequestration rate is low. Consider increasing crop residues or adding compost."
            recommendations.append(
                {
                    "level": "warning",
                    "icon": "alert-triangle",
                    "text": f"Low sequestration rate ({annual_rate:.2f} t/ha/yr). Increase crop residue retention or apply compost (5-10 t/ha).",
                    "source": "FAO (2019). Measuring and Modelling Soil Carbon Stocks.",
                }
            )
        else:
            analysis += "Moderate carbon sequestration. Additional organic inputs could improve rates further."
            recommendations.append(
                {
                    "level": "info",
                    "icon": "info",
                    "text": "Moderate sequestration. Consider biochar application (Terra Preta method) for long-term carbon storage.",
                    "source": "Lehmann J. et al. (2006). Biochar sequestration in terrestrial ecosystems.",
                }
            )

        scenarios = [
            {
                "id": "increase_residue",
                "name": "Increase Crop Residue Retention",
                "desc": "Increase carbon input by 50% through residue retention",
                "params": {"carbon_input": parameters.get("carbon_input", 3.5) * 1.5},
            },
            {
                "id": "add_biochar",
                "name": "Add Biochar (Terra Preta Method)",
                "desc": "Apply 10 t/ha biochar for long-term carbon storage",
                "params": {"carbon_input": parameters.get("carbon_input", 3.5) + 2.0},
            },
        ]
        references = [
            "Coleman K. & Jenkinson D.S. (2014). RothC-26.3 - A Model for the Turnover of Carbon in Soil. Rothamsted Research.",
            "Lehmann J. et al. (2006). Biochar sequestration in terrestrial ecosystems - A review. Mitigation and Adaptation Strategies for Global Change.",
        ]

        # TEK insights for RothC
        if final_soc < 30:
            tek_insights = [
                {
                    "pattern_id": "terra_preta",
                    "name": "Terra Preta - Amazonian Dark Earths",
                    "relevance": "High",
                    "insight": "Amazonian biochar technology can increase SOC by 10-30 t/ha over decades.",
                }
            ]
        else:
            tek_insights = []

    elif simulator_id == "dssat":
        n_stress = metrics.get("nitrogen_stress", 0)
        n_leaching = metrics.get("nitrogen_leaching_kg_ha", 0)
        n_efficiency = metrics.get("nitrogen_efficiency", 0)

        analysis = f"Nitrogen efficiency: {n_efficiency:.0%}. Stress level: {n_stress:.0%}. Leaching: {n_leaching:.1f} kg/ha. "
        if n_stress > 0.3:
            analysis += "High nitrogen stress detected. Crop growth is significantly limited by nitrogen availability."
            recommendations.append(
                {
                    "level": "warning",
                    "icon": "droplet",
                    "text": f"Nitrogen stress is {n_stress:.0%}. Apply supplemental nitrogen fertilizer (50-80 kg N/ha) during vegetative stage.",
                    "source": "Jones J.W. et al. (2003). DSSAT Cropping System Model. European Journal of Agronomy.",
                }
            )
        elif n_leaching > 20:
            analysis += (
                "High nitrogen leaching detected. Split fertilizer applications recommended."
            )
            recommendations.append(
                {
                    "level": "warning",
                    "icon": "alert-triangle",
                    "text": f"Nitrogen leaching ({n_leaching:.1f} kg/ha) exceeds 20 kg/ha. Split fertilizer into 3-4 applications to improve efficiency.",
                    "source": "FAO (2001). Global Estimates of Gaseous Emissions of NH3, NO and N2O from Agricultural Land.",
                }
            )
        else:
            analysis += "Nitrogen management is within acceptable range."
            recommendations.append(
                {
                    "level": "success",
                    "icon": "check-circle",
                    "text": f"Nitrogen efficiency ({n_efficiency:.0%}) is good. Maintain current fertilization schedule.",
                    "source": "DSSAT v4.8 Documentation",
                }
            )

        scenarios = [
            {
                "id": "split_fertilizer",
                "name": "Split Fertilizer Application",
                "desc": "Divide N application into 3 splits (pre-plant, V6, VT)",
                "params": {"n_splits": 3},
            },
            {
                "id": "add_legume_rotation",
                "name": "Add Legume in Rotation",
                "desc": "Include legume crop to fix atmospheric nitrogen (Milpa principle)",
                "params": {"rotation": "maize_bean"},
            },
        ]
        references = [
            "Jones J.W. et al. (2003). The DSSAT cropping system model. European Journal of Agronomy 18(3-4)."
        ]

        # TEK insights for DSSAT
        tek_insights = (
            [
                {
                    "pattern_id": "milpa",
                    "name": "Milpa - Three Sisters Polyculture",
                    "relevance": "High",
                    "insight": "Maize-bean intercropping fixes 50-150 kg N/ha/year biologically, reducing fertilizer needs.",
                }
            ]
            if n_stress > 0.2
            else []
        )

    elif simulator_id == "swat":
        runoff_mm = metrics.get("runoff_mm", 0)
        total_precip = metrics.get("precipitation_mm", 100)
        runoff_pct = (runoff_mm / total_precip * 100) if total_precip > 0 else 0

        analysis = f"Runoff: {runoff_mm:.1f} mm ({runoff_pct:.0f}% of precipitation). "
        if runoff_pct > 50:
            analysis += "High runoff indicates poor infiltration. Soil conservation practices urgently needed."
            recommendations.append(
                {
                    "level": "warning",
                    "icon": "alert-octagon",
                    "text": f"Runoff is {runoff_pct:.0f}% of precipitation. Implement contour farming, terracing, or cover crops to reduce runoff.",
                    "source": "Neitsch S.L. et al. (2011). SWAT Theoretical Documentation. USDA-ARS.",
                }
            )
        elif runoff_pct > 20:
            analysis += "Moderate runoff. Some conservation practices would be beneficial."
            recommendations.append(
                {
                    "level": "info",
                    "icon": "info",
                    "text": f"Moderate runoff ({runoff_pct:.0f}%). Consider strip cropping or grassed waterways.",
                    "source": "USDA NRCS Conservation Practice Standards.",
                }
            )
        else:
            analysis += "Low runoff. Good infiltration and water retention."
            recommendations.append(
                {
                    "level": "success",
                    "icon": "shield",
                    "text": f"Low runoff ({runoff_pct:.0f}%). Soil infiltration capacity is adequate.",
                    "source": "SCS-CN Method, USDA TR-55",
                }
            )

        scenarios = [
            {
                "id": "contour_farming",
                "name": "Contour Farming",
                "desc": "Reduce CN by plowing along contours",
                "params": {"cn": parameters.get("cn", 79) - 5},
            },
            {
                "id": "terracing",
                "name": "Terracing",
                "desc": "Terrace construction for steep slopes",
                "params": {"cn": parameters.get("cn", 79) - 10},
            },
        ]
        references = [
            "Neitsch S.L. et al. (2011). SWAT Theoretical Documentation. USDA-ARS Grassland, Soil and Water Research Laboratory."
        ]

        # TEK insights for SWAT
        if runoff_pct > 30:
            tek_insights = [
                {
                    "pattern_id": "subak",
                    "name": "Subak - Balinese Water Temple System",
                    "relevance": "Medium",
                    "insight": "Balinese terrace systems reduce runoff and improve water distribution across slopes.",
                }
            ]
        else:
            tek_insights = []

    elif simulator_id == "aquacrop":
        yield_val = metrics.get("yield_t_ha", 0)
        wue = metrics.get("water_use_efficiency_kg_m3", 0)

        analysis = f"ط¹ظ…ظ„ع©ط±ط¯ ط´ط¨غŒظ‡â€ط³ط§ط²غŒâ€Œط´ط¯ظ‡ {yield_val:.2f} طھظ† ط¯ط± ظ‡ع©طھط§ط± ط§ط³طھ. "
        if yield_val < 3.0:
            analysis += "ط§غŒظ† ظ…ظ‚ط¯ط§ط± ظ†ط´ط§ظ†â€Œط¯ظ‡ظ” طھظ†ط´ ط´ط¯غŒط¯ (ط¢ط¨غŒ غŒط§ ط؛ط°ط§غŒغŒ) ط¯ط± ط·ظˆظ„ ط¯ظˆط±ظ‡ ط±ط´ط¯ ط§ط³طھ."
            recommendations.append(
                {
                    "level": "warning",
                    "icon": "droplet",
                    "text": "طھظ†ط´ ط¢ط¨غŒ ط´ظ†ط§ط³ط§غŒغŒ ط´ط¯. طھظˆطµغŒظ‡ ظ…غŒâ€Œط´ظˆط¯ ط¢ط¨غŒط§ط±غŒ طھع©ظ…غŒظ„غŒ ط¯ط± ظ…ط±ط§حظ„ ط­ط³ط§ط³ (ع¯ظ„ط¯ظ‡غŒ ظˆ ظ¾ط± ط´ط¯ظ† ط¯ط§ظ†ظ‡) ط§ط¹ظ…ط§ظ„ ط´ظˆط¯.",
                    "source": "FAO AquaCrop Paper 66, آ§Water Stress",
                }
            )
        else:
            analysis += "ط¹ظ…ظ„ع©ط±ط¯ ط¯ط± ظ…ط­ط¯ظˆط¯ظ‡ظ” ظ…ط·ظ„ظˆط¨ ظ‚ط±ط§ط± ط¯ط§ط±ط¯."
            recommendations.append(
                {
                    "level": "success",
                    "icon": "check-circle",
                    "text": "ظ…ط¯غŒط±غŒطھ ط¢ط¨غŒط§ط±غŒ ظپط¹ظ„غŒ ع©ط§ط±ط¢ظ…ط¯ ط§ط³طھ. ط¨ط±ط§غŒ ط¨ظ‡غŒظ†ظ‡â€Œط³ط§ط²غŒ ط¨غŒط´طھط±طŒ ظ…غŒâ€Œطھظˆط§ظ†غŒط¯ ط³ظ†ط§ط±غŒظˆغŒ ع©ط§ظ‡ط´ غ±غ°ظھ ط¢ط¨ ط±ط§ ط¨ط±ط±ط³غŒ ع©ظ†غŒط¯.",
                    "source": "FAO Water Productivity Guidelines",
                }
            )

        if wue > 0 and wue < 1.0:
            recommendations.append(
                {
                    "level": "warning",
                    "icon": "trending-down",
                    "text": "ط¨ظ‡ط±ظ‡â€Œظˆط±غŒ ط¢ط¨ (WUE) ظ¾ط§غŒغŒظ† ط§ط³طھ. ط¨ط±ط±ط³غŒ ظ†ط´طھ ط³غŒط³طھظ… ط¢ط¨غŒط§ط±غŒ غŒط§ ط§ط³طھظپط§ط¯ظ‡ ط§ز ط±ظˆط´â€Œظ‡ط§غŒ ظ‚ط·ط±ظ‡â€Œط§غŒ طھظˆطµغŒظ‡ ظ…غŒâ€Œط´ظˆط¯.",
                    "source": "FAO Irrigation and Drainage Paper",
                }
            )

        scenarios = [
            {
                "id": "deficit_irrigation",
                "name": "ط¢ط¨غŒط§ط±غŒ طھع©ظ…غŒظ„غŒ ط¨ظ‡غŒظ†ظ‡",
                "desc": "ط§ط¹ظ…ط§ظ„ غµغ° ظ…غŒظ„غŒâ€Œظ…طھط± ط¢ط¨غŒط§ط±غŒ ط§ضط§ظپغŒ ط¯ط± ظ…ط±حظ„ظ‡ ع¯ظ„ط¯ظ‡غŒ",
                "params": {"total_irrigation": parameters.get("total_irrigation", 250) + 50},
            },
            {
                "id": "drip_efficiency",
                "name": "ط§ط±طھظ‚ط§ط، ط¨ظ‡ ط¢ط¨غŒط§ط±غŒ ظ‚ط·ط±ظ‡â€Œط§غŒ",
                "desc": "ع©ط§ظ‡ط´ طھظ„ظپط§طھ طھط¨ط®غŒط± ظˆ ط§ضط²ط§غŒط´ ط¨ظ‡ط±ظ‡â€Œظˆط±غŒ ط¢ط¨",
                "params": {
                    "total_irrigation": parameters.get("total_irrigation", 250) * 0.8
                },  # 20% savings
            },
        ]
        references = [
            "Steduto P. et al. (2009). AquaCrop â€” The FAO Crop Model to Simulate Yield Response to Water. FAO Irrigation & Drainage Paper 66."
        ]

    elif simulator_id == "cba":
        npv = metrics.get("npv_m_usd", 0)
        irr = metrics.get("irr_pct", 0)

        analysis = f"ط§ط±زط´ ط®ط§ظ„طµ ظپط¹ظ„غŒ (NPV) ظ¾ط±ظˆعکظ‡ ط¨ط±ط§ط¨ط± ط¨ط§ {npv:.2f} ظˆ ظ†ط±ط® ط¨ط§زط¯ظ‡ ط¯ط§ط®ظ„غŒ (IRR) ط¨ط±ط§ط¨ط± {irr:.1f}ظھ ط§ط³طھ. "
        if npv > 0 and irr > 8.0:
            analysis += "ظ¾ط±ظˆعکظ‡ ط§ز ظ†ط¸ط± ط§ظ‚طھطµط§ط¯غŒ ع©ط§ظ…ظ„ط§ظ‹ طھظˆط¬غŒظ‡â€Œظ¾ط°غŒط± ظˆ ط³ظˆط¯ط¢ظˆط± ط§ط³طھ."
            recommendations.append(
                {
                    "level": "success",
                    "icon": "trending-up",
                    "text": "ط´ط§ط®طµâ€Œظ‡ط§غŒ ظ…ط§ظ„غŒ ظ…ط«ط¨طھ ظ‡ط³طھظ†ط¯. ط§ط¬ط±ط§غŒ ظ¾ط±ظˆعکظ‡ ط¨ط§ ط´ط±ط§غŒط· ظپط¹ظ„غŒ طھظˆطµغŒظ‡ ظ…غŒâ€Œط´ظˆط¯.",
                    "source": "Principles of Corporate Finance (Brealey, Myers, Allen)",
                }
            )
        else:
            analysis += "ظ¾ط±ظˆعکظ‡ ط¯ط± ظ…ط±ز طھظˆط¬غŒظ‡â€Œظ¾ط°غŒط±غŒ ظ‚ط±ط§ط± ط¯ط§ط±ط¯ غŒط§ ط²غŒط§ظ†â€Œط¯ظ‡ ط§ط³طھ."
            recommendations.append(
                {
                    "level": "warning",
                    "icon": "alert-triangle",
                    "text": "NPV ظ…ظ†ظپغŒ غŒط§ ظ¾ط§غŒغŒظ† ط§ط³طھ. ظ¾غŒط´ظ†ظ‡ط§ط¯ ظ…غŒâ€Œط´ظˆط¯ ظ‡زغŒظ†ظ‡â€Œظ‡ط§غŒ ط³ط±ظ…ط§غŒظ‡â€Œع¯ط°ط§ط±غŒ ط§ظˆظ„غŒظ‡ ط±ط§ ع©ط§ظ‡ط´ ط¯ظ‡غŒط¯ غŒط§ ط¨ظ‡ ط¯ظ†ط¨ط§ظ„ طھط³ظ‡غŒظ„ط§طھ ط¨ط§ ظ†ط±خ ط¨ظ‡ط±ظ‡ ظ¾ط§غŒغŒظ†â€Œطھط± ط¨ط§ط´غŒط¯.",
                    "source": "World Bank Project Appraisal Guidelines",
                }
            )

        scenarios = [
            {
                "id": "cost_reduction",
                "name": "ع©ط§ظ‡ط´ غ²غ°ظھ ظ‡زغŒظ†ظ‡â€Œظ‡ط§غŒ ط§ط¬ط±ط§غŒغŒ",
                "desc": "ط¨ط±ط±ط³غŒ ط­ط³ط§ط³غŒطھ ظ¾ط±ظˆعکظ‡ ط¨ظ‡ ط¨ظ‡غŒظ†ظ‡â€Œط³ط§زغŒ ظ‡زغŒظ†ظ‡â€Œظ‡ط§",
                "params": {"annual_cost": parameters.get("annual_cost", 500) * 0.8},
            },
            {
                "id": "subsidy",
                "name": "ط§ط¹ظ…ط§ظ„ غŒط§ط±ط§ظ†ظ‡ ط¯ظˆظ„طھغŒ",
                "desc": "ع©ط§ظ‡ط´ ظ†ط±خ طھظ†زغŒظ„ ظ…ط¤ط«ط± ط¨ظ‡ ط¯ظ„غŒظ„ طھط³ظ‡غŒظ„ط§طھ",
                "params": {"discount_rate": 3.0},
            },
        ]
        references = [
            "Boardman A.E. et al. (2017). Cost-Benefit Analysis: Concepts and Practice. Cambridge University Press."
        ]

    elif simulator_id == "rusle2":
        soil_loss = metrics.get("soil_loss_t_ha", 0)
        analysis = f"ظ…غŒزط§ظ† ظپط±ط³ط§غŒط´ ط®ط§ع© ط´ط¨غŒظ‡â€Œط³ط§ط²غŒâ€Œط´ط¯ظ‡ {soil_loss:.2f} طھظ† ط¯ط± ظ‡ع©طھط§ط± ط¯ط± ط³ط§ظ„ ط§ط³طھ. "
        if soil_loss > 10.0:  # Tolerable soil loss is often around 10 t/ha/yr
            analysis += "ط§غŒظ† ظ…ظ‚ط¯ط§ط± ط¨غŒط´ ط§ط² ط­ط¯ ظ…ط¬ط§ز ظپط±ط³ط§غŒط´ (T-value) ط§ط³طھ ظˆ ظ†غŒط§ز ط¨ظ‡ ظ…ط¯ط§خظ„ظ‡ ظپظˆط±غŒ ط¯ط§ط±ط¯."
            recommendations.append(
                {
                    "level": "warning",
                    "icon": "alert-octagon",
                    "text": "ظپط±ط³ط§غŒط´ ط®ط§ع© ط´ط¯غŒط¯ ط§ط³طھ. ط§ط¬ط±ط§غŒ ط¹ظ…ظ„غŒط§طھ ط­ظپط§ط¸طھغŒ ظ…ط§ظ†ظ†ط¯ ع©ط´طھ ظ†ظˆط§ط±غŒطŒ طھط±ط§ط³â€Œط¨ظ†ط¯غŒ غŒط§ ط§ضط²ط§غŒط´ ظ¾ظˆط´ط´ ع¯غŒط§ظ‡غŒ ط§ع©غŒط¯ط§ظ‹ طھظˆطµغŒظ‡ ظ…غŒâ€Œط´ظˆط¯.",
                    "source": "USDA Agriculture Handbook 703 (RUSLE2)",
                }
            )
        else:
            analysis += "ظ…غŒزط§ظ† ظپط±ط³ط§غŒط´ ط¯ط± ظ…ط­ط¯ظˆط¯ظ‡ظ” ظ‚ط§ط¨ظ„ ظ‚ط¨ظˆظ„ ظˆ ظ¾ط§غŒط¯ط§ط± ظ‚ط±ط§ط± ط¯ط§ط±ط¯."
            recommendations.append(
                {
                    "level": "success",
                    "icon": "shield",
                    "text": "ظ…ط¯غŒط±غŒطھ ظپط¹ظ„غŒ ط®ط§ع© ظ…ط¤ط«ط± ط§ط³طھ. ط­ظپط¸ ظ¾ظˆط´ط´ ع¯غŒط§ظ‡غŒ ظˆ ط¹ط¯ظ… ط´ط®ظ… ط¹ظ…غŒظ‚ ط±ط§ ط§ط¯ط§ظ…ظ‡ ط¯ظ‡غŒط¯.",
                    "source": "USDA NRCS Conservation Practice Standards",
                }
            )

        scenarios = [
            {
                "id": "contour_farming",
                "name": "ع©ط´طھ ط±ظˆغŒ ط®ط·ظˆط· طھط±ط§ز (Contour)",
                "desc": "ع©ط§ظ‡ط´ ط¹ط§ظ…ظ„ ط­ظپط§ط¸طھغŒ P",
                "params": {"P": parameters.get("P", 1.0) * 0.5},
            },
            {
                "id": "cover_crop",
                "name": "ع©ط§ط´طھ ع¯غŒط§ظ‡ ظ¾ظˆط´ط´غŒ",
                "desc": "ع©ط§ظ‡ط´ ط¹ط§ظ…ظ„ ظ¾ظˆط´ط´ C",
                "params": {"C": parameters.get("C", 0.5) * 0.6},
            },
        ]
        references = [
            "Renard K.G. et al. (1997). Predicting Soil Erosion by Water: A Guide to Conservation Planning with RUSLE. USDA."
        ]

    else:
        # Fallback for other simulators (DSSAT, SWAT, etc.)
        analysis = "طھط­ظ„غŒظ„ طھط®طµطµغŒ ظ…طھظ†غŒ ط¨ط±ط§غŒ ط§غŒظ† ط´ط¨غŒظ‡â€Œط³ط§ط² ط¯ط± ط­ط§ظ„ طھظˆط³ط¹ظ‡ ط§ط³طھ. ظ„ط·ظپط§ظ‹ ط¨ظ‡ ط®ط±ظˆط¬غŒâ€Œظ‡ط§غŒ ط¹ط¯ط¯غŒطŒ ظ†ظ…ظˆط¯ط§ط±ظ‡ط§ ظˆ ط¨ط®ط´ ط§ط¹طھط¨ط§ط±ط³ظ†جغŒ طھظˆط¬ظ‡ ع©ظ†غŒط¯."
        recommendations = [
            {
                "level": "info",
                "icon": "info",
                "text": "ظ‚ظˆط§ظ†غŒظ† طھظˆطµغŒظ‡ظ” ظ…ط³طھظ†ط¯ ط¨ط±ط§غŒ ط§غŒظ† ظ…ط§عکظˆظ„ ط¨ظ‡â€Œزظˆط¯غŒ ط¨ط± ط§ط³ط§ط³ ظ…ظ‚ط§ظ„ط§طھ ظ…ط±ط¬ط¹ ط§ضط§ظپظ‡ ط®ظˆط§ظ‡ط¯ ط´ط¯.",
                "source": "EcoNojin Development Roadmap",
            }
        ]
        scenarios = []
        references = []
        tek_insights = []

    return {
        "simulator_id": simulator_id,
        "analysis": analysis,
        "recommendations": recommendations,
        "scenarios": scenarios,
        "references": references,
        "tek_insights": tek_insights,
    }
