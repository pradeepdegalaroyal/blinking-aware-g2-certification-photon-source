"""Figures for the g2(0) certification study (viridis palette, 200 dpi)."""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

DPI = 200
CMAP = plt.get_cmap("viridis")
COL = {"naive_all": CMAP(0.05), "naive_far": CMAP(0.45), "envelope": CMAP(0.8)}
LABEL = {"naive_all": "naive, all 40 side peaks", "naive_far": "naive, 20 outer side peaks",
         "envelope": "envelope fit (proposed)", "envelope_best_tau": "no averaging over tau",
         "envelope_no_denom": "no blinking-aware denominator"}


def _annot(ax, data, fmt, vmin, vmax, xt, yt, xlabel, ylabel, title, cmap="viridis"):
    im = ax.imshow(data, origin="lower", aspect="auto", cmap=cmap, vmin=vmin, vmax=vmax)
    for i in range(data.shape[0]):
        for j in range(data.shape[1]):
            v = data[i, j]
            c = "white" if (v - vmin) / (vmax - vmin + 1e-12) < 0.55 else "black"
            ax.text(j, i, format(v, fmt), ha="center", va="center", color=c, fontsize=7)
    ax.set_xticks(range(len(xt)), [str(x) for x in xt])
    ax.set_yticks(range(len(yt)), [str(y) for y in yt])
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_title(title, fontsize=9)
    return im


def fig_bias_maps(res: Path, out: Path) -> None:
    s = pd.read_csv(res / "e1_summary.csv")
    bs, taus = sorted(s["b"].unique()), sorted(s["tau_b"].unique())
    ests = ["naive_all", "naive_far", "envelope"]
    grids = {e: np.array([[s[(s.estimator == e) & (s.b == b) & (s.tau_b == t)]["bias_mean"].iloc[0]
                           for t in taus] for b in bs]) for e in ests}
    vmax = max(np.abs(g).max() for g in grids.values())
    fig, axes = plt.subplots(1, 3, figsize=(11, 3.8), sharey=True)
    for ax, e in zip(axes, ests):
        im = _annot(ax, grids[e], "+.3f", -vmax, vmax, taus, bs, "blinking time $\\tau_b$ (pulse periods)",
                    "bunching amplitude $b$" if e == ests[0] else "", LABEL[e])
    fig.colorbar(im, ax=axes, label="mean bias of g2(0) estimate (true value 0.03)", shrink=0.9)
    fig.suptitle("Bias of the g2(0) estimate over the blinking plane (mean of 5 seeds)", fontsize=10)
    fig.savefig(out / "fig1_bias_maps.png", dpi=DPI, bbox_inches="tight")
    plt.close(fig)


def fig_rmse_dumbbell(res: Path, out: Path) -> None:
    s = pd.read_csv(res / "e1_summary.csv")
    piv = s.pivot_table(index=["b", "tau_b"], columns="estimator", values="rmse_mean")
    piv = piv.sort_values("naive_far")
    fig, ax = plt.subplots(figsize=(6.5, 6))
    y = np.arange(len(piv))
    for i, (_, r) in enumerate(piv.iterrows()):
        ax.plot([r["naive_far"], r["envelope"]], [i, i], color="0.6", lw=1.5, zorder=1)
    ax.scatter(piv["naive_far"], y, color=COL["naive_far"], s=36, label=LABEL["naive_far"], zorder=2)
    ax.scatter(piv["envelope"], y, color=COL["envelope"], s=36, label=LABEL["envelope"], zorder=2)
    ax.set_yticks(y, [f"b={b:g}, $\\tau_b$={t:g}" for b, t in piv.index], fontsize=7)
    ax.set_xlabel("root-mean-square error of g2(0) (true value 0.03)")
    ax.set_ylabel("blinking scenario")
    ax.set_title("Error per blinking scenario: baseline to proposed", fontsize=10)
    ax.legend(fontsize=8, loc="lower right")
    ax.grid(axis="x", alpha=0.3)
    fig.savefig(out / "fig2_rmse_dumbbell.png", dpi=DPI, bbox_inches="tight")
    plt.close(fig)


def fig_count_scaling(res: Path, out: Path) -> None:
    s = pd.read_csv(res / "e2_summary.csv")
    regimes = ["none", "moderate", "heavy"]
    fig, axes = plt.subplots(2, 3, figsize=(11, 6), sharex=True, sharey=True)
    for c, reg in enumerate(regimes):
        for r, (met, ylab) in enumerate([("cert_rate", "certification rate, good source (g2 = 0.03)"),
                                          ("coverage", "95 % interval coverage of true g2 = 0.03")]):
            ax = axes[r, c]
            for e in ("naive_all", "naive_far", "envelope"):
                d = s[(s.blink == reg) & (s.estimator == e) & np.isclose(s.eps, 0.03)].sort_values("A")
                ax.plot(d["A"], d[f"{met}_mean"], "-o", ms=3, color=COL[e], label=LABEL[e])
                ax.fill_between(d["A"], d[f"{met}_mean"] - d[f"{met}_std"],
                                d[f"{met}_mean"] + d[f"{met}_std"], color=COL[e], alpha=0.2)
            ax.set_xscale("log")
            ax.grid(alpha=0.3)
            if r == 0:
                ax.axhline(0.9, color="k", ls=":", lw=1)
                ax.set_title(f"blinking: {reg}", fontsize=10)
            else:
                ax.axhline(0.95, color="k", ls=":", lw=1)
                ax.set_xlabel("plateau counts per side peak $A$")
            if c == 0:
                ax.set_ylabel(ylab, fontsize=8)
    axes[0, 0].legend(fontsize=7, loc="lower right")
    fig.suptitle("Certification power and interval coverage versus counts (threshold g2(0) < 0.05)", fontsize=11)
    fig.tight_layout()
    fig.savefig(out / "fig3_count_scaling.png", dpi=DPI, bbox_inches="tight")
    plt.close(fig)


def fig_calibration(res: Path, out: Path) -> None:
    s = pd.read_csv(res / "e4_summary.csv")
    rhos, offs = sorted(s["rho"].unique()), sorted(s["rho_offset"].unique())
    fig, axes = plt.subplots(1, 2, figsize=(9, 3.9), sharey=True)
    for ax, e in zip(axes, ["naive_far", "envelope"]):
        g = np.array([[s[(s.estimator == e) & (s.rho == r) & np.isclose(s.rho_offset, o)]["cert_rate_mean"].iloc[0]
                       for o in offs] for r in rhos])
        im = _annot(ax, g, ".2f", 0.0, max(0.2, g.max()), [f"{o:+.2f}" for o in offs], rhos,
                    "systematic error of the signal fraction $\\rho$", "true signal fraction $\\rho$" if e == "naive_far" else "",
                    LABEL[e])
    fig.colorbar(im, ax=axes, label="false-certification rate (source g2 = 0.06; ideal <= 0.05)", shrink=0.9)
    fig.suptitle("Background-fraction miscalibration breaks the certificate", fontsize=10)
    fig.savefig(out / "fig4_calibration_map.png", dpi=DPI, bbox_inches="tight")
    plt.close(fig)


def fig_window(res: Path, out: Path) -> None:
    s = pd.read_csv(res / "e5_summary.csv")
    keys = s[["estimator", "eps", "A"]].drop_duplicates().sort_values(["eps", "A", "estimator"]).values.tolist()
    fig, ax = plt.subplots(figsize=(6.8, 4.2))
    for i, (e, eps, A) in enumerate(keys):
        a = s[(s.estimator == e) & (s.eps == eps) & (s.A == A) & (s["mode"] == "pre-registered")].iloc[0]
        b = s[(s.estimator == e) & (s.eps == eps) & (s.A == A) & (s["mode"] == "data-selected")].iloc[0]
        ax.plot([a["bias_mean"], b["bias_mean"]], [i, i], color="0.6", lw=1.5)
        ax.scatter(a["bias_mean"], i, color=CMAP(0.2), s=40, zorder=3,
                   label="pre-registered window" if i == 0 else None)
        ax.scatter(b["bias_mean"], i, color=CMAP(0.85), s=40, zorder=3,
                   label="window chosen to minimise the estimate" if i == 0 else None)
    ax.axvline(0, color="k", lw=0.8)
    ax.set_yticks(range(len(keys)), [f"{LABEL[e].split(',')[0].split(' (')[0]}, g2={eps:g}, A={A:g}" for e, eps, A in keys], fontsize=7)
    ax.set_xlabel("mean bias of g2(0) estimate")
    ax.set_ylabel("estimator, true g2(0), counts")
    ax.set_title("Cost of choosing the integration window after seeing the data", fontsize=10)
    ax.legend(fontsize=8)
    ax.grid(axis="x", alpha=0.3)
    fig.savefig(out / "fig5_window_selection.png", dpi=DPI, bbox_inches="tight")
    plt.close(fig)


def fig_ablation(res: Path, out: Path) -> None:
    s = pd.read_csv(res / "e3_summary.csv")
    variants = ["naive_far", "envelope_no_denom", "envelope_best_tau", "envelope"]
    regimes = ["none", "moderate", "heavy"]
    fig, axes = plt.subplots(1, 2, figsize=(10, 3.8))
    w = 0.2
    for ax, (m, lab) in zip(axes, [("rmse", "root-mean-square error of g2(0)"), ("coverage", "95 % interval coverage")]):
        for vi, v in enumerate(variants):
            vals = [s[(s.blink == r) & (s.estimator == v)][f"{m}_mean"].iloc[0] for r in regimes]
            err = [s[(s.blink == r) & (s.estimator == v)][f"{m}_std"].iloc[0] for r in regimes]
            ax.bar(np.arange(3) + (vi - 1.5) * w, vals, w, yerr=err, color=CMAP(0.1 + 0.27 * vi),
                   label=LABEL[v], capsize=2)
        ax.set_xticks(range(3), regimes)
        ax.set_xlabel("blinking regime")
        ax.set_ylabel(lab)
        ax.grid(axis="y", alpha=0.3)
    axes[1].axhline(0.95, color="k", ls=":", lw=1)
    axes[1].set_ylim(0.2, 1.02)
    axes[0].legend(fontsize=7)
    fig.suptitle("Ablation of the proposed estimator (true g2 = 0.03, A = 1600)", fontsize=10)
    fig.savefig(out / "fig6_ablation.png", dpi=DPI, bbox_inches="tight")
    plt.close(fig)


def make_all(res: Path, out: Path) -> None:
    """Render every figure from the summary tables in ``res``."""
    for f in (fig_bias_maps, fig_rmse_dumbbell, fig_count_scaling, fig_calibration, fig_window, fig_ablation):
        f(res, out)
