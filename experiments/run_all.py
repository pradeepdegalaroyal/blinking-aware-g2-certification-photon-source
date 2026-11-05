"""Reproduce every result and figure: ``python experiments/run_all.py`` (add ``--quick`` for a smoke run)."""

from __future__ import annotations

import argparse
import json
import platform
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import numpy as np  # noqa: E402

from g2cert import experiments as ex  # noqa: E402
from g2cert import report, tables  # noqa: E402


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--quick", action="store_true", help="tiny smoke run (< 1 minute)")
    ap.add_argument("--seeds", type=int, default=None, help="number of seeds (default 5, quick 2)")
    ap.add_argument("--n-rep", type=int, default=None, help="Monte Carlo repeats per seed")
    ap.add_argument("--skip-figures", action="store_true")
    ap.add_argument("--out", type=Path, default=None, help="output root (default: repo root; temp dir with --quick)")
    args = ap.parse_args()

    quick = args.quick
    seeds = list(range(args.seeds or (2 if quick else 5)))
    n_rep = args.n_rep or (30 if quick else 150)
    root = args.out or (Path(tempfile.gettempdir()) / "g2cert_quick" if quick else ROOT)
    res, fig = root / "results", root / "figures"
    res.mkdir(parents=True, exist_ok=True)
    fig.mkdir(parents=True, exist_ok=True)

    t0 = time.time()
    steps = [
        ("e0_validation", lambda: ex.exp_validation(quick)),
        ("e1_bias_map", lambda: ex.exp_bias_map(seeds, n_rep, quick)),
        ("e2_count_scaling", lambda: ex.exp_count_scaling(seeds, n_rep, quick)),
        ("e3_ablation", lambda: ex.exp_ablation(seeds, n_rep, quick)),
        ("e4_calibration", lambda: ex.exp_calibration(seeds, n_rep, quick)),
        ("e5_window", lambda: ex.exp_window(seeds, n_rep, quick)),
    ]
    for name, fn in steps:
        t = time.time()
        df = fn()
        df.to_csv(res / f"{name}.csv", index=False)
        print(f"{name}: {len(df)} rows, {time.time() - t:.1f} s", flush=True)

    summary = report.summarise_all(res)
    try:  # the README tables index specific grid cells that the reduced --quick grid omits
        tables.make_tables(res)
        tables.hypothesis_checks(res)
    except (IndexError, KeyError):
        if not quick:
            raise
    meta = {
        "quick": quick, "seeds": seeds, "n_rep_per_seed": n_rep,
        "runtime_s": round(time.time() - t0, 1), "python": platform.python_version(),
        "numpy": np.__version__, "platform": platform.platform(),
    }
    (res / "summary.json").write_text(json.dumps({"meta": meta, **summary}, indent=2))
    if not args.skip_figures:
        from g2cert import plots
        plots.make_all(res, fig)
    print(f"done in {time.time() - t0:.1f} s -> {root}")


if __name__ == "__main__":
    main()
