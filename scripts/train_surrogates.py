#!/usr/bin/env python3
"""Train surrogate models from Economugin simulation data"""
import json
import sys

import numpy as np

sys.path.insert(0, r"D:\\econojin.com")
from scripts.core.logger import UnifiedLogger
from scripts.research.surrogate_models import SurrogateModel

logger = UnifiedLogger.get_logger(__name__)


def main():
    # Load data
    with open("data/processed/surrogate_training_data.json") as f:
        data = json.load(f)

    X = [[d["precip_mm"], d["temp_avg_c"], d["clay_pct"], d["management_code"]] for d in data]
    y_yield = [d["yield_kg_ha"] for d in data]
    y_soc = [d["soc_change_t_ha"] for d in data]

    # Train
    yield_model = SurrogateModel("yield").train(X, y_yield)
    soc_model = SurrogateModel("soc").train(X, y_soc)

    # Evaluate (simple R²)
    from sklearn.metrics import r2_score

    yield_pred = yield_model.predict(X)
    soc_pred = soc_model.predict(X)
    logger.info(f"Yield model R²: {r2_score(y_yield, yield_pred):.3f}")
    logger.info(f"SOC model R²: {r2_score(y_soc, soc_pred):.3f}")

    # Save
    import os

    os.makedirs("models", exist_ok=True)
    yield_model.save("models/surrogate_yield.pkl")
    soc_model.save("models/surrogate_soc.pkl")
    logger.info("✓ Models saved to models/")


if __name__ == "__main__":
    main()
