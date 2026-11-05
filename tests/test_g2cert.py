"""Fast unit tests for the g2cert package."""

import numpy as np
import pytest

from g2cert import ESTIMATORS, Scenario, estimate, simulate_histograms
from g2cert.eventsim import EventConfig, simulate_event_histogram, telegraph
from g2cert.metrics import summarise
from g2cert.model import N_SIDE, PREREG_WINDOW, WINDOWS, expected_counts, window_fractions


def test_expected_counts_background_free_no_blinking():
    s = Scenario(eps=0.1, b=0.0, rho=1.0, A=1000.0)
    c, side = expected_counts(s)
    assert c[PREREG_WINDOW] == pytest.approx(100.0)
    assert np.allclose(side[:, PREREG_WINDOW], 2000.0)


def test_windows_nested_and_normalised():
    f = window_fractions()
    assert f[PREREG_WINDOW] == pytest.approx(1.0)
    assert np.all(np.diff(f) > 0)
    rng = np.random.default_rng(0)
    n0, y = simulate_histograms(Scenario(), 20, rng)
    assert n0.shape == (20, len(WINDOWS)) and y.shape == (20, N_SIDE, len(WINDOWS))
    assert np.all(np.diff(n0, axis=1) >= 0) and np.all(np.diff(y, axis=2) >= 0)


def test_simulated_means_match_model():
    s = Scenario(b=0.5, tau_b=10.0, A=500.0)
    n0, y = simulate_histograms(s, 4000, np.random.default_rng(1))
    c, side = expected_counts(s)
    assert n0[:, PREREG_WINDOW].mean() == pytest.approx(c[PREREG_WINDOW], rel=0.03)
    assert y[:, 0, PREREG_WINDOW].mean() == pytest.approx(side[0, PREREG_WINDOW], rel=0.02)


@pytest.mark.parametrize("name", ESTIMATORS)
def test_estimators_unbiased_without_blinking(name):
    s = Scenario(eps=0.1, b=0.0, rho=1.0, A=2000.0, rho_sigma=0.0)
    rng = np.random.default_rng(2)
    n0, y = simulate_histograms(s, 60, rng)
    d = estimate(name, n0[:, PREREG_WINDOW], y[:, :, PREREG_WINDOW], np.ones(60), 0.0, rng, 300)
    assert d.shape == (60, 300)
    assert np.median(d, axis=1).mean() == pytest.approx(0.1, abs=0.02)


def test_envelope_beats_naive_under_strong_blinking():
    s = Scenario(eps=0.03, b=1.0, tau_b=10.0, A=1600.0)
    rng = np.random.default_rng(3)
    n0, y = simulate_histograms(s, 80, rng)
    rh = np.full(80, s.rho)
    rm = {}
    for name in ("naive_far", "envelope"):
        d = estimate(name, n0[:, PREREG_WINDOW], y[:, :, PREREG_WINDOW], rh, s.rho_sigma, rng, 300)
        rm[name] = summarise(d, s.eps)["rmse"]
    assert rm["envelope"] < rm["naive_far"]


def test_telegraph_statistics():
    f, tau = 0.8, 10.0
    st = telegraph(200_000, f, tau, np.random.default_rng(4))
    assert st.mean() == pytest.approx(f, abs=0.02)


def test_event_simulation_matches_peak_area_model():
    cfg = EventConfig(n_pulses=600_000)
    n0, y = simulate_event_histogram(cfg, np.random.default_rng(5))
    k = np.arange(1, cfg.max_lag + 1)
    shape = 1.0 + cfg.rho**2 * cfg.b * np.exp(-k / cfg.tau_b)
    plateau = y[0, -10:].sum() / shape[-10:].sum()
    assert np.mean(np.abs(y[0] / plateau / shape - 1)) < 0.05
    pred = cfg.rho**2 * (1 + cfg.b) * cfg.eps + 1 - cfg.rho**2
    assert n0[0] / plateau * 2.0 == pytest.approx(pred, rel=0.2)


def test_summarise_perfect_estimate():
    d = np.full((10, 50), 0.03) + np.linspace(-1e-3, 1e-3, 50)
    m = summarise(d, 0.03)
    assert m["coverage"] == 1.0 and m["cert_rate"] == 1.0 and abs(m["bias"]) < 1e-9
