"""Aggregate per-seed result tables into mean +/- std summaries and headline numbers."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

METRICS = ["bias", "rel_bias", "rmse", "coverage", "width", "cert_rate"]


def mean_std(df: pd.DataFrame, keys: list[str]) -> pd.DataFrame:
    """Mean and across-seed standard deviation of every metric, grouped by ``keys``."""
    g = df.groupby(keys)[METRICS]
    out = g.mean().add_suffix("_mean").join(g.std(ddof=1).add_suffix("_std"))
    return out.reset_index()


def counts_for_power(e2: pd.DataFrame, level: float = 0.9) -> pd.DataFrame:
    """Smallest plateau count A (per seed) at which the certification rate of a good source >= level."""
    good = e2[np.isclose(e2["eps"], 0.03)]
    rows = []
    for (blink, est, seed), g in good.groupby(["blink", "estimator", "seed"]):
        ok = g[g["cert_rate"] >= level].sort_values("A")
        rows.append({"blink": blink, "estimator": est, "seed": seed,
                     "A_required": float(ok["A"].iloc[0]) if len(ok) else np.nan})
    return pd.DataFrame(rows)


def summarise_all(res: Path) -> dict:
    """Build the headline numbers quoted in the README (all derived from ``results/*.csv``)."""
    e1 = pd.read_csv(res / "e1_bias_map.csv")
    e2 = pd.read_csv(res / "e2_count_scaling.csv")
    e3 = pd.read_csv(res / "e3_ablation.csv")
    e4 = pd.read_csv(res / "e4_calibration.csv")
    e5 = pd.read_csv(res / "e5_window.csv")
    s1 = mean_std(e1, ["estimator", "b", "tau_b"])
    s2 = mean_std(e2, ["blink", "estimator", "eps", "A"])
    s3 = mean_std(e3, ["blink", "estimator"])
    s4 = mean_std(e4, ["estimator", "rho", "rho_offset"])
    s5 = mean_std(e5, ["estimator", "eps", "A", "mode"])
    req = counts_for_power(e2)
    req_s = (req.groupby(["blink", "estimator"])["A_required"].agg(["mean", "std", "count"]).reset_index())
    s1.to_csv(res / "e1_summary.csv", index=False)
    s2.to_csv(res / "e2_summary.csv", index=False)
    s3.to_csv(res / "e3_summary.csv", index=False)
    s4.to_csv(res / "e4_summary.csv", index=False)
    s5.to_csv(res / "e5_summary.csv", index=False)
    req_s.to_csv(res / "e2_counts_required.csv", index=False)
    # overall error across the E1 grid, per estimator
    grid = (e1.groupby(["estimator", "seed"])[["rmse", "coverage"]].mean().groupby("estimator").agg(["mean", "std"]))
    grid.columns = ["_".join(c) for c in grid.columns]
    heavy = s1[(s1["b"] == s1["b"].max())]
    return {
        "e1_grid_average": grid.reset_index().to_dict(orient="records"),
        "e1_worst_cell_by_estimator": heavy.to_dict(orient="records"),
    }

