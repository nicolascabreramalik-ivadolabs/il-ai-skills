# Methodology: A/B Test Results Analysis

## 1. Core Metrics
- **Average Treatment Effect (ATE):** The observed difference in performance metric expectations between the treatment group ($Y_t$) and control group ($Y_c$).
  - $$ATE = \bar{Y}_t - \bar{Y}_c$$
- **Confidence:** Derived from the magnitude of the ATE relative to the variance observed in the data.

## 2. Statistical Framework: Frequentist Approach
We primarily utilize the **Frequentist** approach (Null Hypothesis Significance Testing).
- **Null Hypothesis ($H_0$):** Treatment has no impact; the difference in means is null.
- **P-value:** The probability of obtaining results at least as extreme as the observed data, assuming $H_0$ is true.
- **Significance Level ($\alpha$):** Standardized at **5% (0.05)**.
  - $p < 0.05$: Reject $H_0$ (95% confidence).
  - $p \ge 0.05$: Fail to reject $H_0$; cannot rule out zero effect.

## 3. Decision Logic for Statistical Tests
The choice of test depends on the variable type and sample size:

| Variable Type | Sample Size | Recommended Test |
| :--- | :--- | :--- |
| **Continuous** (e.g., margin) | Large | Student t-test (Equal variance) or Welch t-test |
| **Continuous** (e.g., margin) | Known Std Dev | Z-test (Rare) |
| **Discrete/Binary** (e.g., CTR) | Large | Pearson Chi-square test |
| **Discrete/Binary** (e.g., CTR) | Small | Fisher’s exact test |

### Student t-test Formula
Used for continuous variables with large samples and similar variances:
$$t = \frac{\bar{Y}_t - \bar{Y}_c}{\sigma_p \sqrt{\frac{1}{n_t} + \frac{1}{n_c}}}$$
*Where $\sigma_p$ is the pooled standard deviation and $n$ is the sample size.*

## 4. Directionality
- **Standard:** 2-tailed t-test.
- **Exception:** 1-tailed is only permitted if a negative impact can be ruled out a priori. 
- **AI Solution Policy:** Always perform **2-tailed tests** to account for potential negative performance impacts.