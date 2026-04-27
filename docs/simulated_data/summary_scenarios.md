# A/B Simulator Scenario Guide: Validation & Testing

This document provides a summary of the 8 simulated scenarios developed for the Search Engine A/B Simulator. Use this as a reference to verify the 'Analyst Skill' performance.

---

## Scenario 1: Baseline / Mixed Results (The Standard)
**What it tests:** Request-level analysis and basic mechanism attribution.
* **Mechanism Focus:** Balanced mix of `warm_store_hit` and `fresh_compute_saved`.
* **Expected Results:** * **Engagement:** Often non-significant (near-miss) due to mechanisms canceling each other out.
    * **Latency:** Significant degradation (~30ms) driven by the compute path.
* **Analyst Goal:** Identify that the "failure" is caused by mechanism heterogeneity.

## Scenario 2: Strong Warm-Store Success
**What it tests:** Optimization of the caching layer (Head queries).
* **Mechanism Focus:** High-performance `warm_store_hit`.
* **Expected Results:** * **Engagement:** Significant positive lift (+22% logit boost).
    * **Item Count:** Massive increase in coverage (+110 items for popular queries).
* **Analyst Goal:** Confirm the "Cache-First" strategy is production-ready.

## Scenario 3: Strong Session-Store Reuse
**What it tests:** Live-cache matched analysis (User "learning").
* **Mechanism Focus:** `session_store_hit` on tail/repeated queries.
* **Expected Results:** * **Engagement:** Lift concentrated in later session events.
    * **Temporal Logic:** The system gets "smarter" as the user continues to search.
* **Analyst Goal:** Detect that the win is concentrated in "re-searches" rather than first-touch queries.

## Scenario 4: Weak First-Touch Fresh-Compute (The Poisoned Path)
**What it tests:** Trade-off analysis between speed and relevance.
* **Mechanism Focus:** Heavily degraded `fresh_compute_saved`.
* **Expected Results:** * **Latency:** Extreme spike (+215ms mean).
    * **Engagement:** Significantly negative CTR for fresh paths.
* **Analyst Goal:** Explicitly recommend "killing" the compute path while saving the cache paths.

## Scenario 5: Searchbox Contamination (Trigger Bias)
**What it tests:** Metric dilution and trigger-mode filtering.
* **Mechanism Focus:** Over-representation of `inlineSuggest` triggers.
* **Expected Results:** * **Aggregate CTR:** Crashes toward zero (looks like a failure).
    * **Segmented CTR:** `resultsPage` remains positive.
* **Analyst Goal:** Isolate `resultsPage` to reveal the hidden success masked by typing-behavior.

## Scenario 6: Query-Correction Burden (Selection Bias)
**What it tests:** Fairness and input difficulty.
* **Mechanism Focus:** `fresh_compute_saved` handling messy/typo-heavy queries.
* **Expected Results:** * **Metrics:** Compute path looks weak, but `INPUT_TEXT != NORMALIZED_TEXT` rates are 2-3x higher.
* **Analyst Goal:** Identify that the mechanism isn't "bad," it's just being given "harder" problems.

## Scenario 7: Coverage Win vs. Precision Loss (The Quality Trap)
**What it tests:** Positional ranking and retrieval precision.
* **Mechanism Focus:** High `ITEM_COUNT` but low `alpha` (concentration).
* **Expected Results:** * **Coverage:** "Success" (Zero-results down).
    * **Precision:** "Failure" (Average click rank shifts deeper to 10+).
* **Analyst Goal:** Look past the high item counts to see the decay in ranking quality.

## Scenario 8: Late-Period Divergence (Scoring Drift)
**What it tests:** Stability, stationarity, and mid-experiment failures.
* **Mechanism Focus:** Temporal shift in performance.
* **Expected Results:** * **Time Series:** Alternate group wins early, but metrics "tank" after a specific date (e.g., March 2nd).
* **Analyst Goal:** Detect that the results are non-stationary and suggest a technical drift.