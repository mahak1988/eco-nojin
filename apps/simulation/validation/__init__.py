"""Validation & uncertainty quantification package."""
try:
    from .uncertainty import (
        nse, rmse, kge, pbias, r_squared, compute_all_metrics,
        ParameterSpec, morris_screening, sobol_indices, pce_fit, pce_predict,
        enkf_update, enkf_forecast, run_uq_pipeline, batch_metric_evaluation,
    )
    _UQ = True
except ImportError:
    _UQ = False

__all__ = []
if _UQ:
    __all__ += [
        "nse", "rmse", "kge", "pbias", "r_squared", "compute_all_metrics",
        "ParameterSpec", "morris_screening", "sobol_indices", "pce_fit", "pce_predict",
        "enkf_update", "enkf_forecast", "run_uq_pipeline", "batch_metric_evaluation",
    ]
