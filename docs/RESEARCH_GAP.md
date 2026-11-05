# Research gap

## Scope note on the literature
The literature brief for this study contains **four** papers, all of the role "recent" (none landmark,
review or adjacent). The requested related-work table of at least ten papers from at least three roles
cannot be produced without citing papers that are not in the brief, which this project does not do. The
table below therefore lists all four available papers and states what each does not cover. Physics that is
textbook knowledge in quantum optics (the structure of a pulsed coincidence histogram) is used without a citation.

## State of the art from the brief

| Paper | Year | Role | What it does | What it does NOT cover |
|---|---|---|---|---|
| Srivastava et al., doi:10.1016/j.optcom.2026.133855 | 2027 | recent | Review of orbital angular momentum (OAM) photonics: efficiency, crosstalk and mode-detection benchmarks, deployment readiness. | Metrology of single-photon sources; says validation beyond simulated conditions remains an open priority. |
| Peng et al., doi:10.1016/j.optcom.2026.133879 | 2027 | recent | Passive-decoy semi-quantum key-establishment protocol (quantum key distribution, QKD, family) with a **pre-commitment sampling** rule: the parameter-estimation set is fixed before outcomes are disclosed; bounds are stated as conditional on source and calibration assumptions. | Source characterisation; the pre-commitment idea is not applied to photon-counting statistics. |
| Ma et al., doi:10.1016/j.watres.2026.127204 | 2027 | recent | Hybrid quantum-classical estimation that recovers **physical scale** from normalised quantum-state outputs using anchors and adaptive rescaling. | Photonic hardware; normalisation by a plateau measured on a drifting signal. |
| Huang and Qiu, doi:10.1016/j.jcp.2026.115518 | 2027 | recent | Distributed quantum approximate counting with Grover operators, with noisy intermediate-scale quantum (NISQ) suitability checked in Qiskit. | Counting statistics of real detectors with background and bunching. |

## The gap
A routine measurement of a pulsed single-photon source is the Hanbury Brown-Twiss (HBT) coincidence histogram, whose
central-peak area divided by the side-peak plateau estimates the second-order intensity correlation at zero delay,
g2(0). Three issues, each echoed by one of the papers above, are rarely handled together:

1. **Normalisation is itself an estimate (Ma et al.).** The plateau is read from the side peaks. When the emitter blinks
   (spectral diffusion, charge noise), the side peaks carry a slow bunching envelope, so the plateau is not flat, and
   the central peak carries the same envelope. A flat-plateau normalisation is biased, in either direction.
2. **Choices made after seeing the data (Peng et al.).** The integration window and the set of side peaks are often chosen
   after looking at the histogram, which acts like selecting the estimate. Pre-commitment is the remedy used in the
   key-establishment protocol; it has no counterpart in source certification.
3. **Conditional claims (Peng et al., Srivastava et al.).** The background fraction needed to correct the raw ratio is a
   calibration input; claims should be stated conditionally on it, and its effect on the certificate should be measured.

**Testable question.** For a quantum-dot (QD) source measured with finite counts, background and blinking, does an
estimator that fits the bunching envelope (and divides by the fitted plateau with a blinking-aware denominator) give
smaller bias and honest 95% intervals than flat-plateau normalisation, at no cost when there is no blinking?

**Scale of the evidence.** Simulation only: peak-area Monte Carlo (validated once against a pulse-by-pulse simulation),
no measured data, one detector pair, lags up to 40 pulse periods.

## Hypotheses and success metrics
* **Hypothesis 1 (H1), bias.** In the nine blinking cells with bunching amplitude b >= 0.25 and correlation time
  tau_b <= 30 pulse periods, the envelope estimator has a smaller absolute bias than the best flat-plateau baseline in
  all nine cells and below one third of it in at least seven (true g2(0) = 0.03, 5 seeds).
* **Hypothesis 2 (H2), coverage.** The envelope estimator's 95% interval covers the truth in 93-97% of repeats in every cell
  with tau_b <= 30, while a flat-plateau baseline falls below 90% in at least one cell.
* **Hypothesis 3 (H3), cost.** Without blinking (b = 0) the envelope estimator costs no extra root-mean-square error (RMSE)
  or counts; with blinking it reaches 90% certification power with fewer counts than the baselines while keeping coverage.
* **Hypothesis 4 (H4), pre-commitment.** Choosing the window that minimises the estimate lowers the mean estimate by more
  than 0.003 relative to a pre-registered window.
* **Hypothesis 5 (H5), conditionality.** A systematic error of 0.02 in the background fraction makes the certificate unsafe
  (false-certification rate above 5%) for both estimators.

Each hypothesis can fail; the outcomes, including the failures, are reported in the README.

## Novelty (one sentence)
A blinking-aware, model-averaged normalisation of the HBT plateau with explicit, measured consequences of window
pre-commitment and background-fraction calibration for certifying g2(0) from finite counts.
