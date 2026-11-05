"""Summary metrics for interval estimates of g2(0)."""

from __future__ import annotations

import numpy as np

THRESHOLD = 0.05  # certification threshold on g2(0)


def summarise(draws: np.ndarray, truth: float, threshold: float = THRESHOLD) -> dict[str, float]:
    """Reduce ``(n_rep, n_draw)`` draws to bias, RMSE, coverage and certification rate."""
    med = np.median(draws, axis=1)
    lo, hi = np.quantile(draws, [0.025, 0.975], axis=1)
    up95 = np.quantile(draws, 0.95, axis=1)
    return {
        "bias": float(np.mean(med - truth)),
        "rel_bias": float(np.mean(med - truth) / truth),
        "rmse": float(np.sqrt(np.mean((med - truth) ** 2))),
        "coverage": float(np.mean((lo <= truth) & (truth <= hi))),
        "width": float(np.mean(hi - lo)),
        "cert_rate": float(np.mean(up95 < threshold)),
    }
