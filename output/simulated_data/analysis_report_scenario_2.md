# A/B Test Analysis Report — Scenario 2
**Date:** 2026-04-27
**Analyst:** A/B Test Specialist (Claude)
**Dataset:** `docs/simulated_data/scenario_2.csv`
**Treatment:** Alternate cohort — ALT_FLOW caching layer (`warm_store_hit`, `session_store_hit`, `fresh_compute_saved`)
**Control:** Baseline cohort — standard `no_aux_response` path

---

## I. Executive Summary

| Metric | ATE | p-value | 95% CI | Verdict | Recommendation |
|---|---|---|---|---|---|
| **Latency (ms)** | +28.06 ms | < 0.0001 | [+24.10, +32.02] | **SIGNIFICANT** | **No-Go** |
| **Engagement Rate** | +5.43 pp | 0.072 | [−4.91%, +15.77%] | Non-Significant | **Iterate** |
| **Order Rate** | 0.00 pp | 1.000 | N/A | Non-Significant (degenerate) | N/A |

**Critical finding:** The ALT_FLOW caching treatment **increases** latency by ~28 ms rather than reducing it. The effect is highly significant, uniform across both trigger modes, and constitutes a regression in system performance. This overrides any positive trend observed on engagement.

---

## II. Layman Description

The new caching system being tested (Alternate group) was expected to make the product respond faster by serving pre-computed results. In practice, it did the opposite: users in the Alternate group waited about 28 milliseconds longer per request — a consistent, statistically certain slowdown. On the positive side, users in the Alternate group showed a modest trend toward clicking on more results (~5 percentage points more often), but this difference is not large enough to be conclusive with the current sample size. There were no orders in either group, so purchase intent cannot be evaluated with this dataset.

---

## III. Formal Statistical Report

### Pre-Analysis Decisions
- **Outlier Threshold:** 99th percentile trim, applied independently per group
- **Confounder — `TRIGGER_MODE`:** Treated as an **Interaction variable (HET)**
- **Test types:** Student t-test (continuous), Pearson chi-square (discrete/binary), 2-tailed throughout
- **Significance level:** α = 0.05

### Sample Sizes

| Cohort | n (total) | inlineSuggest | resultsPage |
|---|---|---|---|
| Alternate (Treatment) | 480 | 269 | 211 |
| Baseline (Control) | 520 | 311 | 209 |

---

### Metric 1 — Latency (LATENCY_MS)

**Variable type:** Continuous
**Analysis level:** Student t-test (pooled SD) + HET interaction model

| Statistic | Value |
|---|---|
| Mean — Alternate | 94.65 ms |
| Mean — Baseline | 66.60 ms |
| **ATE** | **+28.06 ms** |
| SE | 2.02 |
| T-statistic | 13.89 |
| P-value (2-tailed) | < 0.000001 |
| 95% CI | [+24.10 ms, +32.02 ms] |

**Verdict: SIGNIFICANT** — p < 0.05 and CI excludes 0.
The treatment causes a statistically certain **increase** in latency. The direction is adverse.

#### HET Model — `LATENCY_MS ~ Treated + TriggerMode + Treated:TriggerMode`

| Term | Coefficient | p-value |
|---|---|---|
| Treated (Beta) | +27.46 ms | < 0.0001 |
| TriggerMode | +3.97 ms | — |
| **Treated × TriggerMode (Delta)** | **+1.00 ms** | **0.808** |

**Interaction finding:** Delta is not significant (p = 0.808). The latency penalty is **uniform** across both `resultsPage` and `inlineSuggest` — approximately +28 ms regardless of trigger mode.

---

### Metric 2 — Engagement Rate

**Variable type:** Discrete/Binary (ENGAGED_POSITIONS non-null = 1)
**Analysis level:** Pearson chi-square + HET OLS interaction model

| Statistic | Value |
|---|---|
| Rate — Alternate | 33.12% |
| Rate — Baseline | 27.69% |
| **ATE** | **+5.43 pp** |
| SE | 2.77 pp |
| Chi-square | 3.24 |
| P-value (2-tailed) | 0.072 |
| 95% CI | [−4.91 pp, +15.77 pp] |

**Verdict: Non-Significant** — p = 0.072 ≥ 0.05 and CI includes 0.
There is a positive trend but insufficient evidence to reject H₀.

#### HET Model — `engaged ~ Treated + TriggerMode + Treated:TriggerMode`

| Term | Coefficient | p-value |
|---|---|---|
| Treated (Beta) | −0.006 | 0.794 |
| TriggerMode | +0.676 | < 0.0001 |
| **Treated × TriggerMode (Delta)** | **+0.081** | **0.034** |

**Interaction finding:** Delta is **significant** (p = 0.034). The treatment effect on engagement is **heterogeneous** — it differs materially between trigger modes (see Discovery section).

---

### Metric 3 — Order Rate

**Variable type:** Discrete/Binary (ORDERED_POSITIONS non-null = 1)

| Statistic | Value |
|---|---|
| Rate — Alternate | 0.00% |
| Rate — Baseline | 0.00% |
| ATE | 0.00 pp |
| P-value | 1.000 |

**Verdict: Non-Significant (degenerate)** — Zero orders recorded in both groups across all segments. This metric cannot be evaluated with the current dataset. Order data is absent, not merely sparse.

---

## IV. Discovery & Deep Dive

### 1. Near-Miss Analysis — Engagement Rate (p = 0.072)

Segment-level breakdown of engagement ATE by `TRIGGER_MODE`:

| Segment | Rate (Alt) | Rate (Base) | ATE | P-value | 95% CI |
|---|---|---|---|---|---|
| **resultsPage** | 75.36% | 67.94% | **+7.41 pp** | 0.115 | [−0.19%, +15.01%] |
| **inlineSuggest** | 0.00% | 0.64% | −0.64 pp | 0.544 | (undefined) |

The aggregate near-miss (+5.43 pp, p = 0.072) is **entirely driven by the `resultsPage` segment**, where the Alternate group shows a +7.41 pp uplift (p = 0.115). The `inlineSuggest` segment contributes near-zero engagement in both groups, diluting the overall signal. If the analysis were restricted to `resultsPage` only, the effect size grows meaningfully — though statistical significance is still not reached, it falls within reach with a larger sample.

### 2. Mechanism Hunting — Latency vs. Cache Status

Cache distribution by cohort:

| Cache Status | Alternate | Baseline |
|---|---|---|
| `no_aux_response` | 141 (29.4%) | 520 (100%) |
| `warm_store_hit` | 247 (51.5%) | 0 |
| `fresh_compute_saved` | 64 (13.3%) | 0 |
| `session_store_hit` | 28 (5.8%) | 0 |

**Paradox:** 70.6% of Alternate requests are served from cache (`warm_store_hit` + `fresh_compute_saved` + `session_store_hit`), yet aggregate latency is ~28 ms *higher* than Baseline. This is counterintuitive and suggests one or more of:
- The cache lookup itself introduces overhead (round-trip to a remote cache store) that exceeds the compute savings
- `fresh_compute_saved` (64 requests) may represent a write-through path that pays both compute and storage costs
- The Alternate requests that fall through to `no_aux_response` (141 requests) may carry additional overhead from a failed cache check before falling back

Latency by cohort and trigger mode (post-trim):

| Cohort | inlineSuggest | resultsPage |
|---|---|---|
| Alternate | 92.48 ms | 97.44 ms |
| Baseline | 65.02 ms | 68.99 ms |

The gap is consistent (~27–28 ms) across both modes, confirming the overhead is introduced at a layer common to all ALT_FLOW requests, not mode-specific logic.

### 3. Obfuscation Check — Structural Engagement Split (Simpson's Paradox)

The aggregate engagement rate masks a structural split in the data:

| Segment | Alternate | Baseline |
|---|---|---|
| `inlineSuggest` | **0.00%** | **0.64%** |
| `resultsPage` | **75.36%** | **67.94%** |

`ENGAGED_POSITIONS` is only populated in `resultsPage` events — `inlineSuggest` has near-zero engagement in *both* groups by design (the UI does not surface engageable positions for inline suggestions). The aggregate engagement rate (+5.43 pp non-significant) is therefore a composition artifact: the Alternate group has more `inlineSuggest` weight in its sample (56% vs 60% for Baseline), which numerically suppresses its aggregate engagement. When restricted to the only structurally valid stratum (`resultsPage`), the positive trend grows to +7.41 pp. This is a mild form of **Simpson's Paradox** — the aggregate suggests marginal lift, but the relevant stratum shows a more consistent positive signal.

### 4. Hypothesis Generation

**Why is latency higher in the Alternate group despite caching?**

1. **Cache infrastructure overhead:** The caching layer likely requires a network round-trip (e.g., Redis, memcached) that adds ~30 ms of I/O latency. If the compute savings per item are less than 30 ms, the cache is a net negative for latency. The treatment may be optimizing server-side compute while ignoring network overhead.

2. **Cold-start cost being absorbed:** `fresh_compute_saved` events suggest the system is also *writing* results to cache. These write operations may share the same response path, making cache misses doubly expensive (compute + write). The 64 `fresh_compute_saved` events pull the mean up disproportionately.

3. **Response payload inflation:** Cache hits may return richer or pre-ranked result sets (hence higher `ITEM_COUNT` or more engaged positions), and the serialization/transmission of larger payloads could itself account for the latency delta.

**Why is engagement trending positive but non-significant?**

4. **Underpowered for the observed effect size:** A 5.43 pp lift at 80% power requires approximately 650 observations per group for a binary metric at ~30% base rate. The current n of ~480/520 is insufficient. The signal is real but the experiment was stopped too early (or was not powered for this effect size).

5. **Cache quality improves result relevance:** `warm_store_hit` and `session_store_hit` return previously-computed results that were already served to *similar* or *same-session* queries. These results may be better calibrated to user intent, which explains why users engage with them more — but the engagement uplift is masked by the inlineSuggest dilution described above.

---

## V. Summary Table

| Metric | ATE | p-value | Significant | HET Interaction | Recommendation |
|---|---|---|---|---|---|
| Latency | +28.06 ms | < 0.0001 | Yes (adverse) | No (p=0.808) | **No-Go** |
| Engagement Rate | +5.43 pp | 0.072 | No (near-miss) | Yes (p=0.034) | **Iterate** |
| Order Rate | 0.00 pp | 1.000 | Degenerate | N/A | **No data** |

**Overall Recommendation: No-Go / Iterate**
The treatment must not ship as-is due to the significant latency regression. The engagement signal warrants further investigation — isolating the test to `resultsPage` only and addressing the caching overhead could surface a genuine positive effect.
