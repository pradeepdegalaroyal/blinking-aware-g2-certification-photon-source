"""Markdown result tables (mean +/- std over seeds) written to ``results/tables.md``."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

NAMES = {
    "naive_all": "naive, all 40 side peaks",
    "naive_far": "naive, 20 outer side peaks",
    "envelope": "envelope fit (proposed)",
    "envelope_best_tau": "ablation: no averaging over tau",
    "envelope_no_denom": "ablation: no blinking-aware denominator",
}


def _pm(m: float, s: float, d: int = 3) -> str:
    return f"{m:.{d}f} ± {s:.{d}f}" if np.isfinite(s) else f"{m:.{d}f}"


def make_tables(res: Path) -> str:
    """Build all README tables from the summary CSVs in ``res`` and save them as ``tables.md``."""
    s1 = pd.read_csv(res / "e1_summary.csv")
    s2 = pd.read_csv(res / "e2_summary.csv")
    s3 = pd.read_csv(res / "e3_summary.csv")
    s4 = pd.read_csv(res / "e4_summary.csv")
    s5 = pd.read_csv(res / "e5_summary.csv")
    rq = pd.read_csv(res / "e2_counts_required.csv")
    e0 = pd.read_csv(res / "e0_validation.csv")
    out: list[str] = []

    out += ["### Table 0 (E0): peak-area model against the pulse-level simulation", "",
            "| quantity | observed | model or truth | 95% interval |", "|---|---|---|---|"]
    for _, r in e0.iterrows():
        ci = f"[{r.ci_lo:.3f}, {r.ci_hi:.3f}]" if np.isfinite(r.get("ci_lo", np.nan)) else "-"
        out.append(f"| {r.quantity} | {r.observed:.4f} | {r.predicted:.4f} | {ci} |")

    out += ["", "### Table 1 (E1): selected blinking cells, true g2(0) = 0.03, A = 400", "",
            "| b | tau_b | estimator | bias | RMSE | 95% coverage |", "|---|---|---|---|---|---|"]
    for b, t in [(0.0, 30.0), (0.5, 3.0), (0.5, 30.0), (1.0, 10.0), (1.0, 30.0), (1.0, 100.0)]:
        for e in ("naive_all", "naive_far", "envelope"):
            r = s1[(s1.estimator == e) & (s1.b == b) & (s1.tau_b == t)].iloc[0]
            out.append(f"| {b:g} | {t:g} | {NAMES[e]} | {_pm(r.bias_mean, r.bias_std, 4)} | "
                       f"{_pm(r.rmse_mean, r.rmse_std, 4)} | {_pm(r.coverage_mean, r.coverage_std, 3)} |")

    out += ["", "### Table 2 (E2): counts for 90% certification power (good source 0.03, threshold 0.05)", "",
            "| blinking | estimator | smallest A reaching 90% power | seeds reaching it (of 5) | "
            "power at A = 3200 | coverage at A = 3200 |", "|---|---|---|---|---|---|"]
    for blink in ("none", "moderate", "heavy"):
        for e in ("naive_all", "naive_far", "envelope"):
            r = rq[(rq.blink == blink) & (rq.estimator == e)]
            c = s2[(s2.blink == blink) & (s2.estimator == e) & np.isclose(s2.eps, 0.03) & (s2.A == 3200)].iloc[0]
            n = int(r["count"].iloc[0]) if len(r) else 0
            val = f"{r['mean'].iloc[0]:.0f}" if n > 0 else "not reached up to 12800"
            out.append(f"| {blink} | {NAMES[e]} | {val} | {n} | {_pm(c.cert_rate_mean, c.cert_rate_std)} | "
                       f"{_pm(c.coverage_mean, c.coverage_std)} |")

    out += ["", "### Table 3 (E3): ablation at A = 1600, true g2(0) = 0.03", "",
            "| blinking | variant | bias | RMSE | 95% coverage | mean interval width |", "|---|---|---|---|---|---|"]
    for blink in ("none", "moderate", "heavy"):
        for e in ("naive_far", "envelope_no_denom", "envelope_best_tau", "envelope"):
            r = s3[(s3.blink == blink) & (s3.estimator == e)].iloc[0]
            out.append(f"| {blink} | {NAMES[e]} | {_pm(r.bias_mean, r.bias_std, 4)} | {_pm(r.rmse_mean, r.rmse_std, 4)} | "
                       f"{_pm(r.coverage_mean, r.coverage_std)} | {r.width_mean:.4f} |")

    out += ["", "### Table 4 (E4): false-certification rate, source g2(0) = 0.06, threshold 0.05, A = 1600", "",
            "| true rho | error in rho | naive, 20 outer side peaks | envelope fit (proposed) |", "|---|---|---|---|"]
    for rho in (1.0, 0.9):
        for off in (-0.02, -0.01, 0.0, 0.01):
            vals = []
            for e in ("naive_far", "envelope"):
                r = s4[(s4.estimator == e) & (s4.rho == rho) & np.isclose(s4.rho_offset, off)].iloc[0]
                vals.append(_pm(r.cert_rate_mean, r.cert_rate_std))
            out.append(f"| {rho:g} | {off:+.2f} | {vals[0]} | {vals[1]} |")

    out += ["", "### Table 5 (E5): pre-registered window against window chosen to minimise the estimate", "",
            "| true g2(0) | A | estimator | window | bias | 95% coverage | certification rate |",
            "|---|---|---|---|---|---|---|"]
    for _, r in s5.sort_values(["eps", "A", "estimator", "mode"]).iterrows():
        out.append(f"| {r.eps:g} | {r.A:g} | {NAMES[r.estimator]} | {r['mode']} | {_pm(r.bias_mean, r.bias_std, 4)} | "
                   f"{_pm(r.coverage_mean, r.coverage_std)} | {_pm(r.cert_rate_mean, r.cert_rate_std)} |")
    text = "\n".join(out) + "\n"
    (res / "tables.md").write_text(text, encoding="utf-8")
    return text


def hypothesis_checks(res: Path) -> dict:
    """Numbers used to accept or reject the pre-stated hypotheses (saved to ``hypotheses.json``)."""
    import json

    s1 = pd.read_csv(res / "e1_summary.csv")
    piv = s1.pivot_table(index=["b", "tau_b"], columns="estimator", values=["bias_mean", "rmse_mean", "coverage_mean"])
    blink = piv[(piv.index.get_level_values("b") >= 0.25) & (piv.index.get_level_values("tau_b") <= 30)]
    ratio_far = (blink["bias_mean"]["envelope"].abs() / blink["bias_mean"]["naive_far"].abs())
    ratio_all = (blink["bias_mean"]["envelope"].abs() / blink["bias_mean"]["naive_all"].abs())
    covered = piv["coverage_mean"]["envelope"]
    inside = piv[piv.index.get_level_values("tau_b") <= 30]["coverage_mean"]["envelope"]
    out = {
        "H1_cells_b>=0.25_tau<=30": int(len(blink)),
        "H1_cells_envelope_abs_bias_below_naive_far": int((ratio_far < 1).sum()),
        "H1_cells_envelope_abs_bias_below_naive_all": int((ratio_all < 1).sum()),
        "H1_cells_envelope_abs_bias_below_one_third_of_naive_far": int((ratio_far < 1 / 3).sum()),
        "H1_median_abs_bias_ratio_vs_naive_far": float(ratio_far.median()),
        "H1_median_abs_bias_ratio_vs_naive_all": float(ratio_all.median()),
        "H1_mean_rmse_ratio_vs_naive_far": float((blink["rmse_mean"]["envelope"] / blink["rmse_mean"]["naive_far"]).mean()),
        "H2_envelope_coverage_min_tau<=30": float(inside.min()),
        "H2_envelope_coverage_max_tau<=30": float(inside.max()),
        "H2_envelope_coverage_tau100_b1": float(covered.loc[(1.0, 100.0)]),
        "H2_naive_far_coverage_min_tau<=30": float(piv[piv.index.get_level_values("tau_b") <= 30]["coverage_mean"]["naive_far"].min()),
        "H2_naive_all_coverage_min_tau<=30": float(piv[piv.index.get_level_values("tau_b") <= 30]["coverage_mean"]["naive_all"].min()),
    }
    (res / "hypotheses.json").write_text(json.dumps(out, indent=2))
    return out
