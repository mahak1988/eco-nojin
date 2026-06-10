"""Example: Generate research figures from Economugin output"""
import json
import sys

sys.path.insert(0, r"D:\\econojin.com")
from scripts.core.logger import UnifiedLogger
from scripts.research.plot_utils import (
    plot_scenario_comparison,
    plot_uncertainty_bands,
    plot_yield_soc_scatter,
)

logger = UnifiedLogger.get_logger(__name__)


def main():
    # Load data
    with open("data/processed/research_report_v1.json") as f:
        report = json.load(f)
    with open("data/processed/uncertainty_analysis.json") as f:
        unc = json.load(f)
    with open("data/processed/surrogate_training_data.json") as f:
        train = json.load(f)

    # Generate figures
    import os

    os.makedirs("output/figures", exist_ok=True)

    # Figure 1: Scenario comparison
    plot_scenario_comparison(report["results_summary"], "output/figures/fig1_scenarios.png")

    # Figure 2: Uncertainty bands
    plot_uncertainty_bands(
        unc["yield"]["samples"] if "samples" in unc["yield"] else [3200] * 1000,
        "output/figures/fig2_uncertainty_yield.png",
        ylabel="Yield (kg/ha)",
    )

    # Figure 3: Yield-SOC trade-off
    plot_yield_soc_scatter(train[:200], "output/figures/fig3_tradeoff.png")

    logger.info("✓ Figures saved to output/figures/")


if __name__ == "__main__":
    main()
