"""Experiment definitions. Each function returns a tidy ``pandas.DataFrame`` of per-seed metrics."""

from __future__ import annotations

import numpy as np
import pandas as pd

from .estimators import estimate
from .eventsim import EventConfig, simulate_event_histogram
from .metrics import summarise
from .model import PREREG_WINDOW, WINDOWS, Scenario, simulate_histograms

#: Named blinking regimes: (bunching amplitude b, correlation time in pulse periods).
BLINK = {"none": (0.0, 10.0), "moderate": (0.25, 10.0), "heavy": (1.0, 30.0)}
MAIN = ("naive_all", "naive_far", "envelope")


def _rng(seed: int, *key: int) -> np.random.Generator:
    return np.random.default_rng(np.random.SeedSequence([seed, *key]))


def _rho_hat(s: Scenario, n_rep: int, rng: np.random.Generator) -> np.ndarray:
    return np.clip(s.rho + s.rho_offset + s.rho_sigma * rng.standard_normal(n_rep), 0.3, 1.0)


def evaluate(
    s: Scenario, estimators: tuple[str, ...], seed: int, key: int, n_rep: int, n_draw: int = 600,
    window: int = PREREG_WINDOW,
) -> list[dict]:
    """Simulate ``n_rep`` measurements of ``s`` and score every estimator on the same data."""
    rng = _rng(seed, key)
    n0, y = simulate_histograms(s, n_rep, rng)
    rh = _rho_hat(s, n_rep, rng)
    rows = []
    for name in estimators:
        d = estimate(name, n0[:, window], y[:, :, window], rh, s.rho_sigma, rng, n_draw)
        rows.append({"seed": seed, "estimator": name, **summarise(d, s.eps)})
    return rows


def _tag(rows: list[dict], **kw) -> list[dict]:
    return [{**kw, **r} for r in rows]


def exp_bias_map(seeds: list[int], n_rep: int, quick: bool) -> pd.DataFrame:
    """E1: bias / RMSE / coverage over blinking amplitude b and correlation time tau_b."""
    bs = [0.0, 0.5] if quick else [0.0, 0.1, 0.25, 0.5, 1.0]
    taus = [3.0, 30.0] if quick else [3.0, 10.0, 30.0, 100.0]
    rows = []
    for i, b in enumerate(bs):
        for j, t in enumerate(taus):
            s = Scenario(b=b, tau_b=t)
            for seed in seeds:
                rows += _tag(evaluate(s, MAIN, seed, 100 + 10 * i + j, n_rep),
                             exp="E1", b=b, tau_b=t, eps=s.eps, A=s.A)
    return pd.DataFrame(rows)


def exp_count_scaling(seeds: list[int], n_rep: int, quick: bool) -> pd.DataFrame:
    """E2: certification power (good source) and false certification (bad source) vs counts."""
    grid = [400.0, 3200.0] if quick else [200.0, 400.0, 800.0, 1600.0, 3200.0, 6400.0, 12800.0]
    rows = []
    for bi, (name, (b, t)) in enumerate(BLINK.items()):
        for ai, A in enumerate(grid):
            for ei, eps in enumerate((0.03, 0.08)):
                s = Scenario(eps=eps, b=b, tau_b=t, A=A)
                for seed in seeds:
                    rows += _tag(evaluate(s, MAIN, seed, 200 + 100 * bi + 10 * ai + ei, n_rep),
                                 exp="E2", blink=name, b=b, tau_b=t, eps=eps, A=A)
    return pd.DataFrame(rows)


def exp_ablation(seeds: list[int], n_rep: int, quick: bool) -> pd.DataFrame:
    """E3: remove one component of the proposed estimator at a time."""
    variants = ("envelope", "envelope_best_tau", "envelope_no_denom", "naive_far")
    rows = []
    for bi, (name, (b, t)) in enumerate(BLINK.items()):
        s = Scenario(b=b, tau_b=t, A=1600.0)
        for seed in seeds:
            rows += _tag(evaluate(s, variants, seed, 600 + bi, n_rep),
                         exp="E3", blink=name, b=b, tau_b=t, eps=s.eps, A=s.A)
    return pd.DataFrame(rows)


def exp_calibration(seeds: list[int], n_rep: int, quick: bool) -> pd.DataFrame:
    """E4: false certification of a marginal source (g2 = 0.06 vs threshold 0.05) under a systematic error in rho."""
    rhos = [1.0, 0.9] if quick else [1.0, 0.97, 0.94, 0.9, 0.85]
    offs = [-0.02, 0.02] if quick else [-0.02, -0.01, 0.0, 0.01, 0.02]
    rows = []
    for ri, rho in enumerate(rhos):
        for oi, off in enumerate(offs):
            s = Scenario(eps=0.06, b=0.25, tau_b=10.0, rho=rho, A=1600.0, rho_offset=off)
            for seed in seeds:
                rows += _tag(evaluate(s, ("naive_far", "envelope"), seed, 700 + 10 * ri + oi, n_rep),
                             exp="E4", rho=rho, rho_offset=off, eps=s.eps)
    return pd.DataFrame(rows)


def exp_window(seeds: list[int], n_rep: int, quick: bool) -> pd.DataFrame:
    """E5: pre-registered window (2 lifetimes) vs window chosen to minimise the estimate."""
    rows = []
    cases = [(0.08, 400.0), (0.08, 1600.0), (0.03, 400.0), (0.03, 1600.0)]
    if quick:
        cases = cases[:2]
    for ci, (eps, A) in enumerate(cases):
        s = Scenario(eps=eps, b=0.25, tau_b=10.0, A=A)
        for seed in seeds:
            rng = _rng(seed, 800 + ci)
            n0, y = simulate_histograms(s, n_rep, rng)
            rh = _rho_hat(s, n_rep, rng)
            for name in ("naive_far", "envelope"):
                draws = np.stack([estimate(name, n0[:, w], y[:, :, w], rh, s.rho_sigma, rng, 400)
                                  for w in range(len(WINDOWS))])  # (W, R, D)
                med = np.median(draws, axis=2)  # (W, R)
                pick = med.argmin(axis=0)
                shop = draws[pick, np.arange(n_rep)]
                for mode, d in (("pre-registered", draws[PREREG_WINDOW]), ("data-selected", shop)):
                    rows.append({"exp": "E5", "seed": seed, "eps": eps, "A": A, "estimator": name,
                                 "mode": mode, **summarise(d, eps)})
    return pd.DataFrame(rows)


def exp_validation(quick: bool, seed: int = 0) -> pd.DataFrame:
    """E0: compare the peak-area model against the pulse-level simulation."""
    cfg = EventConfig(n_pulses=400_000 if quick else 3_000_000)
    rng = _rng(seed, 1)
    n0, y = simulate_event_histogram(cfg, rng)
    rho, b = cfg.rho, cfg.b
    k = np.arange(1, cfg.max_lag + 1)
    shape_pred = 1.0 + rho**2 * b * np.exp(-k / cfg.tau_b)
    plateau = y[0, -10:].sum() / shape_pred[-10:].sum()
    shape_obs = y[0] / plateau
    center_pred = rho**2 * (1 + b) * cfg.eps + 1 - rho**2
    rows = [{
        "quantity": "side-peak envelope, mean abs. relative deviation",
        "observed": float(np.mean(np.abs(shape_obs / shape_pred - 1))), "predicted": 0.0,
    }, {
        "quantity": "central peak / plateau",
        "observed": float(n0[0] / plateau * 2.0), "predicted": float(center_pred),
    }]
    rh = np.array([rho])
    for name in ("naive_far", "envelope"):
        d = estimate(name, n0.astype(float), y.astype(float), rh, 0.003, rng, 4000)
        lo, med, hi = np.quantile(d, [0.025, 0.5, 0.975])
        rows.append({"quantity": f"g2(0) estimate, {name}", "observed": float(med),
                     "predicted": cfg.eps, "ci_lo": float(lo), "ci_hi": float(hi)})
    out = pd.DataFrame(rows)
    out["n_pulses"] = cfg.n_pulses
    out["rho"] = rho
    return out
