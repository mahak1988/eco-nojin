"""Surrogate ML models for Economugin scientific models
Train with: python scripts/research/train_surrogates.py
"""
import json, joblib, numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from scripts.core.logger import UnifiedLogger
logger = UnifiedLogger.get_logger(__name__)


class SurrogateModel:
    def __init__(self, target: str):
        self.target = target
        self.pipeline = None
    
    def train(self, X: list, y: list):
        """Train surrogate model"""
        self.pipeline = Pipeline([
            ("scaler", StandardScaler()),
            ("rf", RandomForestRegressor(n_estimators=100, max_depth=10, random_state=42))
        ])
        self.pipeline.fit(np.array(X), np.array(y))
        return self
    
    def predict(self, X: list) -> list:
        """Fast prediction (100-1000x faster than scientific model)"""
        return self.pipeline.predict(np.array(X)).tolist()
    
    def save(self, path: str):
        joblib.dump(self.pipeline, path)
    
    @classmethod
    def load(cls, path: str, target: str):
        model = cls(target)
        model.pipeline = joblib.load(path)
        return model

# Example usage
if __name__ == "__main__":
    # Load training data
    with open("data/processed/surrogate_training_data.json") as f:
        data = json.load(f)
    
    # Prepare features/targets
    X = [[d["precip_mm"], d["temp_avg_c"], d["clay_pct"], d["management_code"]] for d in data]
    y_yield = [d["yield_kg_ha"] for d in data]
    y_soc = [d["soc_change_t_ha"] for d in data]
    
    # Train models
    yield_model = SurrogateModel("yield").train(X, y_yield)
    soc_model = SurrogateModel("soc").train(X, y_soc)
    
    # Save
    yield_model.save("models/surrogate_yield.pkl")
    soc_model.save("models/surrogate_soc.pkl")
    
    # Test prediction speed
    import time
    test_input = [[350, 20, 25, 2]]  # precip, temp, clay, management
    start = time.time()
    pred_yield = yield_model.predict(test_input)[0]
    pred_soc = soc_model.predict(test_input)[0]
    elapsed = (time.time() - start) * 1000
    logger.info(f"✓ Prediction: yield={pred_yield:.1f} kg/ha, soc={pred_soc:.2f} t/ha ({elapsed:.2f} ms)")
