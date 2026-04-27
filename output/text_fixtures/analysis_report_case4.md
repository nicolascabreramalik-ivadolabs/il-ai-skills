# A/B Test Analysis Report — Case 4 (Missing Data)
**Dataset:** `docs/raw/test_fixtures/case4_missing_data.csv`
**Date:** 2026-04-27
**Analyst:** A/B Test Specialist (Automated)
**Outlier Threshold:** None

---

## I. Executive Summary

| Field | Value |
|:---|:---|
| **Primary Result** | ✅ SIGNIFICANT |
| **Metric** | Margin (continuous) |
| **ATE (Absolute)** | **+6.88** |
| **ATE (Relative)** | **+6.95%** |
| **p-value (2-tailed)** | **3.05 × 10⁻⁶** |
| **95% Confidence Interval** | [3.99, 9.77] |
| **Recommendation** | 🟢 **GO** |

The treatment produced a statistically significant and practically meaningful improvement in margin. The 95% CI is entirely above zero and the p-value is far below the α = 0.05 threshold. Ship the treatment.

---

## II. Layman Description

The experiment tested a change that impacted the margin earned per unit. Across nearly 200 units in each group, the treated units generated on average **6.88 more in margin** than the control units — roughly a **7% improvement**. This result is highly unlikely to be due to chance (odds of seeing this difference randomly are less than 1 in 300,000). The business should have high confidence in rolling this treatment out more broadly.

---

## III. Formal Statistical Report

### Pre-processing

| | Control | Treatment |
|:---|:---|:---|
| **Original rows** | 200 | 200 |
| **Missing (listwise deleted)** | 4 (unit_ids: 16, 43, 100, 151) | 4 (unit_ids: 209, 268, 334, 378) |
| **Effective sample size (n)** | **196** | **196** |

Missing data is symmetric (4 per group) and appears MCAR (Missing Completely At Random); no imputation was applied per the "None" outlier/pre-processing policy.

### Descriptive Statistics

| Statistic | Control | Treatment |
|:---|---:|---:|
| n | 196 | 196 |
| Mean (Ȳ) | 99.008 | 105.891 |
| Std Dev (σ) | 13.471 | 15.646 |
| Median | 99.80 | 105.10 |
| Q1 | 89.27 | 94.50 |
| Q3 | 108.37 | 115.92 |
| IQR | 19.10 | 21.42 |
| Min | 60.41 | 64.43 |
| Max | 132.23 | 144.65 |
| Skewness | −0.119 | +0.172 |

### Statistical Test

**Variable Type:** Continuous → Student t-test (pooled variance, 2-tailed)
*(Welch t-test was computed and yields identical t-stat due to near-equal group sizes; reported together.)*

| Component | Value |
|:---|---:|
| ATE = Ȳ_t − Ȳ_c | **+6.8831** |
| Pooled Std Dev (σ_p) | 14.5993 |
| Standard Error (SE) | 1.4747 |
| t-statistic | **4.6673** |
| Degrees of Freedom | 390 (Student) / 381.57 (Welch) |
| p-value (2-tailed) | **3.05 × 10⁻⁶** |
| 95% CI | **[3.9925, 9.7736]** |

### Interpretation

- **p-value = 3.05 × 10⁻⁶ < 0.05** → Reject H₀
- **95% CI = [3.99, 9.77]** → Does not include 0
- **Verdict: SIGNIFICANT** — Treatment has a positive, statistically reliable effect on margin.

---

## IV. Discovery & Deep Dive

### 1. Near-Misses
Not applicable — the result is significant (p ≪ 0.05). No segment-level near-miss breakdown is required.

### 2. Mechanism Hunting: Right-Tail Lift

The most striking secondary finding is the **asymmetric distributional shift** in the treatment group:

| Segment | Control | Treatment | Δ |
|:---|:---:|:---:|:---:|
| Units with margin **> 130** | 2 / 196 (1.0%) | 14 / 196 (7.1%) | **+6.1 pp** |
| Units with margin **< 70** | 5 / 196 (2.6%) | 3 / 196 (1.5%) | −1.1 pp |

The treatment **amplified the top of the distribution** (7× more high-margin units) while barely moving the low end. This explains why treatment's std dev is 16.1% wider than control (σ_t = 15.65 vs σ_c = 13.47, variance ratio = 1.35). The mean lift is real but it is being **driven primarily by the right tail**, not a uniform upward shift.

The slight left-to-right skew flip (control: −0.12 → treatment: +0.17) corroborates this: control is mildly left-skewed; treatment is mildly right-skewed, consistent with unlocking high-margin outcomes.

### 3. Obfuscation Check (Simpson's Paradox)
The dataset contains only `unit_id`, `group`, and `margin` — no sub-segment variables are available. A formal Simpson's Paradox check cannot be performed. **Recommendation:** If segment data (e.g., product category, region, customer tier) becomes available, re-run the analysis stratified to confirm the aggregate result holds across all subgroups.

### 4. Hypothesis Generation

**Why is the treatment working, and why is it concentrated in the right tail?**

1. **Selective amplification of high-potential units.** The treatment may introduce a mechanism (e.g., pricing optimization, premium upsell, targeted offer) that primarily benefits units already on a higher-margin trajectory. Units near the baseline are unaffected, while units with latent high-margin potential get "unlocked." This would produce exactly the observed right-tail lift without degrading the bottom.

2. **Heterogeneous Treatment Effects (HTE) by unobserved segment.** The wider variance and skew shift suggest the treatment effect is not uniform — some subgroup (possibly a product type, customer cohort, or geography) is responding dramatically better than average. The aggregate ATE of +6.88 is a blended effect masking a much larger effect in the responsive segment. An HTE analysis with interaction terms (`Treated × Segment`) on richer data would likely reveal an even more compelling result for the best-responding stratum.

3. **The treatment reduces floor risk slightly while raising the ceiling substantially.** The marginal decrease in sub-70 units (2.6% → 1.5%) alongside the surge in above-130 units suggests the treatment may combine a downside-protection mechanism with an upside-capture mechanism — consistent with a bundled offer, a risk-hedging contract feature, or a loss-prevention + upsell campaign running simultaneously.

---

## V. Analysis Metadata

| Parameter | Value |
|:---|:---|
| Statistical framework | Frequentist (NHST) |
| Test type | Student t-test (pooled), 2-tailed |
| Significance level (α) | 0.05 |
| Outlier treatment | None |
| Missing data handling | Listwise deletion (MCAR assumed) |
| Confounders | None present in dataset |
| Analysis level | Simple (no regression required) |
