# Method

## Generative model (`src/g2cert/model.py`)
Lag k is counted in laser pulse periods. With intrinsic antibunching parameter eps (the g2(0) of the bright state),
blinking bunching amplitude b and correlation time tau_b, signal fraction rho of detector clicks, and plateau
count A per side peak:

* side peak k: mean `A (1 + rho^2 b exp(-k / tau_b))`, pooled over +k and -k,
* central peak: mean `A (rho^2 (1 + b) eps + 1 - rho^2)`.

The central peak carries the envelope value (1 + b) because the two-photon term scales with the squared bright-state
intensity. Counts are Poisson. Within a peak the time profile is a two-sided exponential of one lifetime, so
five nested integration windows (0.5, 1, 2, 3, 5 lifetimes; the pre-registered window is 2) are built from disjoint annuli.
The model is checked against a **pulse-by-pulse simulation** (`eventsim.py`): telegraph blinking, one- and two-photon
emission, a 50:50 beamsplitter, detector efficiency and dark counts (Experiment 0, E0).

## Estimators (`src/g2cert/estimators.py`)
All estimators share the same uncertainty treatment (Jeffreys-Gamma posterior for the central count, normal calibration
uncertainty on rho), so differences arise only from the normalisation.

| Estimator | Normalisation |
|---|---|
| Naive, all 40 side peaks (community-standard baseline) | mean of all side peaks, subtract background with rho^2 |
| Naive, 20 outer side peaks (stronger classical-statistics baseline) | mean of the 20 outermost side peaks |
| **Envelope fit (proposed)** | Poisson maximum-likelihood fit of `a + c exp(-k / tau)` over a 16-point grid of tau plus a constant model (expectation-maximisation updates), models averaged with an information penalty; estimate `(n0 / plateau - (1 - rho^2)) / (rho^2 + c / a)` |

The baselines are the standard peak-ratio estimators of pulsed photon-correlation practice; the brief contains no paper
defining them, so they are not cited.

## Metrics
Bias and RMSE of the posterior median; coverage of the central 95% interval; certification rate = fraction of repeats
whose 95% upper bound is below the threshold 0.05 (power for a good source, g2(0) = 0.03; false-certification rate for a
source above the threshold); counts A needed for 90% power. Mean +/- standard deviation across 5 seeds, 150 Monte
Carlo repeats per seed.

## Experiments
* **E0** validation of the peak-area model against the pulse-level simulation.
* **E1** blinking plane: b in {0, 0.1, 0.25, 0.5, 1} x tau_b in {3, 10, 30, 100}, A = 400, rho = 0.95.
* **E2** count scaling: A from 200 to 12,800 for no, moderate (b = 0.25, tau_b = 10) and heavy (b = 1, tau_b = 30) blinking.
* **E3** ablation (one component removed at a time): averaging over tau, blinking-aware denominator.
* **E4** noise/robustness sweep: true rho in {0.85, 0.9, 0.94, 0.97, 1} x systematic error of rho in {-0.02 ... +0.02}; source g2(0) = 0.06.
* **E5** window pre-registration against minimum-estimate window selection.

## Seeds and budget
Seeds 0-4 (NumPy `SeedSequence` keyed by seed and cell). Central processing unit (CPU) only; no graphics processor is used.
