# A/B Test Analysis Report — Case 1 (Large Sample, Significant)

**Dataset:** `docs/raw/test_fixtures/case1_large_significant.csv`
**Date:** 2026-04-27
**Analyst:** A/B Test Specialist Agent
**Methodology:** `docs/templates/AB_Analysis_Methodology.md`

---

## Pre-Analysis Declarations

| Parameter | Decision |
| :--- | :--- |
| **Variable Type** | Continuous (`margin`) |
| **Analysis Level** | Simple T-Test (no confounders present in dataset) |
| **Outlier Threshold** | None (no trimming applied — user did not specify; no extreme outliers detected) |
| **Confounders** | None — dataset contains only `unit_id`, `group`, `margin` |
| **Test Type** | Student T-Test with pooled standard deviation (large sample, similar group variances) |
| **Directionality** | 2-tailed (per AI Solution Policy) |

---

## I. Executive Summary

| | |
| :--- | :--- |
| **Primary Result** | **SIGNIFICANT** |
| **Key Metric Impact** | ATE = **+8.24 margin units** (+8.28% relative lift) |
| **P-Value** | **p ≈ 1.28 × 10⁻⁹** (far below α = 0.05) |
| **95% Confidence Interval** | **[+5.58, +10.90]** — does not include 0 |
| **Recommendation** | ✅ **GO** — Ship the treatment |

---

## II. Layman Description

The new treatment produced a clear, statistically robust improvement in margin. On average, units in the treatment group earned about **8.24 more margin units** than those in the control group — equivalent to an **8.3% increase** over the control baseline. We are extremely confident this is a real effect and not due to chance: the probability of observing a difference this large by random luck alone is less than one in a billion.

---

## III. Formal Statistical Report

### Group Descriptive Statistics

| Metric | Control | Treatment |
| :--- | ---: | ---: |
| **N** | 200 | 200 |
| **Mean** | 99.4564 | 107.6929 |
| **Std Dev** | 13.5816 | 13.5574 |
| **Min** | 68.4259 | 61.4242 |
| **Max** | 144.0486 | 147.4800 |

### Inference Results

| Statistic | Value |
| :--- | :--- |
| **ATE** (Ȳ_t − Ȳ_c) | **+8.2365** |
| **Relative Lift** | **+8.28%** over control mean |
| **Pooled Std Dev (σ_p)** | 13.5695 |
| **Standard Error** | 1.3570 |
| **T-Statistic** | **6.07** |
| **Degrees of Freedom** | 398 |
| **P-Value (2-tailed)** | **≈ 1.28 × 10⁻⁹** |
| **95% CI** | **[+5.5769, +10.8962]** |

### Interpretation

- **Significant:** `p < 0.05` ✅ AND 95% CI does not include 0 ✅
- The null hypothesis (H₀: no treatment effect) is **rejected** at the 5% significance level.
- The evidence is overwhelming: a t-statistic of 6.07 is more than 6 standard errors above zero, placing this result deep in the tail of the null distribution.

**Formula applied (Student T-Test with pooled variance):**

$$t = \frac{\bar{Y}_t - \bar{Y}_c}{\sigma_p \sqrt{\frac{1}{n_t} + \frac{1}{n_c}}} = \frac{107.6929 - 99.4564}{13.5695 \times \sqrt{\frac{1}{200} + \frac{1}{200}}} = \frac{8.2365}{1.3570} = 6.07$$

---

## IV. Discovery & Deep Dive

### 1. Near-Miss Assessment

Not applicable — the result is strongly significant (p ≈ 1.28 × 10⁻⁹, well below p < 0.20). No near-miss segment investigation is warranted; the effect is robust at the aggregate level.

### 2. Mechanism Hunting

The dataset contains only the `margin` metric; no secondary behavioral metrics are available for correlation analysis. To understand *how* the treatment drives margin improvement, the following secondary metrics would be valuable additions in a future instrumentation pass:

- **Conversion rate / order volume** — Does the treatment increase the number of transactions, or average margin per transaction?
- **Product mix** — Is the treatment steering users toward higher-margin SKUs?
- **Engagement metrics** — Time-on-site, click-through, or funnel stage that may act as a mediator.

### 3. Obfuscation Check — Simpson's Paradox

With only one column available beyond group assignment, a full Simpson's Paradox check requires subgroup stratification that is not possible here. However, two structural observations provide partial assurance:

1. **Balanced design:** Both groups have exactly n = 200, minimizing group-size-driven aggregation bias.
2. **Similar variance:** σ_control = 13.58, σ_treatment = 13.56 — near-identical dispersion rules out variance-driven paradox scenarios.

No evidence of aggregation reversal is present given the single-metric design.

### 4. Hypothesis Generation

Three qualitative explanations for the observed +8.3% margin lift:

1. **Pricing or upsell nudge:** The treatment likely modified a pricing display, bundle offer, or upsell prompt that successfully shifted users toward higher-margin choices. A ~8% lift in absolute margin without a visible volume signal would be consistent with a margin-mix shift rather than pure volume growth.

2. **Friction reduction in high-margin path:** The treatment may have reduced checkout or selection friction specifically for higher-margin products or services. By making the high-margin option the path of least resistance, the treatment passively captured higher value without requiring active user commitment.

3. **Timing or urgency lever:** A scarcity signal, limited-time offer, or urgency-based UI element may have suppressed discount-seeking behavior, resulting in fewer units sold at reduced margins and an improved average margin per completed transaction.

---

## V. Robustness Notes

| Check | Finding |
| :--- | :--- |
| **Variance equality** | σ_c ≈ σ_t (13.58 vs 13.56) — Student t-test with pooled variance is appropriate |
| **Sample balance** | n_c = n_t = 200 — perfectly balanced; no regression correction needed |
| **Outlier exposure** | 99th pct: control = 128.79, treatment = 136.45; 2 observations above each threshold — negligible influence on means |
| **Large sample validity** | n = 200 per group satisfies Central Limit Theorem assumptions |

---

*Report generated per `docs/templates/AB_Analysis_Methodology.md` and `.claude/skills/ab_test_specialist.md`.*
