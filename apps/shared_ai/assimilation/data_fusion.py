"""
Multi-Source Data Fusion Engine
================================

Integrates heterogeneous data sources into unified estimates.
Handles:
    - Weighted averaging of sensor networks
    - Bayesian data fusion
    - Dempster-Shafer evidence combination
    - Time-series alignment and interpolation
    - Quality-based source weighting

Applications:
    - Fusing weather station + satellite + reanalysis data
    - Combining soil moisture from multiple sensor types
    - Merging economic indicators from various agencies
    - Multi-modal agricultural monitoring

Examples:
    >>> engine = DataFusionEngine()
    >>> engine.add_source("station_1", data=[25.3, 0.65], variance=0.1)
    >>> engine.add_source("satellite", data=[24.8, 0.72], variance=0.3)
    >>> fused = engine.fuse_weighted_average()
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------


@dataclass
class DataSource:
    """Represents a single data source for fusion.

    Attributes:
        name: Unique source identifier.
        data: Vector or scalar data point.
        variance: Uncertainty (variance) of each data element.
        timestamp: When the data was collected.
        weight: User-assigned or quality-derived weight.
        metadata: Arbitrary additional metadata.
    """

    name: str
    data: np.ndarray
    variance: np.ndarray
    timestamp: Optional[datetime] = None
    weight: float = 1.0
    metadata: Dict[str, Any] = field(default_factory=dict)


# ---------------------------------------------------------------------------
# Fusion Engine
# ---------------------------------------------------------------------------


class DataFusionEngine:
    """Multi-source data fusion engine.

    Combines measurements from heterogeneous sources into a single
    optimal estimate using various fusion algorithms.

    Attributes:
        sources: Registered data sources for the current fusion cycle.
        method: Default fusion method.
        quality_scores: Source quality tracking.
    """

    def __init__(
        self,
        default_method: str = "weighted_average",
        outlier_threshold: float = 3.0,
    ) -> None:
        """Initialize the fusion engine.

        Args:
            default_method: Default fusion algorithm name.
            outlier_threshold: Mahalanobis distance threshold for outlier rejection.

        Raises:
            ValueError: If default_method is unsupported.
        """
        self._valid_methods: Tuple[str, ...] = (
            "weighted_average",
            "kalman_fusion",
            "bayesian",
            "dempster_shafer",
            "best_source",
        )

        if default_method not in self._valid_methods:
            raise ValueError(
                f"Unknown method '{default_method}'. "
                f"Available: {self._valid_methods}"
            )

        self.default_method: str = default_method
        self.outlier_threshold: float = outlier_threshold

        self.sources: List[DataSource] = []
        self.quality_scores: Dict[str, float] = {}

        self._fusion_history: List[Dict[str, Any]] = []

        logger.info(
            "DataFusionEngine initialized: method=%s, threshold=%.1f",
            default_method,
            outlier_threshold,
        )

    # ------------------------------------------------------------------
    # Source management
    # ------------------------------------------------------------------

    def add_source(
        self,
        name: str,
        data: ArrayLike,
        variance: Optional[ArrayLike] = None,
        timestamp: Optional[datetime] = None,
        weight: float = 1.0,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Register a data source for fusion.

        Args:
            name: Source identifier.
            data: Data vector/scalar.
            variance: Measurement variance (default: 1.0 per element).
            timestamp: Observation time.
            weight: Source weight.
            metadata: Optional metadata dict.

        Raises:
            ValueError: If data is empty.
        """
        data_arr: np.ndarray = np.atleast_1d(np.array(data, dtype=np.float64))

        if data_arr.size == 0:
            raise ValueError(f"Source '{name}' has empty data")

        if variance is None:
            variance_arr: np.ndarray = np.ones(data_arr.shape)
        else:
            variance_arr = np.atleast_1d(np.array(variance, dtype=np.float64))
            if variance_arr.shape != data_arr.shape:
                # Broadcast scalar to vector
                if variance_arr.size == 1:
                    variance_arr = np.full(data_arr.shape, variance_arr.item())
                else:
                    raise ValueError(
                        f"Variance shape {variance_arr.shape} does not "
                        f"match data shape {data_arr.shape}"
                    )

        # Clip variance to avoid division by zero
        variance_arr = np.maximum(variance_arr, 1e-10)

        source: DataSource = DataSource(
            name=name,
            data=data_arr,
            variance=variance_arr,
            timestamp=timestamp or datetime.utcnow(),
            weight=weight,
            metadata=metadata or {},
        )

        # Update quality score
        self._update_quality_source(source)

        self.sources.append(source)
        logger.debug("Added source '%s': data=%s", name, data_arr)

    def clear_sources(self) -> None:
        """Remove all registered data sources."""
        self.sources.clear()

    # ------------------------------------------------------------------
    # Fusion methods
    # ------------------------------------------------------------------

    def fuse(
        self,
        method: Optional[str] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Fuse all registered sources using the specified method.

        Args:
            method: Fusion method name (uses default if None).
            **kwargs: Method-specific parameters.

        Returns:
            Dict with keys: fused_value, variance, method, source_count,
            and method-specific diagnostics.

        Raises:
            ValueError: If no sources are registered.
        """
        if not self.sources:
            raise ValueError("No sources registered for fusion")

        fusion_method: str = method or self.default_method

        # Reject outliers first
        clean_sources: List[DataSource] = self._reject_outliers()

        if not clean_sources:
            logger.warning("All sources rejected as outliers; using raw sources")
            clean_sources = self.sources

        # Dispatch
        fusion_map: Dict[str, Callable] = {
            "weighted_average": self._fuse_weighted_average,
            "kalman_fusion": self._fuse_kalman,
            "bayesian": self._fuse_bayesian,
            "dempster_shafer": self._fuse_dempster_shafer,
            "best_source": self._fuse_best_source,
        }

        result: Dict[str, Any] = fusion_map[fusion_method](clean_sources, **kwargs)
        result["method"] = fusion_method
        result["source_count"] = len(clean_sources)
        result["total_sources"] = len(self.sources)
        result["timestamp"] = datetime.utcnow().isoformat()

        self._fusion_history.append(result)
        logger.info(
            "Fusion complete: method=%s, sources=%d, result=%s",
            fusion_method,
            len(clean_sources),
            result.get("fused_value"),
        )

        return result

    # --- Weighted Average ---

    def _fuse_weighted_average(self, sources: List[DataSource]) -> Dict[str, Any]:
        """Fuse via inverse-variance weighted average.

        Args:
            sources: Cleaned data sources.

        Returns:
            Fused result dict.
        """
        # Weights = 1 / variance for each source
        total_weight: float = 0.0
        weighted_sum: Optional[np.ndarray] = None

        for source in sources:
            weight: float = np.sum(source.weight / source.variance)
            total_weight += weight

            if weighted_sum is None:
                weighted_sum = source.data * weight
            else:
                weighted_sum += source.data * weight

        fused_value: np.ndarray = weighted_sum / total_weight
        fused_variance: float = 1.0 / total_weight

        return {
            "fused_value": fused_value.tolist(),
            "variance": float(fused_variance),
            "weights": {
                s.name: float(np.sum(s.weight / s.variance)) for s in sources
            },
        }

    # --- Kalman Fusion ---

    def _fuse_kalman(self, sources: List[DataSource]) -> Dict[str, Any]:
        """Fuse multiple sources via sequential Kalman updates.

        Treats each source as a sequential measurement update
        to refine a global state estimate.

        Args:
            sources: Data sources.

        Returns:
            Fused result dict.
        """
        from apps.shared_ai.assimilation.kalman_filter import KalmanFilter

        data_dim: int = sources[0].data.shape[0]
        kf: KalmanFilter = KalmanFilter(
            state_dim=data_dim,
            measurement_dim=data_dim,
        )

        # Start from first source
        kf.x = sources[0].data.copy()

        # Sequentially update
        for source in sources[1:]:
            kf.R = np.diag(source.variance)
            kf.update(source.data)

        fused_state: np.ndarray = kf.get_state()
        fused_cov: np.ndarray = kf.get_covariance()

        return {
            "fused_value": fused_state.tolist(),
            "variance": float(np.mean(np.diag(fused_cov))),
            "covariance": fused_cov.tolist(),
            "kalman_iterations": len(sources) - 1,
        }

    # --- Bayesian Fusion ---

    def _fuse_bayesian(self, sources: List[DataSource]) -> Dict[str, Any]:
        """Fuse via Bayesian posterior update.

        Assumes Gaussian likelihoods and a non-informative prior.
        Computes the maximum a posteriori (MAP) estimate.

        Args:
            sources: Data sources.

        Returns:
            Fused result dict.
        """
        # Posterior precision = sum of precisions
        total_precision: np.ndarray = np.zeros(
            (sources[0].data.shape[0], sources[0].data.shape[0])
        )
        precision_weighted_sum: np.ndarray = np.zeros(sources[0].data.shape[0])

        for source in sources:
            precision: np.ndarray = np.diag(1.0 / source.variance) * source.weight
            total_precision += precision
            precision_weighted_sum += precision @ source.data

        try:
            total_var: np.ndarray = np.linalg.inv(total_precision)
            map_estimate: np.ndarray = total_var @ precision_weighted_sum
        except np.linalg.LinAlgError:
            total_var = np.linalg.pinv(total_precision)
            map_estimate = total_var @ precision_weighted_sum

        return {
            "fused_value": map_estimate.tolist(),
            "variance": float(np.mean(np.diag(total_var))),
            "posterior_covariance": total_var.tolist(),
            "log_evidence": float(
                -0.5
                * np.sum(
                    [
                        np.sum(
                            (s.data - map_estimate) ** 2 / s.variance
                        )
                        for s in sources
                    ]
                )
            ),
        }

    # --- Dempster-Shafer ---

    def _fuse_dempster_shafer(self, sources: List[DataSource]) -> Dict[str, Any]:
        """Fuse via Dempster-Shafer evidence theory.

        Combines evidence masses from multiple sources.
        Each source contributes a belief mass proportional to its precision.

        Args:
            sources: Data sources.

        Returns:
            Fused result dict.
        """
        # Compute total belief and conflict
        total_belief: float = 0.0
        conflict: float = 0.0

        for i, s1 in enumerate(sources):
            for j, s2 in enumerate(sources):
                if i < j:
                    # Evidence mass from each source (inverse variance)
                    m1: float = np.mean(1.0 / s1.variance) * s1.weight
                    m2: float = np.mean(1.0 / s2.variance) * s2.weight

                    # Agreement measure
                    agreement: float = float(
                        np.exp(-0.5 * np.sum((s1.data - s2.data) ** 2))
                    )

                    total_belief += agreement * m1 * m2
                    conflict += (1.0 - agreement) * m1 * m2

        # Fused value via weighted average
        weighted_result: Dict[str, Any] = self._fuse_weighted_average(sources)

        return {
            "fused_value": weighted_result["fused_value"],
            "variance": weighted_result["variance"],
            "belief": round(total_belief, 4),
            "conflict": round(conflict, 4),
            "consistency": round(total_belief / (total_belief + conflict + 1e-10), 4),
        }

    # --- Best Source ---

    def _fuse_best_source(self, sources: List[DataSource]) -> Dict[str, Any]:
        """Select the single best source based on quality score.

        Args:
            sources: Data sources.

        Returns:
            Fused result dict.
        """
        best: DataSource = max(
            sources,
            key=lambda s: self.quality_scores.get(s.name, s.weight / np.mean(s.variance)),
        )

        return {
            "fused_value": best.data.tolist(),
            "variance": float(np.mean(best.variance)),
            "best_source": best.name,
            "quality_score": round(self.quality_scores.get(best.name, 0.0), 4),
        }

    # ------------------------------------------------------------------
    # Outlier detection
    # ------------------------------------------------------------------

    def _reject_outliers(self) -> List[DataSource]:
        """Reject outlier sources via Mahalanobis distance.

        Returns:
            List of non-outlier sources.
        """
        if len(self.sources) <= 1:
            return list(self.sources)

        # Compute group mean and covariance
        all_data: np.ndarray = np.array([s.data for s in self.sources])
        group_mean: np.ndarray = np.mean(all_data, axis=0)
        group_cov: np.ndarray = np.cov(all_data, rowvar=False)

        # Regularize
        group_cov += np.eye(group_cov.shape[0]) * 1e-4

        clean_sources: List[DataSource] = []
        try:
            cov_inv: np.ndarray = np.linalg.inv(group_cov)

            for source in self.sources:
                diff: np.ndarray = source.data - group_mean
                mahalanobis: float = float(
                    np.sqrt(diff.T @ cov_inv @ diff)
                )

                if mahalanobis <= self.outlier_threshold:
                    clean_sources.append(source)
                else:
                    logger.warning(
                        "Outlier rejected: '%s' (mahalanobis=%.2f, threshold=%.1f)",
                        source.name,
                        mahalanobis,
                        self.outlier_threshold,
                    )

        except np.linalg.LinAlgError:
            logger.warning("Covariance matrix singular; skipping outlier rejection")
            return list(self.sources)

        return clean_sources

    # ------------------------------------------------------------------
    # Quality tracking
    # ------------------------------------------------------------------

    def _update_quality_source(self, source: DataSource) -> None:
        """Update quality score for a source.

        Args:
            source: Data source to evaluate.
        """
        # Quality = weight / average variance
        avg_var: float = float(np.mean(source.variance))
        quality: float = source.weight / max(avg_var, 1e-10)
        self.quality_scores[source.name] = quality

    def get_quality_report(self) -> Dict[str, float]:
        """Return quality scores for all seen sources.

        Returns:
            Dict mapping source name to quality score.
        """
        return dict(self.quality_scores)

    # ------------------------------------------------------------------
    # Utilities
    # ------------------------------------------------------------------

    def fuse_sensor_network(
        self,
        sensor_readings: Dict[str, ArrayLike],
        variances: Optional[Dict[str, ArrayLike]] = None,
    ) -> Dict[str, Any]:
        """One-step fusion of a sensor network.

        Convenience method that adds all sensors and fuses in one call.

        Args:
            sensor_readings: Dict of {sensor_name: reading_value}.
            variances: Optional dict of {sensor_name: variance}.

        Returns:
            Fused result dict.
        """
        self.clear_sources()

        for name, reading in sensor_readings.items():
            var: Optional[ArrayLike] = variances.get(name) if variances else None
            self.add_source(name=name, data=reading, variance=var)

        return self.fuse()

    def get_history(self) -> List[Dict[str, Any]]:
        """Return the fusion history.

        Returns:
            List of fusion result dicts.
        """
        return list(self._fusion_history)

    def reset(self) -> None:
        """Clear sources and history."""
        self.clear_sources()
        self._fusion_history.clear()
        logger.info("DataFusionEngine reset")

    # ------------------------------------------------------------------
    # Time-series specific
    # ------------------------------------------------------------------

    def fuse_time_series(
        self,
        time_series: Dict[str, Dict[datetime, float]],
        method: Optional[str] = None,
    ) -> Dict[datetime, Dict[str, Any]]:
        """Fuse multiple time series into a single aligned series.

        Args:
            time_series: Dict mapping source name to {timestamp: value}.
            method: Fusion method.

        Returns:
            Dict mapping timestamp to fused result.
        """
        # Collect all unique timestamps
        all_timestamps: set = set()
        for series in time_series.values():
            all_timestamps.update(series.keys())

        sorted_ts: List[datetime] = sorted(all_timestamps)
        results: Dict[datetime, Dict[str, Any]] = {}

        for ts in sorted_ts:
            self.clear_sources()

            for source_name, series in time_series.items():
                if ts in series:
                    self.add_source(
                        name=source_name,
                        data=series[ts],
                        timestamp=ts,
                    )

            if self.sources:
                results[ts] = self.fuse(method=method)

        return results
