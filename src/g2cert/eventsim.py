"""Pulse-by-pulse (event-level) simulation used to validate the peak-area model.

A blinking two-level telegraph process switches the emitter between bright and dark. In the
bright state a pulse emits one photon (probability ``p``) or two (probability ``q``, from
re-excitation). Photons split on a 50:50 beamsplitter onto two detectors of efficiency ``eta``;
each detector also fires at random with dark probability ``d`` per pulse. Pulse-pair coincidences
are tallied for every lag.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class EventConfig:
    """Parameters of the event-level simulation."""

    n_pulses: int = 3_000_000
    p: float = 0.30       # one-photon probability per pulse in the bright state
    eps: float = 0.10     # intrinsic g2(0) of the bright state
    b: float = 0.25       # bunching amplitude, b = (1 - f) / f
    tau_b: float = 10.0   # telegraph correlation time (pulse periods)
    eta: float = 0.5      # detection efficiency per detector (incl. beamsplitter loss)
    dark: float = 0.003   # dark-click probability per pulse per detector
    max_lag: int = 40

    @property
    def bright_fraction(self) -> float:
        return 1.0 / (1.0 + self.b)

    @property
    def q(self) -> float:
        """Two-photon probability such that 2 q / (p + 2 q)^2 = eps (fixed-point iteration)."""
        q = 0.5 * self.eps * self.p**2
        for _ in range(50):
            q = 0.5 * self.eps * (self.p + 2.0 * q) ** 2
        return q

    @property
    def rho(self) -> float:
        """Signal fraction of the clicks on one detector."""
        mean_n = self.bright_fraction * (self.p + 2.0 * self.q)
        sig = mean_n * self.eta / 2.0
        return float(sig / (sig + self.dark))


def telegraph(n: int, f: float, tau: float, rng: np.random.Generator) -> np.ndarray:
    """Boolean bright/dark state per pulse; on-fraction ``f``, correlation time ``tau``."""
    leave_on, leave_off = (1.0 - f) / tau, f / tau
    n_runs = int(n * (leave_on + leave_off) * 1.2) + 100
    state = np.empty(0, dtype=bool)
    while state.size < n:
        on_len = rng.geometric(leave_on, n_runs)
        off_len = rng.geometric(leave_off, n_runs)
        lens = np.empty(2 * n_runs, dtype=np.int64)
        lens[0::2], lens[1::2] = on_len, off_len
        state = np.concatenate([state, np.repeat(np.tile([True, False], n_runs), lens)])
    return state[:n]


def simulate_event_histogram(
    cfg: EventConfig, rng: np.random.Generator
) -> tuple[np.ndarray, np.ndarray]:
    """Return ``(n0, y)``: central coincidence count ``(1,)`` and pooled side counts ``(1, max_lag)``."""
    n = cfg.n_pulses
    bright = telegraph(n, cfg.bright_fraction, cfg.tau_b, rng)
    u = rng.random(n)
    n_ph = np.where(u < cfg.p, 1, np.where(u < cfg.p + cfg.q, 2, 0)) * bright
    d1 = np.zeros(n, dtype=bool)
    d2 = np.zeros(n, dtype=bool)
    for j in (1, 2):  # photon index within the pulse; each goes to D1, D2 (eta/2 each) or is lost
        has = n_ph >= j
        v = rng.random(n)
        d1 |= has & (v < cfg.eta / 2.0)
        d2 |= has & (v >= cfg.eta / 2.0) & (v < cfg.eta)
    d1 |= rng.random(n) < cfg.dark
    d2 |= rng.random(n) < cfg.dark
    a, b = d1.astype(np.int64), d2.astype(np.int64)
    n0 = int(np.dot(a, b))
    y = np.empty(cfg.max_lag, dtype=np.int64)
    for k in range(1, cfg.max_lag + 1):
        y[k - 1] = int(np.dot(a[:-k], b[k:]) + np.dot(b[:-k], a[k:]))
    return np.array([n0]), y[None, :]
