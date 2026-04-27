# A/B Test Analysis Report — Case 3 (Small Sample)

**Dataset:** `docs/raw/test_fixtures/case3_small_sample.csv`
**Date:** 2026-04-27
**Analyst:** A/B Test Specialist (AI)

---

## I. Executive Summary

| Field | Value |
| :--- | :--- |
| **Primary Result** | **Non-Significant** |
| **Key Metric** | Margin |
| **ATE (Beta)** | −1.95 (−1.86% vs. control mean) |
| **P-value (2-tailed)** | 0.7606 |
| **95% Confidence Interval** | [−15.12, +11.21] |
| **Recommendation** | **No-Go / Do Not Ship** |

> The treatment shows no statistically meaningful effect on margin. The result is far from significant (p = 0.76), and the confidence interval is extremely wide — spanning a loss of 15 points to a gain of 11 points — reflecting the high uncertainty inherent in a 23-unit sample.

---

## II. Layman Description

The tested treatment had virtually no impact on revenue margin: the treatment group averaged $102.93 versus $104.89 for the control group — a difference of less than $2. This difference is nowhere near statistically distinguishable from random chance; with a sample this small and outcomes this variable, we simply cannot tell signal from noise. Until a much larger experiment is run, there is no evidence to support shipping this treatment.

---

## III. Formal Statistical Report

### Pre-Analysis Decisions
- **Variable Type:** Continuous (margin)
- **Analysis Level:** Simple T-Test (no confounders)
- **Outlier Treatment:** None applied (user instruction)
- **Test Direction:** 2-tailed (AI Policy, per methodology)

### Descriptive Statistics

| Metric | Control | Treatment |
| :--- | ---: | ---: |
| N | 12 | 11 |
| Mean | 104.89 | 102.93 |
| Std Dev | 14.57 | 15.79 |
| Min | 89.08 | 87.47 |
| P25 | 95.64 | 90.19 |
| Median | 104.25 | 101.07 |
| P75 | 108.70 | 110.16 |
| Max | 138.54 | 139.75 |
| CV (%) | 13.89% | 15.34% |

### Statistical Calculations

| Quantity | Formula | Value |
| :--- | :--- | ---: |
| **ATE** | $\bar{Y}_t - \bar{Y}_c$ | **−1.9544** |
| **Pooled Std Dev ($\sigma_p$)** | $\sqrt{\frac{(n_t-1)s_t^2 + (n_c-1)s_c^2}{n_t+n_c-2}}$ | 15.1658 |
| **Standard Error** | $\sigma_p \sqrt{\frac{1}{n_t}+\frac{1}{n_c}}$ | 6.3306 |
| **T-Statistic** | $\frac{ATE}{SE}$ | −0.3087 |
| **Degrees of Freedom** | $n_t + n_c - 2$ | 21 |
| **P-value (2-tailed)** | Student t-distribution | **0.7606** |
| **T-critical (α=0.05)** | df=21, 2-tailed | ±2.080 |
| **95% CI** | $ATE \pm t_{crit} \times SE$ | **[−15.12, +11.21]** |

### Significance Assessment

- **Significance threshold:** p < 0.05
- **Observed p-value:** 0.7606 — **fails to meet threshold** ✗
- **95% CI includes 0:** Yes ([−15.12, +11.21]) — **Non-Significant** ✗

> **Verdict: Non-Significant.** We fail to reject $H_0$. There is no evidence that the treatment has a meaningful effect on margin.

---

## IV. Discovery & Deep Dive

### 1. Near-Miss Check
The p-value is 0.7606, well above the 0.20 threshold that would warrant a segment-level breakdown. **No near-miss detected.** There is no subgroup analysis to pursue.

### 2. Mechanism Hunting
The dataset contains only a single outcome metric (`margin`). No secondary behavioral or engagement metrics are available for correlation analysis. Mechanism hunting is not feasible with the current data structure.

### 3. Obfuscation Check (Simpson's Paradox)
There are no sub-group or stratification variables in this dataset. Simpson's Paradox cannot manifest in a single-level analysis. **No obfuscation detected.**

**High-Leverage Observations:** Both groups contain one value near +2.3 standard deviations:
- Control: unit #5 → 138.54 (z = +2.31)
- Treatment: unit #13 → 139.75 (z = +2.33)

These are symmetric in magnitude and position within their respective groups — they effectively cancel out and are not distorting the ATE in either direction.

### 4. Hypothesis Generation

**Why is the effect null or undetectable?**

1. **Critically underpowered experiment.** Cohen's d = 0.13 (a very small effect size). To detect an effect of this magnitude with 80% power at α=0.05 (2-tailed), approximately **946 units per group** would be required — 83× the current treatment group size. The current sample (n=23 total) provides near-zero statistical power; a null result here is essentially uninformative.

2. **High baseline variance obscures the signal.** The coefficient of variation is ~14–15% in both groups, meaning natural unit-to-unit variation in margin is large relative to the treatment effect. Any real treatment signal is being drowned out by inherent noise. A more homogeneous population or a pre-experiment variance reduction (e.g., CUPED/covariate adjustment) would improve sensitivity.

3. **Treatment may genuinely have no effect on margin.** It is equally plausible that the intervention simply does not move the margin needle — the ATE of −$1.95 is not directionally positive, and the distribution shapes of both groups are nearly identical (similar min, max, spread, and CV). The treatment may be affecting a behavioral lever that does not translate to margin for this cohort size and composition.

---

## V. Recommendation

| Decision | Rationale |
| :--- | :--- |
| **No-Go** | Result is non-significant with p = 0.76 and a CI spanning −$15 to +$11 |
| **Re-test Required** | Need ~946 units/group to detect an effect of the current observed magnitude |
| **Next Steps** | (1) Scale the experiment significantly. (2) Consider adding pre-experiment covariates (e.g., historical margin) to reduce variance via regression adjustment. (3) Validate whether the treatment mechanism is expected to impact margin directly or through a mediating metric. |
