"""Estimators of the intrinsic g2(0) from a coincidence histogram, returning posterior-style draws.

All estimators share the same uncertainty treatment so that differences come from the
*normalisation* only: the central count has a Jeffreys-Gamma posterior ``Gamma(n0 + 1/2)``, the
signal fraction ``rho`` carries its calibration uncertainty, and the plateau uncertainty is
propagated from the fit. Each returns an array of draws of shape ``(n_rep, n_draw)``.

Estimators
----------
``naive_all``  central count over the mean of all side peaks (common practice).
``naive_far``  central count over the mean of the 20 outermost side peaks (stronger baseline).
``envelope``   Poisson maximum-likelihood fit of a bunching envelope ``a + c exp(-k/tau)`` over a
               grid of ``tau`` (plus a constant model), model-averaged with an information
               penalty; the central count is divided by the fitted *plateau* and the signal
               denominator is ``rho^2 + c/a`` (blinking-aware).
Ablated variants: ``envelope_best_tau`` (no averaging over ``tau``) and ``envelope_no_denom``
(plain ``rho^2`` denominator).
"""

from __future__ import annotations

import numpy as np

TAU_GRID = np.geomspace(1.0, 150.0, 16)
N_EM_ITER = 250
ESTIMATORS = ("naive_all", "naive_far", "envelope", "envelope_best_tau", "envelope_no_denom")


def _signal_draws(
    n0: np.ndarray, rho_hat: np.ndarray, rho_sigma: float, n_draw: int, rng: np.random.Generator
) -> tuple[np.ndarray, np.ndarray]:
    lam0 = rng.gamma(n0[:, None] + 0.5, 1.0, size=(len(n0), n_draw))
    rho = np.clip(rho_hat[:, None] + rho_sigma * rng.standard_normal((len(n0), n_draw)), 0.3, 1.0)
    return lam0, rho


def _naive(
    n0: np.ndarray, y: np.ndarray, rho_hat: np.ndarray, rho_sigma: float, n_draw: int,
    rng: np.random.Generator, first: int,
) -> np.ndarray:
    used = y[:, first:]
    m = used.shape[1]
    tot = used.sum(axis=1)
    plateau = tot / (2.0 * m)
    sd = np.sqrt(np.maximum(tot, 1.0)) / (2.0 * m)
    lam0, rho = _signal_draws(n0, rho_hat, rho_sigma, n_draw, rng)
    plat = np.maximum(plateau[:, None] + sd[:, None] * rng.standard_normal(lam0.shape), 1e-9)
    return (lam0 / plat - (1.0 - rho**2)) / rho**2


def _em_fit(y: np.ndarray, e: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Non-negative Poisson fit ``mu_k = a + c e_k`` by multiplicative (EM) updates.

    y: (R, K); e: (M, K). Returns a, c of shape (R, M).
    """
    ym = y[:, None, :]
    mean = y.mean(axis=1)[:, None]
    a = np.repeat(mean, e.shape[0], axis=1)
    c = 0.2 * a
    ee = e[None, :, :]
    se = ee.sum(axis=2)
    for _ in range(N_EM_ITER):
        mu = a[..., None] + c[..., None] * ee
        r = ym / np.maximum(mu, 1e-12)
        a = a * r.mean(axis=2)
        c = c * (r * ee).sum(axis=2) / se
    return a, c


def _envelope(
    n0: np.ndarray, y: np.ndarray, rho_hat: np.ndarray, rho_sigma: float, n_draw: int,
    rng: np.random.Generator, average: bool, blink_denominator: bool,
) -> np.ndarray:
    n_rep, K = y.shape
    k = np.arange(1, K + 1, dtype=float)
    e = np.exp(-k[None, :] / TAU_GRID[:, None])  # (M, K)
    a, c = _em_fit(y, e)
    mu = a[..., None] + c[..., None] * e[None]
    loglik = (y[:, None, :] * np.log(np.maximum(mu, 1e-12)) - mu).sum(axis=2)  # (R, M)
    # information matrix of (a, c) for Poisson identity link
    inv_mu = 1.0 / np.maximum(mu, 1e-12)
    i11 = inv_mu.sum(axis=2)
    i12 = (inv_mu * e[None]).sum(axis=2)
    i22 = (inv_mu * e[None] ** 2).sum(axis=2)
    det = np.maximum(i11 * i22 - i12**2, 1e-12)
    v11, v12, v22 = i22 / det, -i12 / det, i11 / det
    # constant model appended as the last member
    a0 = y.mean(axis=1)
    la0 = (y * np.log(np.maximum(a0[:, None], 1e-12)) - a0[:, None]).sum(axis=1)
    a = np.concatenate([a, a0[:, None]], axis=1)
    c = np.concatenate([c, np.zeros((n_rep, 1))], axis=1)
    v11 = np.concatenate([v11, (a0 / K)[:, None]], axis=1)
    v12 = np.concatenate([v12, np.zeros((n_rep, 1))], axis=1)
    v22 = np.concatenate([v22, np.zeros((n_rep, 1))], axis=1)
    score = np.concatenate([loglik - 3.0, (la0 - 1.0)[:, None]], axis=1)
    if average:
        w = np.exp(score - score.max(axis=1, keepdims=True))
        w /= w.sum(axis=1, keepdims=True)
        cdf = np.cumsum(w, axis=1)
        u = rng.random((n_rep, n_draw))
        idx = np.minimum((u[:, :, None] > cdf[:, None, :]).sum(axis=2), cdf.shape[1] - 1)
    else:
        idx = np.broadcast_to(score.argmax(axis=1)[:, None], (n_rep, n_draw))
    take = lambda arr: np.take_along_axis(arr, idx, axis=1)  # noqa: E731
    ga, gc, g11, g12, g22 = take(a), take(c), take(v11), take(v12), take(v22)
    l11 = np.sqrt(np.maximum(g11, 1e-12))
    l21 = g12 / l11
    l22 = np.sqrt(np.maximum(g22 - l21**2, 0.0))
    z1 = rng.standard_normal(ga.shape)
    z2 = rng.standard_normal(ga.shape)
    da = np.maximum(ga + l11 * z1, 1e-9)
    dc = np.maximum(gc + l21 * z1 + l22 * z2, 0.0)
    lam0, rho = _signal_draws(n0, rho_hat, rho_sigma, n_draw, rng)
    plateau = da / 2.0
    denom = rho**2 + (dc / da if blink_denominator else 0.0)
    return (lam0 / plateau - (1.0 - rho**2)) / denom


def estimate(
    name: str, n0: np.ndarray, y: np.ndarray, rho_hat: np.ndarray, rho_sigma: float,
    rng: np.random.Generator, n_draw: int = 1000,
) -> np.ndarray:
    """Return ``(n_rep, n_draw)`` draws of the intrinsic g2(0) for one window.

    Parameters
    ----------
    name: one of :data:`ESTIMATORS`.
    n0: ``(n_rep,)`` central-peak counts.
    y: ``(n_rep, K)`` pooled side-peak counts.
    rho_hat: ``(n_rep,)`` estimated signal fractions; rho_sigma: their stated 1-sigma uncertainty.
    """
    if name == "naive_all":
        return _naive(n0, y, rho_hat, rho_sigma, n_draw, rng, 0)
    if name == "naive_far":
        return _naive(n0, y, rho_hat, rho_sigma, n_draw, rng, y.shape[1] // 2)
    if name == "envelope":
        return _envelope(n0, y, rho_hat, rho_sigma, n_draw, rng, True, True)
    if name == "envelope_best_tau":
        return _envelope(n0, y, rho_hat, rho_sigma, n_draw, rng, False, True)
    if name == "envelope_no_denom":
        return _envelope(n0, y, rho_hat, rho_sigma, n_draw, rng, True, False)
    raise ValueError(f"unknown estimator {name!r}")
