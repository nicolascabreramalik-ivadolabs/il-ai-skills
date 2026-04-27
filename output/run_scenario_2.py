import pandas as pd
import numpy as np
from scipy import stats
import statsmodels.formula.api as smf
import warnings
warnings.filterwarnings("ignore")

DATA_PATH = "/Users/nicolas.cabrera-malik/claude-internal-skills/docs/simulated_data/scenario_2.csv"
OUT_PATH  = "/Users/nicolas.cabrera-malik/claude-internal-skills/output/simulated_data/analysis_report_scenario_2.md"

df = pd.read_csv(DATA_PATH)

# ── Group flags ──────────────────────────────────────────────────────────────
df["Treated"] = (df["COHORT_ID"] == "Alternate").astype(int)
df["TriggerMode"] = df["TRIGGER_MODE"].map({"resultsPage": 1, "inlineSuggest": 0})

# ── Derived binary metrics ────────────────────────────────────────────────────
df["engaged"]  = df["ENGAGED_POSITIONS"].notna().astype(int)
df["ordered"]  = df["ORDERED_POSITIONS"].notna().astype(int)

# ── 99th-percentile outlier trimming (independent groups) ────────────────────
def trim_99(series, group_flag):
    result = series.copy().astype(float)
    for g in [0, 1]:
        mask = group_flag == g
        p99  = series[mask].quantile(0.99)
        result.loc[mask & (series > p99)] = np.nan
    return result

df["latency_trimmed"] = trim_99(df["LATENCY_MS"], df["Treated"])

# ── Helper: 2-tailed t-test summary ─────────────────────────────────────────
def ttest_summary(metric, treated_flag):
    g1 = metric[treated_flag == 1].dropna()
    g0 = metric[treated_flag == 0].dropna()
    ate = g1.mean() - g0.mean()
    nt, nc = len(g1), len(g0)
    sp = np.sqrt(((nt - 1)*g1.std()**2 + (nc - 1)*g0.std()**2) / (nt + nc - 2))
    se = sp * np.sqrt(1/nt + 1/nc)
    t  = ate / se
    p  = stats.t.sf(abs(t), df=nt+nc-2) * 2
    ci_lo, ci_hi = ate - 1.96*se, ate + 1.96*se
    return dict(mean_t=g1.mean(), mean_c=g0.mean(), nt=nt, nc=nc,
                ate=ate, se=se, t=t, p=p, ci_lo=ci_lo, ci_hi=ci_hi)

# ── Helper: Chi-square summary ───────────────────────────────────────────────
def chisq_summary(binary_metric, treated_flag):
    ct = pd.crosstab(treated_flag, binary_metric)
    chi2, p, dof, _ = stats.chi2_contingency(ct)
    r_t = binary_metric[treated_flag == 1].mean()
    r_c = binary_metric[treated_flag == 0].mean()
    ate = r_t - r_c
    n   = len(binary_metric)
    se  = np.sqrt(r_t*(1-r_t)/binary_metric[treated_flag==1].sum() +
                  r_c*(1-r_c)/binary_metric[treated_flag==0].sum())
    ci_lo, ci_hi = ate - 1.96*se, ate + 1.96*se
    return dict(rate_t=r_t, rate_c=r_c,
                nt=int((treated_flag==1).sum()), nc=int((treated_flag==0).sum()),
                ate=ate, se=se, chi2=chi2, p=p, ci_lo=ci_lo, ci_hi=ci_hi)

# ── Helper: HET OLS ──────────────────────────────────────────────────────────
def het_ols(formula, data):
    m = smf.ols(formula, data=data.dropna(subset=formula.split("~")[0].strip().split("+")
                                          + ["Treated","TriggerMode"])).fit()
    return m

# ══════════════════════════════════════════════════════════════════════════════
# 1. LATENCY_MS  (continuous → t-test + HET OLS)
# ══════════════════════════════════════════════════════════════════════════════
lat = ttest_summary(df["latency_trimmed"], df["Treated"])

lat_het_data = df[["latency_trimmed","Treated","TriggerMode"]].dropna()
lat_het = smf.ols("latency_trimmed ~ Treated + TriggerMode + Treated:TriggerMode",
                  data=lat_het_data).fit()

# ══════════════════════════════════════════════════════════════════════════════
# 2. ENGAGEMENT RATE  (binary → chi-square + HET logit)
# ══════════════════════════════════════════════════════════════════════════════
eng = chisq_summary(df["engaged"], df["Treated"])

eng_het = smf.ols("engaged ~ Treated + TriggerMode + Treated:TriggerMode",
                  data=df[["engaged","Treated","TriggerMode"]].dropna()).fit()

# ══════════════════════════════════════════════════════════════════════════════
# 3. ORDER RATE  (binary → chi-square + HET OLS)
# ══════════════════════════════════════════════════════════════════════════════
ord_ = chisq_summary(df["ordered"], df["Treated"])

ord_het = smf.ols("ordered ~ Treated + TriggerMode + Treated:TriggerMode",
                  data=df[["ordered","Treated","TriggerMode"]].dropna()).fit()

# ══════════════════════════════════════════════════════════════════════════════
# DISCOVERY
# ══════════════════════════════════════════════════════════════════════════════

# Cache hit breakdown by cohort
cache_dist = df.groupby(["COHORT_ID","ALT_FLOW_STATUS"]).size().unstack(fill_value=0)

# Latency by trigger mode and cohort
lat_by_mode = (df.groupby(["COHORT_ID","TRIGGER_MODE"])["latency_trimmed"]
               .agg(["mean","median","count"]).round(2))

# Engagement rate by trigger mode
eng_by_mode = (df.groupby(["COHORT_ID","TRIGGER_MODE"])["engaged"]
               .agg(["mean","count"]).round(4))

# Segment-level latency ATE by trigger mode
def seg_ttest(segment_val):
    sub = df[df["TRIGGER_MODE"] == segment_val]
    return ttest_summary(sub["latency_trimmed"], sub["Treated"])

lat_results = dict(resultsPage=seg_ttest("resultsPage"),
                   inlineSuggest=seg_ttest("inlineSuggest"))

# Segment-level engagement ATE by trigger mode
def seg_chisq(segment_val):
    sub = df[df["TRIGGER_MODE"] == segment_val]
    return chisq_summary(sub["engaged"], sub["Treated"])

eng_results = dict(resultsPage=seg_chisq("resultsPage"),
                   inlineSuggest=seg_chisq("inlineSuggest"))

# Simpsons paradox check: order rate by segment
ord_by_seg = (df.groupby(["COHORT_ID","TRIGGER_MODE"])["ordered"]
              .agg(["mean","sum","count"]).round(4))

# ══════════════════════════════════════════════════════════════════════════════
# PRINT STRUCTURED OUTPUT
# ══════════════════════════════════════════════════════════════════════════════

def sig(p, ci_lo, ci_hi):
    if p < 0.05 and not (ci_lo <= 0 <= ci_hi):
        return "**SIGNIFICANT** (p < 0.05, CI excludes 0)"
    return "Non-Significant"

print("=== LATENCY ===")
print(f"  Mean Alternate : {lat['mean_t']:.2f} ms")
print(f"  Mean Baseline  : {lat['mean_c']:.2f} ms")
print(f"  ATE            : {lat['ate']:.4f} ms")
print(f"  SE             : {lat['se']:.4f}")
print(f"  T-stat         : {lat['t']:.4f}")
print(f"  P-value        : {lat['p']:.6f}")
print(f"  95% CI         : [{lat['ci_lo']:.4f}, {lat['ci_hi']:.4f}]")
print(f"  n_t={lat['nt']}, n_c={lat['nc']}")
print(f"  Verdict        : {sig(lat['p'], lat['ci_lo'], lat['ci_hi'])}")
print()
print("  HET (Treated:TriggerMode interaction):")
delta = lat_het.params.get("Treated:TriggerMode", np.nan)
delta_p = lat_het.pvalues.get("Treated:TriggerMode", np.nan)
print(f"    Delta (interaction) = {delta:.4f}, p = {delta_p:.6f}")
print(f"    Beta (Treated main) = {lat_het.params['Treated']:.4f}, p = {lat_het.pvalues['Treated']:.6f}")

print("\n=== ENGAGEMENT RATE ===")
print(f"  Rate Alternate : {eng['rate_t']:.4f} ({eng['rate_t']*100:.2f}%)")
print(f"  Rate Baseline  : {eng['rate_c']:.4f} ({eng['rate_c']*100:.2f}%)")
print(f"  ATE            : {eng['ate']:.6f} ({eng['ate']*100:.4f} pp)")
print(f"  Chi2           : {eng['chi2']:.4f}")
print(f"  P-value        : {eng['p']:.6f}")
print(f"  95% CI         : [{eng['ci_lo']:.6f}, {eng['ci_hi']:.6f}]")
print(f"  n_t={eng['nt']}, n_c={eng['nc']}")
print(f"  Verdict        : {sig(eng['p'], eng['ci_lo'], eng['ci_hi'])}")
print()
print("  HET (Treated:TriggerMode interaction):")
e_delta = eng_het.params.get("Treated:TriggerMode", np.nan)
e_delta_p = eng_het.pvalues.get("Treated:TriggerMode", np.nan)
print(f"    Delta (interaction) = {e_delta:.6f}, p = {e_delta_p:.6f}")
print(f"    Beta (Treated main) = {eng_het.params['Treated']:.6f}, p = {eng_het.pvalues['Treated']:.6f}")

print("\n=== ORDER RATE ===")
print(f"  Rate Alternate : {ord_['rate_t']:.4f} ({ord_['rate_t']*100:.2f}%)")
print(f"  Rate Baseline  : {ord_['rate_c']:.4f} ({ord_['rate_c']*100:.2f}%)")
print(f"  ATE            : {ord_['ate']:.6f} ({ord_['ate']*100:.4f} pp)")
print(f"  Chi2           : {ord_['chi2']:.4f}")
print(f"  P-value        : {ord_['p']:.6f}")
print(f"  95% CI         : [{ord_['ci_lo']:.6f}, {ord_['ci_hi']:.6f}]")
print(f"  n_t={ord_['nt']}, n_c={ord_['nc']}")
print(f"  Verdict        : {sig(ord_['p'], ord_['ci_lo'], ord_['ci_hi'])}")
print()
print("  HET (Treated:TriggerMode interaction):")
o_delta = ord_het.params.get("Treated:TriggerMode", np.nan)
o_delta_p = ord_het.pvalues.get("Treated:TriggerMode", np.nan)
print(f"    Delta (interaction) = {o_delta:.6f}, p = {o_delta_p:.6f}")
print(f"    Beta (Treated main) = {ord_het.params['Treated']:.6f}, p = {ord_het.pvalues['Treated']:.6f}")

print("\n=== DISCOVERY ===")
print("Cache distribution:\n", cache_dist.to_string())
print("\nLatency by mode:\n", lat_by_mode.to_string())
print("\nEngagement by mode:\n", eng_by_mode.to_string())
print("\nLatency ATE by segment:")
for seg, r in lat_results.items():
    print(f"  {seg}: ATE={r['ate']:.2f}, p={r['p']:.4f}, CI=[{r['ci_lo']:.2f},{r['ci_hi']:.2f}]")
print("\nEngagement ATE by segment:")
for seg, r in eng_results.items():
    print(f"  {seg}: ATE={r['ate']:.4f}, p={r['p']:.4f}, CI=[{r['ci_lo']:.4f},{r['ci_hi']:.4f}]")
print("\nOrder rate by segment:\n", ord_by_seg.to_string())

print("\n=== SAMPLE SIZES ===")
print(df.groupby("COHORT_ID").size())
print(df.groupby(["COHORT_ID","TRIGGER_MODE"]).size())
