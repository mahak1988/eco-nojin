"""
Kalman Filter for Sensor Data Assimilation
===========================================

Implements a classic Kalman filter for fusing noisy sensor
measurements into optimal state estimates.

Mathematical Background:
    State prediction:  x_k = F * x_{k-1} + B * u_k + w_k
    Measurement:       z_k = H * x_k + v_k
    Where w_k ~ N(0, Q) and v_k ~ N(0, R)

Applications in Econojin:
    - Soil moisture estimation from multiple sensors
    - Temperature field reconstruction
    - Crop growth state tracking
    - Economic indicator smoothing

Examples:
    >>> kf = KalmanFilter(state_dim=4, measurement_dim=2)
    >>> kf.predict()
    >>> kf.update(measurement=np.array([25.3, 0.65]))
    >>> state = kf.get_state()
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional, Tuple, Union

import numpy as np

logger = logging.getLogger(__name__)

# Type aliases
ArrayLike = Union[List[float], np.ndarray]
MatrixLike = Union[List[List[float]], np.ndarray]


class KalmanFilter:
    """Classic Kalman filter for linear state estimation.

    Maintains state mean and covariance, performing predict-update
    cycles as new measurements arrive.

    Attributes:
        state_dim: Dimension of the state vector.
        measurement_dim: Dimension of the measurement vector.
        F: State transition matrix.
        H: Observation matrix.
        Q: Process noise covariance.
        R: Measurement noise covariance.
        x: Current state estimate.
        P: Current state covariance.
    """

    def __init__(
        self,
        state_dim: int,
        measurement_dim: int,
        dt: float = 1.0,
        process_noise: float = 0.01,
        measurement_noise: float = 0.1,
    ) -> None:
        """Initialize the Kalman filter.

        Args:
            state_dim: Dimension of the state vector.
            measurement_dim: Dimension of the measurement vector.
            dt: Time step for discrete-time dynamics.
            process_noise: Process noise standard deviation scalar.
            measurement_noise: Measurement noise standard deviation scalar.

        Raises:
            ValueError: If dimensions are non-positive.
        """
        if state_dim <= 0 or measurement_dim <= 0:
            raise ValueError(
                f"Dimensions must be positive: state_dim={state_dim}, "
                f"measurement_dim={measurement_dim}"
            )

        self.state_dim: int = state_dim
        self.measurement_dim: int = measurement_dim
        self.dt: float = dt

        # State transition matrix (identity + dt for continuous models)
        self.F: np.ndarray = np.eye(state_dim)

        # Observation matrix (identity padded/truncated)
        self.H: np.ndarray = np.zeros((measurement_dim, state_dim))
        self.H[:measurement_dim, :measurement_dim] = np.eye(
            min(measurement_dim, state_dim)
        )

        # Control matrix (optional)
        self.B: Optional[np.ndarray] = None

        # Process noise covariance
        self.Q: np.ndarray = np.eye(state_dim) * (process_noise ** 2)

        # Measurement noise covariance
        self.R: np.ndarray = np.eye(measurement_dim) * (measurement_noise ** 2)

        # State estimate (start at origin)
        self.x: np.ndarray = np.zeros(state_dim)

        # State covariance (initially high uncertainty)
        self.P: np.ndarray = np.eye(state_dim) * 100.0

        # History for diagnostics
        self._history: List[Dict[str, Any]] = []

        logger.info(
            "KalmanFilter initialized: state_dim=%d, meas_dim=%d, dt=%.2f",
            state_dim,
            measurement_dim,
            dt,
        )

    # ------------------------------------------------------------------
    # Configuration
    # ------------------------------------------------------------------

    def set_transition_matrix(self, F: ArrayLike) -> None:
        """Set the state transition matrix.

        Args:
            F: State transition matrix of shape (state_dim, state_dim).

        Raises:
            ValueError: If shape does not match.
        """
        F_arr: np.ndarray = np.atleast_2d(np.array(F, dtype=np.float64))
        if F_arr.shape != (self.state_dim, self.state_dim):
            raise ValueError(
                f"F must be {self.state_dim}x{self.state_dim}, got {F_arr.shape}"
            )
        self.F = F_arr

    def set_observation_matrix(self, H: ArrayLike) -> None:
        """Set the observation matrix.

        Args:
            H: Observation matrix of shape (measurement_dim, state_dim).

        Raises:
            ValueError: If shape does not match.
        """
        H_arr: np.ndarray = np.atleast_2d(np.array(H, dtype=np.float64))
        if H_arr.shape != (self.measurement_dim, self.state_dim):
            raise ValueError(
                f"H must be {self.measurement_dim}x{self.state_dim}, got {H_arr.shape}"
            )
        self.H = H_arr

    def set_noise_covariances(
        self,
        Q: Optional[ArrayLike] = None,
        R: Optional[ArrayLike] = None,
    ) -> None:
        """Set process and/or measurement noise covariance matrices.

        Args:
            Q: Process noise covariance (state_dim x state_dim).
            R: Measurement noise covariance (meas_dim x meas_dim).

        Raises:
            ValueError: If shapes are invalid.
        """
        if Q is not None:
            Q_arr: np.ndarray = np.atleast_2d(np.array(Q, dtype=np.float64))
            if Q_arr.shape != (self.state_dim, self.state_dim):
                raise ValueError(
                    f"Q must be {self.state_dim}x{self.state_dim}, got {Q_arr.shape}"
                )
            self.Q = Q_arr

        if R is not None:
            R_arr: np.ndarray = np.atleast_2d(np.array(R, dtype=np.float64))
            if R_arr.shape != (self.measurement_dim, self.measurement_dim):
                raise ValueError(
                    f"R must be {self.measurement_dim}x{self.measurement_dim}, "
                    f"got {R_arr.shape}"
                )
            self.R = R_arr

    # ------------------------------------------------------------------
    # Core Algorithm
    # ------------------------------------------------------------------

    def predict(self, u: Optional[ArrayLike] = None) -> np.ndarray:
        """Perform the prediction step (time update).

        Projects the state and covariance forward in time.

        Args:
            u: Optional control input vector of shape (control_dim,).

        Returns:
            Predicted state vector.

        Raises:
            RuntimeError: If control input is provided but B is not set.
        """
        # State prediction
        self.x = self.F @ self.x

        if u is not None:
            if self.B is None:
                raise RuntimeError(
                    "Control input u provided but B (control matrix) is not set. "
                    "Call set_control_matrix() first."
                )
            u_arr: np.ndarray = np.atleast_1d(np.array(u, dtype=np.float64))
            self.x += self.B @ u_arr

        # Covariance prediction
        self.P = self.F @ self.P @ self.F.T + self.Q

        logger.debug("Predict: state=[%s]", np.array2string(self.x, precision=4))
        return self.x.copy()

    def update(self, measurement: ArrayLike) -> np.ndarray:
        """Perform the update step (measurement update).

        Incorporates a new measurement to refine the state estimate.

        Args:
            measurement: Measurement vector of shape (measurement_dim,).

        Returns:
            Updated state estimate.

        Raises:
            ValueError: If measurement dimension is incorrect.
        """
        z: np.ndarray = np.atleast_1d(np.array(measurement, dtype=np.float64))

        if z.shape[0] != self.measurement_dim:
            raise ValueError(
                f"Measurement dimension mismatch: expected {self.measurement_dim}, "
                f"got {z.shape[0]}"
            )

        # Innovation (measurement residual)
        y: np.ndarray = z - self.H @ self.x

        # Innovation covariance
        S: np.ndarray = self.H @ self.P @ self.H.T + self.R

        # Optimal Kalman gain
        try:
            K: np.ndarray = self.P @ self.H.T @ np.linalg.inv(S)
        except np.linalg.LinAlgError:
            # Fallback: use pseudo-inverse
            logger.warning("S matrix singular, using pseudo-inverse for Kalman gain")
            K = self.P @ self.H.T @ np.linalg.pinv(S)

        # State update
        self.x = self.x + K @ y

        # Covariance update (Joseph form for numerical stability)
        I_KH: np.ndarray = np.eye(self.state_dim) - K @ self.H
        self.P = I_KH @ self.P @ I_KH.T + K @ self.R @ K.T

        # Log history
        self._history.append(
            {
                "state": self.x.copy(),
                "covariance": self.P.copy(),
                "measurement": z.copy(),
                "innovation": y.copy(),
                "kalman_gain": K.copy(),
            }
        )

        logger.debug(
            "Update: measurement=[%s], state=[%s]",
            np.array2string(z, precision=4),
            np.array2string(self.x, precision=4),
        )

        return self.x.copy()

    def step(
        self,
        measurement: ArrayLike,
        u: Optional[ArrayLike] = None,
    ) -> np.ndarray:
        """Perform a full predict-update cycle.

        Args:
            measurement: Measurement vector.
            u: Optional control input.

        Returns:
            Updated state estimate.
        """
        self.predict(u=u)
        return self.update(measurement)

    # ------------------------------------------------------------------
    # State access
    # ------------------------------------------------------------------

    def get_state(self) -> np.ndarray:
        """Return the current state estimate.

        Returns:
            State vector copy.
        """
        return self.x.copy()

    def get_covariance(self) -> np.ndarray:
        """Return the current state covariance.

        Returns:
            Covariance matrix copy.
        """
        return self.P.copy()

    def get_uncertainty(self) -> np.ndarray:
        """Return the state standard deviations (sqrt of diagonal of P).

        Returns:
            Array of standard deviations, one per state element.
        """
        diag: np.ndarray = np.diag(self.P)
        # Clamp negative values (numerical artifacts)
        diag = np.maximum(diag, 0.0)
        return np.sqrt(diag)

    def get_innovation(self, measurement: ArrayLike) -> np.ndarray:
        """Compute the innovation (measurement residual).

        Args:
            measurement: Measurement vector.

        Returns:
            Innovation vector (z - H*x).
        """
        z: np.ndarray = np.atleast_1d(np.array(measurement, dtype=np.float64))
        return z - self.H @ self.x

    # ------------------------------------------------------------------
    # Diagnostics
    # ------------------------------------------------------------------

    def get_history(self) -> List[Dict[str, Any]]:
        """Return the full filter history.

        Returns:
            List of state/meta dicts from each update step.
        """
        return list(self._history)

    def reset(self) -> None:
        """Reset the filter to its initial state."""
        self.x = np.zeros(self.state_dim)
        self.P = np.eye(self.state_dim) * 100.0
        self._history.clear()
        logger.info("KalmanFilter reset")

    def residual_test(
        self, measurement: ArrayLike, threshold: float = 3.0
    ) -> bool:
        """Test if measurement is consistent with the current state.

        Args:
            measurement: Measurement to test.
            threshold: Mahalanobis distance threshold.

        Returns:
            True if measurement is consistent (not an outlier).
        """
        z: np.ndarray = np.atleast_1d(np.array(measurement, dtype=np.float64))
        innovation: np.ndarray = self.get_innovation(z)
        S: np.ndarray = self.H @ self.P @ self.H.T + self.R

        try:
            S_inv: np.ndarray = np.linalg.inv(S)
            mahalanobis: float = float(
                np.sqrt(innovation.T @ S_inv @ innovation)
            )
            return mahalanobis <= threshold
        except np.linalg.LinAlgError:
            return True  # Cannot reject if S is singular


# ---------------------------------------------------------------------------
# Convenience factory
# ---------------------------------------------------------------------------


def create_soil_moisture_filter(
    num_sensors: int = 3, dt: float = 1.0
) -> KalmanFilter:
    """Create a Kalman filter pre-configured for soil moisture estimation.

    Tracks soil moisture state from multiple sensor readings.

    Args:
        num_sensors: Number of soil moisture sensors.
        dt: Measurement interval in hours.

    Returns:
        Configured KalmanFilter instance.
    """
    kf: KalmanFilter = KalmanFilter(
        state_dim=2,  # [moisture_level, rate_of_change]
        measurement_dim=num_sensors,
        dt=dt,
        process_noise=0.05,
        measurement_noise=0.1,
    )

    # Transition: moisture changes by rate_of_change * dt
    kf.set_transition_matrix(np.array([[1.0, dt], [0.0, 1.0]]))

    # Observation: each sensor reads moisture level directly
    H: np.ndarray = np.zeros((num_sensors, 2))
    H[:, 0] = 1.0
    kf.set_observation_matrix(H)

    return kf


def create_temperature_filter() -> KalmanFilter:
    """Create a Kalman filter for temperature estimation.

    Returns:
        Configured KalmanFilter instance.
    """
    kf: KalmanFilter = KalmanFilter(
        state_dim=2,  # [temperature, trend]
        measurement_dim=1,
        dt=1.0,
        process_noise=0.1,
        measurement_noise=0.5,
    )

    kf.set_transition_matrix(np.array([[1.0, 1.0], [0.0, 1.0]]))
    kf.set_observation_matrix(np.array([[1.0, 0.0]]))

    return kf
