# A/B Test Analysis Report — Scenario 1
**Date:** 2026-04-27  
**Analyst:** A/B Test Specialist (Claude)  
**Dataset:** `docs/simulated_data/scenario_1.csv`  
**Groups:** Baseline (n=506) vs. Alternate (n=494)

---

## I. Executive Summary

| Metric | Result | ATE | p-value | 95% CI | Recommendation |
|---|---|---|---|---|---|
| **LATENCY_MS** | **SIGNIFICANT** | +29.7 ms (+46.6%) | < 0.001 | [+25.6, +33.8] | **No-Go** |
| **ITEM_COUNT** | **SIGNIFICANT** | +27.3 items (+68.0%) | < 0.001 | [+21.9, +32.7] | **Iterate** |
| **Engagement Rate** | **NON-SIGNIFICANT** | +4.52 pp | 0.119 | [−1.15, +10.19] | **No-Go** |

**Overall Recommendation: Iterate.**  
The Alternate treatment successfully delivers more items to users — but at a significant latency cost (+30 ms, +47%), and with no real engagement benefit once TRIGGER_MODE composition is corrected for. The engagement lift is a statistical artifact. The latency regression is real and large.

---

## II. Layman Description

The new Alternate system shows it can surface more search results for users — nearly 70% more items on average — but it does so at the cost of meaningfully slower response times. Despite returning more results, users are not actually clicking or engaging with them any more than before; the small apparent improvement in engagement disappears entirely when we account for how requests are distributed across surface types. In short: the system is working harder but not delivering better user outcomes, and the speed regression is a serious concern.

---

## III. Formal Statistical Report

### Pre-processing
- **Outlier threshold:** 99th percentile, trimmed independently per group.
  - LATENCY_MS: 10 rows removed (990 remaining).
  - ITEM_COUNT: 11 rows removed (989 remaining).
  - Engagement: no trim (binary variable, 1,000 rows).
- **ALT_FLOW_STATUS reclassified:** This variable is exclusive to the Alternate group (Baseline = 100% `no_aux_response`). It is a **post-treatment mediator**, not a confounder. Including it as an interaction term would introduce post-treatment bias. It is used only in the Discovery section.
- **Valid HET variable:** TRIGGER_MODE (distributed across both cohorts: 57.5% / 36.4% resultsPage split for Alternate / Baseline).

---

### Metric 1: LATENCY_MS (Continuous)
**Test:** Student t-test, 2-tailed, pooled variance. Outliers trimmed at 99th percentile per group.

| | Baseline | Alternate |
|---|---|---|
| n | 501 | 489 |
| Mean | 63.79 ms | 93.50 ms |
| Std | ~19.0 ms | ~42.8 ms |

| Statistic | Value |
|---|---|
| ATE (β) | **+29.71 ms** |
| t-statistic | 14.29 |
| p-value | < 0.001 |
| 95% CI | [+25.64, +33.78] |
| **Verdict** | **SIGNIFICANT** |

**HET — TRIGGER_MODE Interaction:**

| Term | Coef | p-value | Interpretation |
|---|---|---|---|
| Intercept (Baseline, inlineSuggest) | 61.58 ms | < 0.001 | — |
| resultsPage (main effect) | +6.03 ms | 0.045 | resultsPage is inherently slower |
| treated (inlineSuggest) | +27.66 ms | < 0.001 | Core treatment latency penalty |
| treated × resultsPage (δ) | +3.95 ms | 0.350 | **Not significant** |

**HET Conclusion:** The latency increase is uniform across TRIGGER_MODE. δ = +3.95 ms (p=0.350) — the interaction is not significant. The treatment adds ~28 ms to inlineSuggest and ~32 ms to resultsPage, but this difference is within noise. **The latency regression is a global, undifferentiated cost of the treatment.**

---

### Metric 2: ITEM_COUNT (Continuous)
**Test:** Student t-test, 2-tailed, pooled variance. Outliers trimmed at 99th percentile per group.

| | Baseline | Alternate |
|---|---|---|
| n | 500 | 489 |
| Mean | 40.11 items | 67.40 items |
| Std | ~28.0 | ~56.3 |

| Statistic | Value |
|---|---|
| ATE (β) | **+27.29 items** |
| t-statistic | 9.97 |
| p-value | < 0.001 |
| 95% CI | [+21.93, +32.65] |
| **Verdict** | **SIGNIFICANT** |

**HET — TRIGGER_MODE Interaction:**

| Term | Coef | p-value | Interpretation |
|---|---|---|---|
| Intercept (Baseline, inlineSuggest) | 41.84 items | < 0.001 | — |
| resultsPage (main effect) | −4.77 items | 0.229 | Not significant |
| treated (inlineSuggest) | +18.29 items | < 0.001 | Treatment adds 18 items on inlineSuggest |
| treated × resultsPage (δ) | +21.96 items | < 0.001 | **SIGNIFICANT interaction** |

**HET Conclusion:** δ = +21.96 (p<0.001) — the interaction is highly significant.

- **inlineSuggest:** Alternate returns **+18.3 items** over Baseline (41.8 → 60.1).  
- **resultsPage:** Alternate returns **+40.2 items** over Baseline (37.1 → 77.3).  

The treatment's item enrichment is **more than twice as large on resultsPage** than on inlineSuggest. This is the strongest differential finding in the dataset.

---

### Metric 3: Engagement Rate (Binary)
**Test:** Pearson Chi-square, 2-tailed.

| | Baseline | Alternate |
|---|---|---|
| n | 506 | 494 |
| Engaged | 140 (27.67%) | 159 (32.19%) |
| Not Engaged | 366 | 335 |

| Statistic | Value |
|---|---|
| ATE (β) | **+4.52 pp** |
| Chi²-statistic | 2.43 |
| p-value | 0.119 |
| 95% CI | [−1.15 pp, +10.19 pp] |
| **Verdict** | **NON-SIGNIFICANT** |

**HET — TRIGGER_MODE Interaction (LPM):**

| Term | Coef | p-value | Interpretation |
|---|---|---|---|
| Intercept (Baseline, inlineSuggest) | 0.006 | 0.685 | ~0% engagement on inlineSuggest |
| resultsPage (main effect) | +0.744 | < 0.001 | resultsPage drives all engagement |
| treated (inlineSuggest) | −0.006 | 0.781 | No treatment effect on inlineSuggest |
| treated × resultsPage (δ) | +0.013 | 0.708 | **Not significant** |

**HET Conclusion:** Neither the main treatment effect nor the interaction term is significant. The treatment has no measurable effect on engagement within either trigger mode.

---

## IV. Discovery & Deep Dive

### 1. Near-Miss Analysis (Engagement, p=0.119)

Segment-level chi-square on engagement:

| TRIGGER_MODE | Baseline Rate | Alternate Rate | ATE | p-value |
|---|---|---|---|---|
| inlineSuggest | 0.6% (n=322) | 0.0% (n=284) | −0.6 pp | 0.183 |
| resultsPage | 75.0% (n=184) | 75.7% (n=210) | +0.7 pp | 0.870 |

**Conclusion:** There is no sub-segment driving the aggregate +4.52 pp — both segments show near-zero treatment effects. The aggregate signal is entirely explained by a **compositional imbalance**: Alternate contains proportionally more resultsPage requests (42.5%) than Baseline (36.4%). Since resultsPage has a ~75% engagement floor regardless of treatment, the Alternate group's higher proportion of resultsPage requests mechanically inflates its aggregate engagement rate.

> **This is a compositional/Simpson's Paradox-type obfuscation, not a treatment effect. See Section 3.**

---

### 2. Mechanism Hunting (via ALT_FLOW_STATUS)

ALT_FLOW_STATUS reveals the internal mechanics of the Alternate treatment:

| Flow Path | n | Latency (ms) | Item Count | Engagement Rate |
|---|---|---|---|---|
| `warm_store_hit` | 228 (46.2%) | 95.9 | 111.9 | 45.6% |
| `fresh_compute_saved` | 77 (15.6%) | **168.2** | 18.3 | 10.4% |
| `session_store_hit` | 22 (4.5%) | 86.1 | 40.2 | **54.5%** |
| `no_aux_response` | 167 (33.8%) | 61.5 | 39.6 | 21.0% |
| **Baseline (all no_aux)** | 506 (100%) | **63.8** | **41.2** | **27.7%** |

**Key findings:**

- **`warm_store_hit`** is the primary driver of both the item count increase (+72 items vs. Baseline) and the latency increase (+32 ms). With 46% of Alternate traffic, it dominates the treatment effect.
- **`fresh_compute_saved`** is a high-cost, low-return pathway: 168 ms latency (+104 ms vs. Baseline), only 18 items returned, and only 10.4% engagement. This path likely represents cache misses that force an expensive computation.
- **`session_store_hit`** shows the highest engagement (54.5%) and reasonable latency, but accounts for only 4.5% of traffic — too small to move the aggregate needle.
- **`no_aux_response` within Alternate** (33.8% of traffic) performs identically to Baseline — confirming that the treatment effect is entirely attributable to the auxiliary response paths.

---

### 3. Obfuscation Check — Simpson's Paradox

**Finding: CONFIRMED (compositional)**

The aggregate +4.52 pp engagement lift is not a treatment effect. Within both TRIGGER_MODE segments, the treatment has near-zero effect:

- inlineSuggest: −0.6 pp (p=0.183)
- resultsPage: +0.7 pp (p=0.870)

The Alternate group has 6.1 pp more resultsPage exposure (42.5% vs. 36.4%), and since resultsPage drives ~75% engagement floor by design, the Alternate group's aggregate rate is structurally higher. **The aggregate difference disappears when controlling for TRIGGER_MODE.**

This is not a full Simpson's Paradox (where direction reverses), but it is a classic confounding-by-composition case that makes a null result appear positive in aggregate.

---

### 4. Hypothesis Generation

**H1 — The latency penalty is suppressing engagement recovery.**  
The treatment delivers more items (especially `warm_store_hit` → 112 items), but the +30ms latency increase (and up to +104ms for `fresh_compute_saved`) may be causing user abandonment before the richer results load. Research on search UX consistently shows engagement drops at latency thresholds of ~100ms+. The `fresh_compute_saved` path at 168ms is almost certainly in this penalty zone.

**H2 — `fresh_compute_saved` is a broken path that needs to be gated.**  
16% of Alternate requests fall into `fresh_compute_saved` (cache miss → live compute): these requests have the highest latency (168ms), the fewest items (18), and the lowest engagement (10%). This path is actively harming aggregate performance. If this path were suppressed or rerouted to `no_aux_response`, latency would drop ~15ms and engagement would likely improve.

**H3 — The resultsPage × treatment interaction reveals where the product hypothesis is strongest.**  
The item count benefit is twice as large on resultsPage (+40 items) vs. inlineSuggest (+18 items), and resultsPage users engage at 75%. If the Alternate system can reduce latency (especially for `fresh_compute_saved`), a resultsPage-only rollout might achieve both the item richness benefit and improved engagement without the latency cost that undermines inline surfaces.

---

## V. Methodology Notes

- All tests are **2-tailed** per policy.
- Significance threshold: **α = 0.05** (p < 0.05 AND 95% CI excludes 0).
- ALT_FLOW_STATUS excluded from regression models as a **post-treatment mediator** (exclusive to Alternate group — inclusion would constitute post-treatment bias).
- TRIGGER_MODE used as the HET interaction variable (balanced across both cohorts).
- Outlier trim: 99th percentile applied **independently per group**.
