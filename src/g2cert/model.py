"""Peak-area generative model of a pulsed Hanbury Brown-Twiss (HBT) coincidence histogram.

Conventions
-----------
* Lag ``k`` is measured in laser pulse periods; ``k = 0`` is the central peak.
* ``eps`` is the *intrinsic* antibunching parameter of the emitter in its bright state.
* Slow blinking (telegraph switching, time scale ``tau_b`` pulse periods, bunching amplitude
  ``b = (1 - f) / f`` for bright fraction ``f``) multiplies every signal-signal coincidence at
  lag ``k`` by ``1 + b exp(-|k| / tau_b)``. The central peak carries the same envelope value
  ``1 + b`` because ``<n(n-1)>`` scales with the squared bright-state intensity.
* ``rho`` is the signal fraction of clicks on each detector (the rest is uncorrelated background).
* Within a peak the coincidence time profile is a two-sided exponential of lifetime ``tau_1``;
  the integration window half-width ``w`` is given in units of ``tau_1``.

Expected counts in one side peak (window ``w``) are ``A (F_w / F_2) (1 + rho^2 b e^{-k/tau_b})``
and in the central peak ``A (F_w / F_2) (rho^2 (1 + b) eps + 1 - rho^2)`` with
``F_w = 1 - exp(-w)``; ``A`` is the plateau count per side peak in the default window ``w = 2``.
"""

from __future__ import annotations

from dataclasses import dataclass, replace

import numpy as np

#: Candidate integration half-widths in units of the emitter lifetime.
WINDOWS: tuple[float, ...] = (0.5, 1.0, 2.0, 3.0, 5.0)
#: Index of the pre-registered window (2 lifetimes).
PREREG_WINDOW: int = 2
#: Number of side peaks (per sign) available in the histogram.
N_SIDE: int = 40


@dataclass(frozen=True)
class Scenario:
    """Physical and acquisition parameters of one simulated measurement."""

    eps: float = 0.03        # intrinsic g2(0) of the bright state
    b: float = 0.25          # blinking bunching amplitude
    tau_b: float = 10.0      # blinking correlation time in pulse periods
    rho: float = 0.95        # signal fraction of detector clicks
    A: float = 400.0         # plateau counts per side peak in the default window
    rho_sigma: float = 0.003  # random calibration uncertainty of rho
    rho_offset: float = 0.0  # unknown systematic calibration offset of rho

    def with_(self, **kw: float) -> "Scenario":
        return replace(self, **kw)


def window_fractions() -> np.ndarray:
    """Fraction of a peak's counts inside each nested window, normalised to the default window."""
    f = 1.0 - np.exp(-np.asarray(WINDOWS))
    return f / f[PREREG_WINDOW]


def expected_counts(s: Scenario) -> tuple[np.ndarray, np.ndarray]:
    """Return (center, side) expected counts per window.

    ``center`` has shape ``(n_windows,)``; ``side`` has shape ``(N_SIDE, n_windows)`` and refers to
    the *pooled* +k and -k peaks (twice the single-peak mean).
    """
    frac = window_fractions()
    k = np.arange(1, N_SIDE + 1)
    side_shape = 1.0 + s.rho**2 * s.b * np.exp(-k / s.tau_b)
    center = s.A * (s.rho**2 * (1.0 + s.b) * s.eps + 1.0 - s.rho**2)
    return center * frac, 2.0 * s.A * side_shape[:, None] * frac[None, :]


def simulate_histograms(
    s: Scenario, n_rep: int, rng: np.random.Generator
) -> tuple[np.ndarray, np.ndarray]:
    """Draw Poisson peak areas for ``n_rep`` independent measurements.

    Nested windows are built from disjoint annuli so that counts in a smaller window are a subset
    of those in a larger one (this matters for the window-selection experiment).

    Returns
    -------
    n0 : ndarray, shape (n_rep, n_windows)
        Central-peak counts per window.
    y : ndarray, shape (n_rep, N_SIDE, n_windows)
        Pooled (+k and -k) side-peak counts per window.
    """
    mu0, muy = expected_counts(s)

    def nested(mu: np.ndarray) -> np.ndarray:
        inc = np.diff(mu, axis=-1, prepend=0.0)
        draws = rng.poisson(np.broadcast_to(inc, (n_rep,) + inc.shape))
        return np.cumsum(draws, axis=-1)

    return nested(mu0), nested(muy)
