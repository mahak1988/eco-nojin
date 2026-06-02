"""
GR4J Conceptual Rainfall-Runoff Model
======================================
Implementation of the GR4J daily lumped hydrological model.
Open source alternative for catchment-scale hydrology.

Reference: Perrin et al. (2003), "Improvement of a parsimonious model for streamflow simulation"
"""

import numpy as np
from dataclasses import dataclass
from typing import Dict, Optional


@dataclass
class GR4JParams:
    """GR4J model parameters"""
    x1: float = 300  # Production store capacity (mm)
    x2: float = 0.5  # Groundwater exchange coefficient (mm)
    x3: float = 20   # One-day-ahead routing store capacity (mm)
    x4: float = 1.5  # Time base of unit hydrograph UH1 (days)


class GR4JModel:
    """
    GR4J daily lumped rainfall-runoff model.

    Four parameters:
    - x1: Production store capacity (mm)
    - x2: Groundwater exchange coefficient (mm)
    - x3: Routing store capacity (mm)
    - x4: Time base of unit hydrograph (days)
    """

    def __init__(self, params: Optional[GR4JParams] = None):
        self.params = params or GR4JParams()
        self.state = self._init_state()

    def _init_state(self) -> Dict:
        """Initialize model state variables"""
        return {
            'production_store': 0,  # mm
            'routing_store': 0,     # mm
            'uh1_store': np.zeros(int(self.params.x4)),  # Unit hydrograph 1
            'uh2_store': np.zeros(int(2 * self.params.x4)),  # Unit hydrograph 2
        }

    def run(self, precip: np.ndarray, pet: np.ndarray,
            start_date: str, end_date: str) -> Dict:
        """
        Run GR4J simulation.

        Parameters:
        -----------
        precip : np.ndarray
            Daily precipitation (mm/day)
        pet : np.ndarray
            Daily potential evapotranspiration (mm/day)
        start_date, end_date : str
            Simulation period
        """
        n_days = len(precip)
        discharge = np.zeros(n_days)
        et_actual = np.zeros(n_days)
        soil_moisture = np.zeros(n_days)

        for t in range(n_days):
            # Production store
            p_net, et_prod, ps = self._production_store(
                precip[t], pet[t], self.state['production_store']
            )

            # Percolation and routing
            pr = p_net * 0.9  # 90% to routing
            perc = p_net * 0.1  # 10% percolation

            # Unit hydrographs
            uh1_out, uh2_out = self._unit_hydrographs(pr + perc)

            # Groundwater exchange
            exchange = self.params.x2 * (self.state['routing_store'] / self.params.x3) ** 3.5

            # Update routing store
            self.state['routing_store'] += uh1_out + exchange
            self.state['routing_store'] = max(0, self.state['routing_store'])

            # Discharge from routing store
            q_rout = self.state['routing_store'] * (1 - (1 + (self.state['routing_store'] / self.params.x3) ** 4) ** -0.25)
            self.state['routing_store'] -= q_rout

            # Total discharge
            discharge[t] = q_rout + uh2_out
            et_actual[t] = et_prod
            soil_moisture[t] = self.state['production_store']

        # Calculate metrics if observed data available
        metrics = {}

        return {
            'discharge': discharge,
            'et': et_actual,
            'soil_moisture': soil_moisture,
            'metrics': metrics
        }

    def _production_store(self, p: float, etp: float, ps: float) -> tuple:
        """Production store calculation (Eq. 1-4 in Perrin et al. 2003)"""
        x1 = self.params.x1

        if p >= etp:
            # Wet period
            p_net = x1 * (1 - (ps/x1)**2) * np.tanh(p/x1) / (1 + ps/x1 * np.tanh(p/x1))
            et_prod = etp * (ps/x1) * (2 - ps/x1) * np.tanh(etp/x1) / (1 + (1-ps/x1) * np.tanh(etp/x1))
        else:
            # Dry period
            p_net = 0
            et_prod = ps * (2 - ps/x1) * np.tanh(etp/x1) / (1 + (1-ps/x1) * np.tanh(etp/x1))

        # Update production store
        ps_new = ps + p_net - et_prod
        ps_new = max(0, min(x1, ps_new))
        self.state['production_store'] = ps_new

        return p_net, et_prod, ps_new

    def _unit_hydrographs(self, pr: float) -> tuple:
        """Calculate unit hydrograph outputs"""
        x4 = self.params.x4

        # UH1 ordinates (90% of flow)
        uh1_ords = self._uh_ordinates(x4, 0.9)
        # UH2 ordinates (10% of flow)
        uh2_ords = self._uh_ordinates(2*x4, 0.1)

        # Convolve with effective rainfall
        uh1_out = np.convolve([pr], uh1_ords, mode='full')[0] if len(uh1_ords) > 0 else 0
        uh2_out = np.convolve([pr], uh2_ords, mode='full')[0] if len(uh2_ords) > 0 else 0

        # Update stores
        self.state['uh1_store'] = np.roll(self.state['uh1_store'], 1)
        self.state['uh1_store'][0] = pr * 0.9

        self.state['uh2_store'] = np.roll(self.state['uh2_store'], 1)
        self.state['uh2_store'][0] = pr * 0.1

        return uh1_out, uh2_out

    def _uh_ordinates(self, x4: float, fraction: float) -> np.ndarray:
        """Generate unit hydrograph ordinates"""
        n = int(x4)
        if n <= 0:
            return np.array([])

        # Gamma distribution-based UH
        t = np.arange(1, n+1)
        uh = fraction * (t / x4) ** (x4 - 1) * np.exp(-t / x4) / (x4 * np.math.gamma(x4))
        return uh / np.sum(uh)  # Normalize

    def update_parameters(self, new_params: Dict[str, float]):
        """Update model parameters"""
        for key, value in new_params.items():
            if hasattr(self.params, key):
                setattr(self.params, key, value)
