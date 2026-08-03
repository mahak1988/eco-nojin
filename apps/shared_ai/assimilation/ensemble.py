"""
Ensemble Kalman Filter (EnKF)
===============================

Implements the Ensemble Kalman Filter for non-linear data
assimilation problems. Uses a Monte Carlo ensemble to
approximate state distributions without explicit linearization.

Mathematical Background:
    State:  X = [x^(1), x^(2), ..., x^(N)]  (N ensemble members)
    Prediction: x^(i)_k = f(x^(i)_{k-1}) + w^(i)_k
    Update:    X^a = X^f + K * (D - H * X^f)

Applications in Econojin:
    - Crop growth model assimilation (non-linear dynamics)
    - Satellite-derived vegetation indices fusion
    - Non-linear economic model calibration
    - Weather forecast ensemble processing

Examples:
    >>> def crop_model(state, params):
    ...     return state * 1.1 + params["rainfall"] * 0.01
    ...
    >>> enkf = EnsembleKalmanFilter(state_dim=3, ensemble_size=50)
    >>> enkf.predict(model=crop_model, model_params={"rainfall": 25.0})
    >>> enkf.update(measurement=np.array([0.8, 15.2, 3.1]))
    >>> mean, std = enkf.get_ensemble_stats()
"""

from __future__ import annotations

import logging
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

import numpy as np

logger = logging.getLogger(__name__)

# Type alias for model function
ModelFunction = Callable[[np.ndarray, Dict[str, Any]], np.ndarray]


class EnsembleKalmanFilter:
    """Ensemble Kalman Filter for non-linear state estimation.

    Maintains an ensemble of state vectors that collectively
    represent the state probability distribution.

    Attributes:
        state_dim: Dimension of state vector.
        ensemble_size: Number of ensemble members.
        measurement_dim: Dimension of measurement vector.
        X: Ensemble matrix, shape (state_dim, ensemble_size).
        R: Measurement noise covariance.
    """

    def __init__(
        self,
        state_dim: int,
        ensemble_size: int = 100,
        measurement_dim: int = 1,
        process_noise_std: float = 0.01,
        measurement_noise_std: float = 0.1,
        inflation_factor: float = 1.01,
        localization_radius: Optional[float] = None,
        random_seed: Optional[int] = None,
    ) -> None:
        """Initialize the Ensemble Kalman Filter.

        Args:
            state_dim: Dimension of the state vector.
            ensemble_size: Number of ensemble members.
            measurement_dim: Dimension of measurement vectors.
            process_noise_std: Standard deviation of additive process noise.
            measurement_noise_std: Standard deviation of measurement noise.
            inflation_factor: Multiplicative covariance inflation factor (>1).
            localization_radius: Optional spatial localization radius.
            random_seed: Random seed for reproducibility.

        Raises:
            ValueError: If dimensions or ensemble size are invalid.
        """
        if state_dim <= 0:
            raise ValueError(f"state_dim must be positive, got {state_dim}")
        if ensemble_size < 2:
            raise ValueError(f"ensemble_size must be at least 2, got {ensemble_size}")

        self.state_dim: int = state_dim
        self.ensemble_size: int = ensemble_size
        self.measurement_dim: int = measurement_dim
        self.process_noise_std: float = process_noise_std
        self.measurement_noise_std: float = measurement_noise_std
        self.inflation_factor: float = inflation_factor
        self.localization_radius: Optional[float] = localization_radius

        # Random state
        self._rng: np.random.Generator = np.random.default_rng(seed=random_seed)

        # Ensemble matrix: (state_dim, ensemble_size)
        self.X: np.ndarray = np.zeros((state_dim, ensemble_size))

        # Observation matrix
        self.H: np.ndarray = np.zeros((measurement_dim, state_dim))
        self.H[:measurement_dim, :measurement_dim] = np.eye(
            min(measurement_dim, state_dim)
        )

        # Measurement noise covariance
        self.R: np.ndarray = np.eye(measurement_dim) * (measurement_noise_std ** 2)

        # Perturbed observation ensemble (for stochastic EnKF)
        self._perturbed_obs: Optional[np.ndarray] = None

        # History
        self._history: List[Dict[str, Any]] = []

        logger.info(
            "EnKF initialized: dim=%d, ensemble=%d, inflation=%.3f",
            state_dim,
            ensemble_size,
            inflation_factor,
        )

    # ------------------------------------------------------------------
    # Configuration
    # ------------------------------------------------------------------

    def initialize_ensemble(
        self,
        mean: Optional[ArrayLike] = None,
        cov: Optional[ArrayLike] = None,
    ) -> None:
        """Initialize the ensemble from a Gaussian distribution.

        Args:
            mean: Mean state vector (default: zeros).
            cov: Covariance matrix. If None, uses identity.
        """
        mean_arr: np.ndarray = (
            np.atleast_1d(np.array(mean, dtype=np.float64))
            if mean is not None
            else np.zeros(self.state_dim)
        )

        if cov is not None:
            cov_arr: np.ndarray = np.atleast_2d(np.array(cov, dtype=np.float64))
            # Cholesky decomposition for correlated samples
            try:
                L: np.ndarray = np.linalg.cholesky(cov_arr)
                for i in range(self.ensemble_size):
                    self.X[:, i] = mean_arr + L @ self._rng.normal(
                        0, 1, self.state_dim
                    )
            except np.linalg.LinAlgError:
                logger.warning(
                    "Covariance not positive definite, using diagonal sampling"
                )
                stds: np.ndarray = np.sqrt(np.maximum(np.diag(cov_arr), 0.0))
                for i in range(self.ensemble_size):
                    self.X[:, i] = mean_arr + stds * self._rng.normal(
                        0, 1, self.state_dim
                    )
        else:
            for i in range(self.ensemble_size):
                self.X[:, i] = mean_arr + self._rng.normal(0, 1, self.state_dim)

        logger.info("Ensemble initialized with mean=[%s]", mean_arr)

    def set_observation_matrix(self, H: ArrayLike) -> None:
        """Set the observation matrix.

        Args:
            H: Observation matrix (measurement_dim x state_dim).

        Raises:
            ValueError: If shape does not match.
        """
        H_arr: np.ndarray = np.atleast_2d(np.array(H, dtype=np.float64))
        if H_arr.shape != (self.measurement_dim, self.state_dim):
            raise ValueError(
                f"H must be {self.measurement_dim}x{self.state_dim}, "
                f"got {H_arr.shape}"
            )
        self.H = H_arr

    # ------------------------------------------------------------------
    # Core Algorithm
    # ------------------------------------------------------------------

    def predict(
        self,
        model: Optional[ModelFunction] = None,
        model_params: Optional[Dict[str, Any]] = None,
    ) -> np.ndarray:
        """Propagate the ensemble forward in time.

        If no model function is provided, uses a simple persistence model
        (state unchanged plus process noise).

        Args:
            model: Callable f(state, params) -> new_state for each member.
            model_params: Parameters passed to the model function.

        Returns:
            Ensemble mean (state_dim,).
        """
        params: Dict[str, Any] = model_params or {}

        for i in range(self.ensemble_size):
            if model is not None:
                self.X[:, i] = model(self.X[:, i], params)
            # Add process noise
            self.X[:, i] += self._rng.normal(
                0, self.process_noise_std, self.state_dim
            )

        # Covariance inflation
        ensemble_mean: np.ndarray = np.mean(self.X, axis=1)
        for i in range(self.ensemble_size):
            self.X[:, i] = (
                ensemble_mean
                + self.inflation_factor * (self.X[:, i] - ensemble_mean)
            )

        logger.debug("Predict: ensemble propagated")
        return ensemble_mean.copy()

    def update(
        self,
        measurement: ArrayLike,
        perturbed_obs: bool = True,
    ) -> np.ndarray:
        """Update the ensemble with a new measurement.

        Uses the stochastic EnKF formulation (perturbed observations)
        or the deterministic ETKF variant if perturbed_obs=False.

        Args:
            measurement: Observation vector (measurement_dim,).
            perturbed_obs: If True, use perturbed-observation EnKF.
                If False, use Ensemble Transform KF (deterministic).

        Returns:
            Updated ensemble mean.

        Raises:
            ValueError: If measurement dimension is incorrect.
        """
        z: np.ndarray = np.atleast_1d(np.array(measurement, dtype=np.float64))

        if z.shape[0] != self.measurement_dim:
            raise ValueError(
                f"Measurement dimension mismatch: expected {self.measurement_dim}, "
                f"got {z.shape[0]}"
            )

        # Ensemble mean
        x_mean: np.ndarray = np.mean(self.X, axis=1)

        # Ensemble anomalies
        A: np.ndarray = self.X - x_mean[:, np.newaxis]  # (state_dim, N)

        # Projected ensemble in observation space
        Y: np.ndarray = self.H @ A  # (measurement_dim, N)

        if perturbed_obs:
            # ---- Stochastic (perturbed observations) EnKF ----
            self._perturbed_obs = np.zeros((self.measurement_dim, self.ensemble_size))
            for i in range(self.ensemble_size):
                self._perturbed_obs[:, i] = z + self._rng.multivariate_normal(
                    np.zeros(self.measurement_dim), self.R
                )

            # Innovation
            innovation: np.ndarray = self._perturbed_obs - self.H @ self.X

            # Kalman gain via ensemble
            YYT: np.ndarray = Y @ Y.T / (self.ensemble_size - 1)
            AYT: np.ndarray = A @ Y.T / (self.ensemble_size - 1)

            try:
                K: np.ndarray = AYT @ np.linalg.inv(YYT + self.R)
            except np.linalg.LinAlgError:
                logger.warning("Singular matrix in K computation, using pseudo-inverse")
                K = AYT @ np.linalg.pinv(YYT + self.R)

            # Update
            self.X = self.X + K @ innovation

        else:
            # ---- Deterministic (ETKF) ----
            # Transform matrix
            Y_centered: np.ndarray = Y  # already centered (A is anomalies)

            try:
                R_inv: np.ndarray = np.linalg.inv(self.R)
                T: np.ndarray = np.linalg.inv(
                    np.eye(self.ensemble_size)
                    + Y_centered.T @ R_inv @ Y_centered / (self.ensemble_size - 1)
                )
            except np.linalg.LinAlgError:
                logger.warning("Using pseudo-inverse in ETKF transform")
                T = np.linalg.pinv(
                    np.eye(self.ensemble_size)
                    + Y_centered.T @ np.linalg.pinv(self.R) @ Y_centered
                    / (self.ensemble_size - 1)
                )

            # Symmetric square root of T
            eigenvalues, eigenvectors = np.linalg.eigh(T)
            eigenvalues = np.maximum(eigenvalues, 0.0)
            T_sqrt: np.ndarray = eigenvectors @ np.diag(np.sqrt(eigenvalues)) @ eigenvectors.T

            # Weight vector
            w: np.ndarray = (
                T
                @ Y_centered.T
                @ np.linalg.pinv(self.R)
                @ (z - self.H @ x_mean)
                / (self.ensemble_size - 1)
            ).flatten()

            # Update
            Wa: np.ndarray = np.sqrt(self.ensemble_size - 1) * T_sqrt
            self.X = (
                x_mean[:, np.newaxis]
                + A @ Wa / np.sqrt(self.ensemble_size - 1)
                + A @ w[:, np.newaxis].T
            )

        # Log
        self._history.append(
            {
                "ensemble_mean": np.mean(self.X, axis=1).copy(),
                "ensemble_std": np.std(self.X, axis=1).copy(),
                "measurement": z.copy(),
            }
        )

        logger.debug("Update: measurement=[%s]", np.array2string(z, precision=4))
        return np.mean(self.X, axis=1)

    def step(
        self,
        measurement: ArrayLike,
        model: Optional[ModelFunction] = None,
        model_params: Optional[Dict[str, Any]] = None,
    ) -> np.ndarray:
        """Full predict-update cycle.

        Args:
            measurement: Observation vector.
            model: Model function for prediction.
            model_params: Model parameters.

        Returns:
            Updated ensemble mean.
        """
        self.predict(model=model, model_params=model_params)
        return self.update(measurement)

    # ------------------------------------------------------------------
    # Ensemble statistics
    # ------------------------------------------------------------------

    def get_ensemble_stats(self) -> Tuple[np.ndarray, np.ndarray]:
        """Return the ensemble mean and standard deviation.

        Returns:
            Tuple of (mean, std), each of shape (state_dim,).
        """
        mean: np.ndarray = np.mean(self.X, axis=1)
        std: np.ndarray = np.std(self.X, axis=1)
        return mean, std

    def get_state(self) -> np.ndarray:
        """Return the current state estimate (ensemble mean).

        Returns:
            State vector (state_dim,).
        """
        return np.mean(self.X, axis=1)

    def get_covariance(self) -> np.ndarray:
        """Return the ensemble-estimated covariance matrix.

        Returns:
            Covariance matrix (state_dim, state_dim).
        """
        x_mean: np.ndarray = np.mean(self.X, axis=1)
        A: np.ndarray = self.X - x_mean[:, np.newaxis]
        return (A @ A.T) / (self.ensemble_size - 1)

    def get_ensemble_members(self) -> np.ndarray:
        """Return all ensemble members.

        Returns:
            Ensemble matrix (state_dim, ensemble_size).
        """
        return self.X.copy()

    # ------------------------------------------------------------------
    # Diagnostics
    # ------------------------------------------------------------------

    def get_history(self) -> List[Dict[str, Any]]:
        """Return filter diagnostic history.

        Returns:
            List of step-wise statistics.
        """
        return list(self._history)

    def reset(self) -> None:
        """Reset the ensemble to initial zero-mean state."""
        self.X = np.zeros((self.state_dim, self.ensemble_size))
        self._history.clear()
        self._perturbed_obs = None
        logger.info("EnsembleKalmanFilter reset")

    def ensemble_spread(self) -> float:
        """Compute the total ensemble spread (trace of covariance).

        Returns:
            Total variance summed across all state dimensions.
        """
        return float(np.trace(self.get_covariance()))


# ---------------------------------------------------------------------------
# Convenience factory
# ---------------------------------------------------------------------------


def create_crop_growth_enkf(
    ensemble_size: int = 50,
) -> EnsembleKalmanFilter:
    """Create an EnKF for crop growth tracking.

    State: [biomass, leaf_area_index, soil_moisture]

    Args:
        ensemble_size: Number of ensemble members.

    Returns:
        Configured EnsembleKalmanFilter.
    """
    enkf: EnsembleKalmanFilter = EnsembleKalmanFilter(
        state_dim=3,
        ensemble_size=ensemble_size,
        measurement_dim=2,  # [observed_biomass, observed_lai]
        process_noise_std=0.02,
        measurement_noise_std=0.1,
        inflation_factor=1.02,
    )

    enkf.set_observation_matrix(
        np.array([[1.0, 0.0, 0.0], [0.0, 1.0, 0.0]])
    )

    return enkf
