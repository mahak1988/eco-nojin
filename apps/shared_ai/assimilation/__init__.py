"""
Data Assimilation Module
=========================

Advanced data assimilation and sensor fusion techniques for the
Econojin platform. Handles multiple data sources (weather stations,
satellite imagery, IoT sensors) and fuses them into coherent estimates.

Submodules:
    - kalman_filter: Classic Kalman filter for linear systems
    - ensemble: Ensemble Kalman Filter for non-linear systems
    - data_fusion: Multi-source data fusion and integration

Applications:
    - Agricultural sensor data fusion (soil moisture, temperature, humidity)
    - Climate model data assimilation
    - Economic indicator smoothing and forecasting
    - Multi-source weather data reconciliation
"""

from apps.shared_ai.assimilation.kalman_filter import KalmanFilter
from apps.shared_ai.assimilation.ensemble import EnsembleKalmanFilter
from apps.shared_ai.assimilation.data_fusion import DataFusionEngine

__all__ = [
    "KalmanFilter",
    "EnsembleKalmanFilter",
    "DataFusionEngine",
]
