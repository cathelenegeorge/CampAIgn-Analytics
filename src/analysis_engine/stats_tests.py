# src/analysis_engine/stats_tests.py
import numpy as np
import pandas as pd
from typing import Dict, Any
from scipy.stats import ttest_ind
from statsmodels.stats.proportion import proportions_ztest
import math

def run_ab_tests(df: pd.DataFrame, revenue_col: str = None) -> Dict[str, Any]:
    """
    Run statistics for:
     - proportion z-test for conversion rate (purchases / reach)
     - t-test for revenue per user (or revenue estimate)
    Return p-values, test statistics, confidence intervals approximations.
    """
    results = {}

    # ensure groups exist
    groups = df['group'].unique().tolist()
    if not ('A' in groups and 'B' in groups):
        results['error'] = "Both groups A (control) and B (test) required."
        return results

    df_A = df[df['group'] == 'A']
    df_B = df[df['group'] == 'B']

    # ---------- Proportion z-test (conversion rates) ----------
    # counts = total purchases, nobs = total reach
    count = np.array([df_A['# of Purchase'].sum(), df_B['# of Purchase'].sum()])
    nobs = np.array([df_A['Reach'].sum(), df_B['Reach'].sum()])

    stat, pval = proportions_ztest(count, nobs)
    # compute pooled prop and se for crude CI on diff
    p1 = count[0] / nobs[0]
    p2 = count[1] / nobs[1]
    diff = p2 - p1
    pooled = (count.sum()) / (nobs.sum())
    se = math.sqrt(pooled * (1 - pooled) * (1 / nobs[0] + 1 / nobs[1]))
    # 95% CI
    z = 1.96
    ci_lower = diff - z * se
    ci_upper = diff + z * se

    results['conversion_rate_test'] = {
        'statistic': float(stat),
        'pvalue': float(pval),
        'cr_A': float(p1),
        'cr_B': float(p2),
        'diff': float(diff),
        'ci_95': [float(ci_lower), float(ci_upper)]
    }

    # ---------- T-test on revenue per user ----------
    # compute revenue per reach (rpu) per row
    if revenue_col and revenue_col in df.columns:
        df['revenue'] = df[revenue_col]
    else:
        df['revenue'] = df['# of Purchase']  # fallback: purchases as proxy

    # revenue per user (per reach)
    if 'rpu' not in df.columns:
        df['rpu'] = df['revenue'] / df['Reach']
    
    df_A = df[df['group'] == 'A']
    df_B = df[df['group'] == 'B']

    rpu_A = df_A['rpu'].dropna()
    rpu_B = df_B['rpu'].dropna()

    # Use Welch's t-test (unequal variances)
    tstat, tpval = ttest_ind(rpu_A, rpu_B, equal_var=False, nan_policy='omit')

    # compute 95% CI of difference using standard methods (approx)
    # We'll compute mean difference and standard error:
    mean_diff = float(rpu_B.mean() - rpu_A.mean())
    se_diff = math.sqrt(rpu_A.var(ddof=1)/len(rpu_A) + rpu_B.var(ddof=1)/len(rpu_B))
    ci_lower_rpu = mean_diff - z * se_diff
    ci_upper_rpu = mean_diff + z * se_diff

    results['rpu_ttest'] = {
        'tstatistic': float(tstat),
        'pvalue': float(tpval),
        'rpu_A_mean': float(rpu_A.mean()),
        'rpu_B_mean': float(rpu_B.mean()),
        'mean_diff': mean_diff,
        'ci_95': [float(ci_lower_rpu), float(ci_upper_rpu)]
    }

    return results
