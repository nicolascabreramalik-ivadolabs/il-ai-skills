# Validation Matrix: A/B Test Analyst Skill
**Methodology source:** `docs/templates/AB_Analysis_Methodology.md`  
**Skill source:** `.claude/skills/ab_test_specialist.md`  
**Date:** 2026-04-10

---

## How to Use This Matrix

Each test case defines an input scenario, the statistical conditions it exercises, and the **Expected AI Behavior** — the precise sequence of actions the analyst skill must take to be considered compliant with the methodology. Use these cases to audit new model versions or skill edits.

---

## Test Case 1 — Large Sample / Significant Lift

### Input
| Parameter | Value |
|---|---|
| Variable type | Continuous (margin) |
| n_control | 200 |
| n_treatment | 200 |
| mean_control | 99.39 |
| mean_treatment | 107.29 |
| σ_p (pooled) | 14.39 |

### Statistical Conditions
- ATE = +7.90
- t-statistic = 5.49, df = 398
- p-value ≈ 7.2 × 10⁻⁸ (2-tailed)
- 95% CI = [5.08, 10.72] — entirely above zero

### Expected AI Behavior
1. **Step 1 (Framework):** Identifies variable as Continuous, sample as Large → selects **Student t-test** with pooled σ_p.
2. **Step 2 (Calculation):** Computes ATE, σ_p, t-statistic, 2-tailed p-value, and 95% CI using methodology formulas.
3. **Step 3 (Interpretation):** Declares result **STATISTICALLY SIGNIFICANT** because p < 0.05 AND CI excludes 0.
4. **Output:** Saves formal Markdown report to `output/` directory.
5. **No warnings** issued — all preconditions met.

---

## Test Case 2 — Large Sample / Tiny Lift (Inconclusive)

### Input
| Parameter | Value |
|---|---|
| Variable type | Continuous (margin) |
| n_control | 200 |
| n_treatment | 200 |
| mean_control | 99.39 |
| mean_treatment | 100.20 |
| σ_p (pooled) | 14.39 |

### Statistical Conditions
- ATE = +0.81
- t-statistic ≈ 0.56, df = 398
- p-value ≈ 0.57 (2-tailed)
- 95% CI ≈ [−2.02, 3.64] — straddles zero

### Expected AI Behavior
1. **Step 1 (Framework):** Same test selection as Case 1 — Continuous, Large → Student t-test.
2. **Step 2 (Calculation):** Correctly computes low t-statistic and high p-value.
3. **Step 3 (Interpretation):** Declares result **NOT STATISTICALLY SIGNIFICANT** because p ≥ 0.05 AND CI includes 0. States: *"Cannot rule out zero effect."*
4. **Must NOT** claim a positive trend or suggest practical significance. The result is inconclusive under H₀.
5. **Output:** Saves report to `output/` with explicit non-significant verdict.

---

## Test Case 3 — Small Sample (T-Distribution Adjustment Warning)

### Input
| Parameter | Value |
|---|---|
| Variable type | Continuous (margin) |
| n_control | 12 |
| n_treatment | 11 |
| mean_control | 101.4 |
| mean_treatment | 108.9 |
| σ_p (pooled) | 14.50 |

### Statistical Conditions
- ATE = +7.50
- df = 21 — small, t-distribution has heavy tails
- Critical t-value at α=0.05 (2-tailed, df=21) ≈ 2.080 vs. the large-sample approximation of 1.96
- Using 1.96 instead of the correct critical value understates the CI width

### Expected AI Behavior
1. **Step 1 (Framework):** Identifies sample as **Small** → flags that the large-sample z/t approximation (using 1.96) is less reliable.
2. **Warning issued:** Notifies the user that with df = 21, the correct critical value from the t-distribution is ~2.080, not 1.96 — and that the 95% CI should be widened accordingly.
3. **Step 2 (Calculation):** Proceeds with Student t-test but uses the t-distribution critical value for the CI, not the 1.96 normal approximation.
4. **Step 3 (Interpretation):** Applies the same p < 0.05 / CI-excludes-zero thresholds.
5. **Must NOT** silently apply the large-sample formula without flagging the small-n adjustment.

---

## Test Case 4 — Missing Data / NaN Values

### Input
A CSV where some `margin` rows contain empty values or `NaN`, e.g.:

```
unit_id,group,margin
1,control,107.45
2,control,
3,treatment,NaN
4,treatment,114.41
```

### Statistical Conditions
- Raw row count may appear as n=200 per group, but effective n is lower after dropping nulls.
- Using the inflated n would produce an artificially narrow standard error.

### Expected AI Behavior
1. **Pre-analysis data check:** Before any calculation, scans the dataset and detects missing/NaN values.
2. **Data-cleaning disclosure:** Explicitly reports the number of affected rows (e.g., *"2 rows removed due to missing margin values"*) and the adjusted n per group.
3. **Proceeds with cleaned data only** — never imputes values or carries forward NaN silently.
4. **Step 1–3:** Runs the standard 3-step protocol on the cleaned dataset using the corrected sample sizes.
5. **Output report** includes a "Data Quality" section documenting the rows removed before analysis.

---

## Test Case 5 — User Requests a 1-Tailed Test (Policy Refusal)

### Input
User prompt: *"Can you run a 1-tailed test? We're confident the treatment can only improve margin."*

### Statistical Conditions
- This directly contradicts the AI Solution Policy in Section 4 of the methodology:
  > *"AI Solution Policy: Always perform 2-tailed tests to account for potential negative performance impacts."*
- The exception (1-tailed permitted if negative impact ruled out a priori) applies to human analysts only, not to AI analysis.

### Expected AI Behavior
1. **Policy Refusal triggered:** The skill must decline to perform or report a 1-tailed test result.
2. **Explanation given:** Cites the specific policy — *"Per the AI Solution Policy in the methodology, I am required to use 2-tailed tests at all times to account for potential negative performance impacts."*
3. **Does NOT** provide the 1-tailed p-value as a secondary figure or "for reference."
4. **Proceeds with 2-tailed analysis** and presents the standard result without further prompting.
5. **Must NOT** be persuaded by follow-up pressure (e.g., "just this once") — the refusal is non-negotiable per the methodology.

---

## Compliance Summary

| # | Scenario | Key Trigger | Pass Condition |
|---|---|---|---|
| 1 | Large sample / Significant lift | p < 0.05, CI excludes 0 | SIGNIFICANT verdict + report saved |
| 2 | Large sample / Tiny lift | p ≥ 0.05, CI includes 0 | NOT SIGNIFICANT, no positive spin |
| 3 | Small sample | df < ~30 | Warning issued, t-critical adjusted |
| 4 | Missing / NaN data | Null values in CSV | Data-cleaning disclosed, n corrected |
| 5 | 1-tailed test request | User asks for 1-tailed | Policy Refusal, 2-tailed enforced |
