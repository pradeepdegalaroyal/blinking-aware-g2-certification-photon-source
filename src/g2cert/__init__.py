"""g2cert: blinking-aware certification of g2(0) for pulsed single-photon sources."""

from .model import Scenario, WINDOWS, simulate_histograms
from .estimators import ESTIMATORS, estimate

__all__ = ["Scenario", "WINDOWS", "simulate_histograms", "ESTIMATORS", "estimate"]
__version__ = "0.1.0"
