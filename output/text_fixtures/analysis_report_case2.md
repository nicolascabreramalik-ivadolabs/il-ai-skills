# A/B Test Analysis Report — Case 2 (Large, Inconclusive)

**Dataset:** `docs/raw/test_fixtures/case2_large_inconclusive.csv`
**Date:** 2026-04-27
**Outlier Treatment:** None
**Methodology:** `docs/templates/AB_Analysis_Methodology.md`

---

## I. Executive Summary

| Field | Value |
| :--- | :--- |
| **Primary Result** | **Non-Significant** |
| **Key Metric** | Margin |
| **ATE (Beta)** | −0.088 units (−0.09% vs. control mean) |
| **t-statistic** | −0.065 |
| **p-value (2-tailed)** | 0.9482 |
| **95% CI** | [−2.754, +2.577] |
| **Cohen's d** | −0.007 (negligible) |
| **Recommendation** | **No-Go / Iterate** |

The treatment produced no statistically meaningful change in margin. The observed difference is effectively indistinguishable from zero and far inside the noise band of the experiment.

---

## II. Layman Description

The test and control groups performed almost identically — on average, the treatment group earned $0.09 less per unit than the control, an amount that could easily be random variation. With 200 customers in each group, we cannot detect any meaningful business effect here. Before re-running the test, the team should either increase the sample size substantially or reconsider whether margin is the right metric to measure.

---

## III. Formal Statistical Report

### Pre-Analysis Framework

| Parameter | Value |
| :--- | :--- |
| Variable Type | Continuous (margin) |
| Test Selected | Student t-test (pooled variance, 2-tailed) |
| Justification | Large sample (n=200 per group), similar variances (ratio = 0.972) |
| Outlier Threshold | None |
| Confounders | None identified |

### Group Descriptive Statistics

| Statistic | Control | Treatment |
| :--- | ---: | ---: |
| N | 200 | 200 |
| Mean | 99.231 | 99.143 |
| Std Dev | 13.695 | 13.500 |
| Min | 59.542 | 60.257 |
| P10 | 81.93 | 81.60 |
| Median | 100.34 | 98.72 |
| P90 | 115.52 | 117.85 |
| Max | 134.368 | 132.419 |

### Hypothesis Test

$$H_0: \bar{Y}_t - \bar{Y}_c = 0$$

$$\text{ATE} = \bar{Y}_t - \bar{Y}_c = 99.143 - 99.231 = -0.088$$

$$\sigma_p = \sqrt{\frac{(n_c-1)\,s_c^2 + (n_t-1)\,s_t^2}{n_c + n_t - 2}} = \sqrt{\frac{199 \times 13.695^2 + 199 \times 13.500^2}{398}} = 13.598$$

$$t = \frac{-0.088}{13.598 \times \sqrt{\tfrac{1}{200} + \tfrac{1}{200}}} = \frac{-0.088}{1.361} = -0.065 \quad (df = 398)$$

$$p\text{-value (2-tailed)} = 0.9482 \quad \gg \alpha = 0.05$$

$$95\%\ \text{CI} = -0.088 \pm 1.96 \times 1.361 = [-2.754,\ +2.577]$$

### Decision

| Criterion | Outcome |
| :--- | :--- |
| $p < 0.05$? | No (p = 0.9482) |
| 95% CI excludes 0? | No (CI = [−2.754, +2.577]) |
| **Verdict** | **Non-Significant — Fail to reject $H_0$** |

The result is decisively non-significant. The 95% confidence interval spans more than 5 units and straddles zero symmetrically, confirming no detectable treatment effect in either direction.

---

## IV. Discovery & Deep Dive

### 1. Near-Miss Check

**Not applicable.** The p-value (0.948) is far above the 0.20 threshold that would trigger a segment-level breakdown. There is no directional trend worth decomposing.

### 2. Mechanism Hunting

The dataset contains only `unit_id`, `group`, and `margin`. No secondary behavioral metrics (e.g., conversion rate, order volume, session depth) are available to correlate with the treatment effect. Mechanism analysis is **data-limited** for this case.

**Observation:** The standard deviations are nearly identical between groups (13.695 vs. 13.500, ratio = 0.972), confirming the treatment did not alter the spread of outcomes — ruling out a scenario where the treatment benefits some units while hurting others with zero net effect.

### 3. Simpson's Paradox / Obfuscation Check

No sub-segments (region, cohort, tier, device, etc.) exist in this dataset. A formal Simpson's Paradox check cannot be performed. However, the extreme symmetry of the distributions (nearly identical percentile profiles across P10–P90) makes paradox-driven obfuscation unlikely; the null result appears genuine rather than a concealed divergence of sub-segments.

### 4. Hypothesis Generation

Three qualitative explanations for the observed null result:

**H1 — True Zero Effect (Most Likely)**
The treatment itself simply has no material impact on margin. If the intervention was, for example, a UI change, messaging tweak, or minor pricing adjustment, the downstream effect on profitability may genuinely be zero because the change does not alter customer purchasing behaviour or unit economics in a detectable way.

**H2 — Underpowered for Small Economically Meaningful Effects**
With $n = 200$ per group and $\sigma \approx 13.7$, the Minimum Detectable Effect (MDE) at 80% power is **≈ 3.84 units (≈ 3.87% of the control mean)**. Any real treatment effect smaller than this threshold is statistically invisible at this sample size. If stakeholders would act on a +1% margin lift, the experiment requires approximately **n ≈ 1,800 per group** to reliably detect it.

$$n = \frac{2\sigma^2 (z_{\alpha/2} + z_\beta)^2}{\delta^2} = \frac{2 \times 13.598^2 \times (1.96 + 0.842)^2}{(99.231 \times 0.01)^2} \approx 1{,}800$$

**H3 — Margin Is Too Noisy a Primary KPI**
The coefficient of variation (CV = σ / mean ≈ 13.7 / 99.2 ≈ **13.8%**) means margin carries substantial inherent noise. A binary metric closer to the treatment mechanism (e.g., click-through rate, add-to-cart rate, or checkout conversion) would typically have lower variance and enable detection of smaller effects with the same sample size. Future tests should consider a more proximal KPI before moving to aggregate margin measurement.

---

## V. Power & Sample Size Reference

| Desired Detectable Effect | Required n (per group, 80% power) |
| :--- | ---: |
| ±5% of mean (≈ ±4.96 units) | ~120 |
| ±3% of mean (≈ ±2.98 units) | ~335 |
| ±2% of mean (≈ ±1.98 units) | ~756 |
| ±1% of mean (≈ ±0.99 units) | ~3,022 |

*Assumes $\sigma = 13.598$, $\alpha = 0.05$, two-tailed.*

---

*Report generated by A/B Test Specialist skill | Methodology: `docs/templates/AB_Analysis_Methodology.md`*
