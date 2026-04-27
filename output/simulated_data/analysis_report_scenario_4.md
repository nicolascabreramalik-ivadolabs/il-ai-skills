# A/B Test Analysis Report — Scenario 4

**Date:** 2026-04-27
**Analyst:** A/B Test Specialist (Claude)
**Dataset:** `docs/simulated_data/scenario_4.csv`
**Cohorts:** Baseline (n=984) vs. Alternate (n=1,016)

---

## Pre-Analysis Configuration

| Parameter | Value |
|---|---|
| Outlier threshold | 99th percentile cap, applied independently per group |
| P99 cap — Baseline | 114 ms |
| P99 cap — Alternate | 306 ms |
| Rows removed | 19 → final n = 1,981 (Baseline: 976, Alternate: 1,005) |
| Significance level (α) | 0.05 (2-tailed) |
| Confounder treatment | Interaction (HET) |

**Methodological note on ALT_FLOW_STATUS:** During pre-processing, `ALT_FLOW_STATUS` was found to be a **post-treatment variable** — all non-baseline flow states (`warm_store_hit`, `fresh_compute_saved`, `session_store_hit`) exist exclusively in the Alternate cohort. Controlling for this variable would introduce post-treatment bias (bad control). It is treated as a **mechanism variable** in the Discovery section instead. `TRIGGER_MODE` is balanced across cohorts (resultsPage: 387/410, inlineSuggest: 589/595) and was used as the HET interaction variable.

---

## I. Executive Summary

### KPI 1 — Latency (`LATENCY_MS`)

| | Value |
|---|---|
| **Primary Result** | **SIGNIFICANT** |
| ATE (Beta) | **+29.50 ms** (+44.3% over baseline mean of 66.54 ms) |
| t-statistic | 16.55 |
| p-value | 1.01 × 10⁻⁵⁷ |
| 95% Confidence Interval | [+26.01 ms, +32.99 ms] |
| **Recommendation** | **No-Go** on latency. The Alternate flow is significantly and materially slower. |

### KPI 2 — Engagement Rate (`ENGAGED_POSITIONS`)

| | Value |
|---|---|
| **Primary Result** | **NON-SIGNIFICANT** |
| ATE | **+2.42 percentage points** (29.92% → 32.34%) |
| Chi-square | 1.242 |
| p-value | 0.265 |
| 95% Confidence Interval | [−1.66 pp, +6.50 pp] |
| **Recommendation** | **Iterate** — No statistically significant engagement lift, but a directional positive trend warrants further investigation. |

---

## II. Layman Description

The new Alternate experience loads noticeably slower — nearly half a second more on average — because it activates a new caching and pre-computation layer behind the scenes. While users in the Alternate group did click on results slightly more often (about 2 out of every 100 extra searches), this uplift wasn't large enough to be statistically reliable, meaning it could be due to chance. The business faces a clear tradeoff: the new system's speed cost is proven and large, but its engagement benefit is unproven.

---

## III. Formal Statistical Report

### KPI 1: Response Latency (Continuous — Student t-test + HET Regression)

**Variable type:** Continuous
**Test:** Student t-test (pooled variance), 2-tailed

| Statistic | Value |
|---|---|
| Mean — Baseline | 66.54 ms (SD = 19.40) |
| Mean — Alternate | 96.04 ms (SD = 52.31) |
| ATE | **+29.50 ms** |
| Pooled SD (σp) | 39.67 |
| Standard Error | 1.78 |
| t-statistic | 16.55 |
| p-value | 1.01 × 10⁻⁵⁷ |
| 95% CI | [+26.01, +32.99] |
| **Verdict** | **SIGNIFICANT** — p < 0.05 and 95% CI excludes 0 |

**HET Regression — TRIGGER_MODE Interaction** (OLS: `LATENCY_MS ~ Treated * TriggerMode_inline`)

| Term | Coefficient | p-value | 95% CI | Interpretation |
|---|---|---|---|---|
| Intercept | +69.97 ms | < 0.001 | [66.02, 73.91] | Baseline / resultsPage mean |
| Treated (β) | **+29.06 ms** | < 0.001 | [+23.56, +34.57] | Main treatment effect |
| TriggerMode_inline | −5.68 ms | 0.028 | [−10.77, −0.60] | inlineSuggest is inherently faster |
| **Treated × TriggerMode_inline (δ)** | **+0.64 ms** | **0.860** | [−6.48, +7.76] | **No HET — interaction not significant** |

R² = 0.125

**Conclusion:** The treatment effect on latency is **uniform across trigger modes** (δ p = 0.86). The +29 ms penalty applies equally to `resultsPage` and `inlineSuggest` requests.

---

### KPI 2: Engagement Rate (Binary — Pearson Chi-Square + HET Logistic Regression)

**Variable type:** Discrete / Binary
**Test:** Pearson Chi-Square, 2-tailed

| Statistic | Value |
|---|---|
| Engagement Rate — Baseline | 29.92% (292 / 976) |
| Engagement Rate — Alternate | 32.34% (325 / 1,005) |
| ATE | **+2.42 pp** |
| Standard Error | 0.0208 |
| Chi-square statistic | 1.242 (dof = 1) |
| p-value | 0.265 |
| 95% CI | [−1.66 pp, +6.50 pp] |
| **Verdict** | **NON-SIGNIFICANT** — p ≥ 0.05 and 95% CI includes 0 |

**HET Logistic Regression — TRIGGER_MODE Interaction** (`Engaged ~ Treated * TriggerMode_inline`)

| Term | Coefficient | p-value | 95% CI | Interpretation |
|---|---|---|---|---|
| Intercept | +1.054 | < 0.001 | [+0.83, +1.28] | Log-odds of engagement: resultsPage baseline |
| Treated (β) | **+0.229** | **0.171** | [−0.099, +0.556] | Main treatment effect — **not significant** |
| TriggerMode_inline | **−5.815** | **< 0.001** | [−6.72, −4.91] | inlineSuggest has near-zero engagement |
| **Treated × TriggerMode_inline (δ)** | **−0.464** | **0.504** | [−1.82, +0.90] | **No HET — interaction not significant** |

Pseudo-R² (McFadden) = 0.603 (driven almost entirely by TRIGGER_MODE, not treatment)

**Conclusion:** Treatment shows no statistically significant interaction with TRIGGER_MODE on engagement. The dominant driver of engagement is the trigger mode itself — `resultsPage` users engage at ~75% vs. <1% for `inlineSuggest`.

---

## IV. Discovery & Deep Dive

### 1. Near-Miss: resultsPage Engagement

The aggregate engagement result is non-significant (p = 0.265), but a segment-level breakdown reveals a notable signal:

| Segment | Baseline Rate | Alternate Rate | ATE | p-value |
|---|---|---|---|---|
| `resultsPage` | 74.16% | 78.29% | **+4.13 pp** | **0.198** |
| `inlineSuggest` | 0.85% | 0.67% | −0.18 pp | 0.988 |

The `resultsPage` segment is a **near-miss at p = 0.198** with a +4.13 pp lift. The `inlineSuggest` segment shows effectively zero engagement in both arms (< 1%), meaning it contributes noise to the aggregate test, diluting an otherwise potentially meaningful signal for the main product surface.

### 2. Mechanism Hunting — ALT_FLOW_STATUS as Treatment Mediator

The Alternate treatment introduces three auxiliary response flow states absent in Baseline. These reveal the internal mechanics of the latency impact and a hidden engagement split:

**Latency by flow path:**

| Flow Path | Mean Latency | n | vs. Baseline (66.5 ms) |
|---|---|---|---|
| Baseline (`no_aux_response`) | **66.5 ms** | 976 | — |
| Alternate `no_aux_response` | **60.5 ms** | 352 | **−6.0 ms (faster)** |
| Alternate `session_store_hit` | 64.9 ms | 48 | −1.6 ms (faster) |
| Alternate `warm_store_hit` | 100.2 ms | 479 | +33.7 ms |
| Alternate `fresh_compute_saved` | **191.4 ms** | 126 | **+124.9 ms (3× slower)** |

**Key insight:** When the Alternate system does NOT invoke the caching layer, it is actually **6 ms faster** than Baseline. The entire +29.5 ms average penalty is attributable to the overhead of the new caching infrastructure — particularly `fresh_compute_saved` (+124.9 ms) which represents the first-pass computation cost.

**Engagement by flow path:**

| Flow Path | Engagement Rate | vs. Baseline |
|---|---|---|
| Baseline `no_aux_response` | 29.9% | — |
| Alternate `no_aux_response` | 23.6% | −6.3 pp |
| Alternate `session_store_hit` | 31.3% | +1.4 pp |
| Alternate `warm_store_hit` | **44.7%** | **+14.8 pp** |
| Alternate `fresh_compute_saved` | **10.3%** | **−19.6 pp** |

Cached warm results drive dramatically higher engagement (+14.8 pp), but fresh computation requests drive dramatically lower engagement (−19.6 pp). These opposing effects cancel out in the aggregate.

### 3. Obfuscation Check — Simpson's Paradox

No classic Simpson's Paradox was detected. Both TRIGGER_MODE segments show the same directional pattern (resultsPage positive, inlineSuggest near-zero) as the aggregate. However, there is a **directional inconsistency by ALT_FLOW_STATUS** within the Alternate group: `warm_store_hit` strongly boosts engagement while `fresh_compute_saved` strongly suppresses it — masking a real positive signal in the aggregate test.

### 4. Hypothesis Generation

**H1 — Cache warmth drives quality, cold compute drives noise.**
The `warm_store_hit` path (48% of Alternate requests) returns pre-cached, presumably higher-quality or better-ranked results, explaining the +14.8 pp engagement lift. The `fresh_compute_saved` path is the system saving results for the first time under load — these may be lower-quality first-pass computations, which would explain the −19.6 pp engagement drop.

**H2 — The core serving logic is better; the infrastructure is the bottleneck.**
The Alternate system's native `no_aux_response` path is 6 ms faster than Baseline, suggesting the core ranking or retrieval logic improved. The latency regression is masking this signal because 64% of Alternate requests trigger the caching layer overhead. A targeted analysis isolating `no_aux_response` would show a net win on both latency and potentially engagement.

**H3 — `inlineSuggest` is drowning the engagement signal.**
`inlineSuggest` accounts for ~59% of all requests but has engagement rates below 1% in both arms. Its near-zero variance contributes primarily noise to the aggregate chi-square test. If the product team's actual hypothesis is about `resultsPage` engagement (where the treatment is logically relevant), the test is underpowered for that question and the near-miss (+4.13 pp, p = 0.198) could reach significance with a properly scoped and powered experiment.

---

*Report generated by A/B Test Specialist — Claude (claude-sonnet-4-6)*
*Methodology: `docs/templates/ab_analysis_methodology.md`*
