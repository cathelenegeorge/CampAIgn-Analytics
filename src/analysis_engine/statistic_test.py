# src/analysis_engine/stats_tests.py
from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Any, Optional, Tuple, Literal
import numpy as np
import pandas as pd
from scipy.stats import ttest_ind
from statsmodels.stats.proportion import proportions_ztest, proportion_confint

@dataclass
class PropTestResult:
    statistic: float
    pvalue: float
    cr_A: float
    cr_B: float
    diff: float
    diff_ci_95: Tuple[float, float]
    A_ci_95: Tuple[float, float]
    B_ci_95: Tuple[float, float]
    numerator: str
    denominator: str

@dataclass
class RPUTestResult:
    tstatistic: float
    pvalue: float
    rpu_A_mean: float
    rpu_B_mean: float
    mean_diff: float
    ci_95: Tuple[float, float]
    note: str

def _safe_rate(num: float, den: float) -> float:
    return float(num / den) if den and den > 0 else np.nan

def _prop_test(numA: float, denA: float, numB: float, denB: float,
               numerator: str, denominator: str, alpha: float = 0.05) -> Dict[str, Any]:
    """Two-proportion z-test with Wilson CIs per group and normal-approx diff CI."""
    crA = _safe_rate(numA, denA)
    crB = _safe_rate(numB, denB)

    if (denA > 0) and (denB > 0):
        # z-test
        stat, pval = proportions_ztest(count=[numA, numB], nobs=[denA, denB])

        # diff CI (normal approx)
        pooled = (numA + numB) / (denA + denB)
        se_diff = np.sqrt(pooled * (1 - pooled) * (1 / denA + 1 / denB))
        z = 1.96
        diff = crB - crA
        diff_ci = (float(diff - z * se_diff), float(diff + z * se_diff))

        # Per-group Wilson CIs
        A_low, A_high = proportion_confint(numA, denA, alpha=alpha, method="wilson")
        B_low, B_high = proportion_confint(numB, denB, alpha=alpha, method="wilson")

        return PropTestResult(
            statistic=float(stat),
            pvalue=float(pval),
            cr_A=float(crA),
            cr_B=float(crB),
            diff=float(diff),
            diff_ci_95=(float(diff_ci[0]), float(diff_ci[1])),
            A_ci_95=(float(A_low), float(A_high)),
            B_ci_95=(float(B_low), float(B_high)),
            numerator=numerator,
            denominator=denominator
        ).__dict__
    else:
        return {
            "error": "Zero/invalid denominator for one or both groups.",
            "cr_A": crA,
            "cr_B": crB,
            "numerator": numerator,
            "denominator": denominator
        }

def run_ab_tests(
    df: pd.DataFrame,
    revenue_col: Optional[str] = None,
    alpha: float = 0.05,
    conv_denominator: Literal["Clicks", "Reach", "Both"] = "Clicks",
    bootstrap_rpu: bool = True,
    bootstrap_iter: int = 5000,
    random_state: Optional[int] = 42
) -> Dict[str, Any]:
    """
    Run A/B tests with configurable conversion-rate definition:

      - conv_denominator="Clicks" : CR = Purchases / Clicks
      - conv_denominator="Reach"  : CR = Purchases / Reach
      - conv_denominator="Both"   : Returns both CR tests

    Also runs a Welch t-test on RPU (revenue per reach) with optional bootstrap CI.

    Expected columns in df:
      'group' in {'A','B'},
      '# of Purchase', '# of Website Clicks', 'Reach'
      Optional revenue column (revenue_col); if absent, uses purchases as proxy.
    """
    out: Dict[str, Any] = {}
    dx = df.copy()

    # Validate groups
    groups = set(dx.get("group", pd.Series(dtype=object)).unique())
    if not {"A", "B"}.issubset(groups):
        return {"error": "Both groups A and B required in 'group' column."}

    A = dx[dx["group"] == "A"].copy()
    B = dx[dx["group"] == "B"].copy()

    # Aggregate counts
    numA = float(pd.to_numeric(A["# of Purchase"], errors="coerce").sum())
    numB = float(pd.to_numeric(B["# of Purchase"], errors="coerce").sum())
    clicksA = float(pd.to_numeric(A["# of Website Clicks"], errors="coerce").sum())
    clicksB = float(pd.to_numeric(B["# of Website Clicks"], errors="coerce").sum())
    reachA  = float(pd.to_numeric(A["Reach"], errors="coerce").sum())
    reachB  = float(pd.to_numeric(B["Reach"], errors="coerce").sum())

    # --- Conversion rate tests ---
    if conv_denominator in ("Clicks", "Both"):
        out["cr_click_based"] = _prop_test(
            numA, clicksA, numB, clicksB,
            numerator="# of Purchase", denominator="# of Website Clicks", alpha=alpha
        )

    if conv_denominator in ("Reach", "Both"):
        out["cr_reach_based"] = _prop_test(
            numA, reachA, numB, reachB,
            numerator="# of Purchase", denominator="Reach", alpha=alpha
        )

    # --- RPU test (revenue per reach, row-level) ---
    if revenue_col and revenue_col in dx.columns:
        dx["_revenue"] = pd.to_numeric(dx[revenue_col], errors="coerce")
        note = f"Used revenue column '{revenue_col}'."
    else:
        dx["_revenue"] = pd.to_numeric(dx["# of Purchase"], errors="coerce")
        note = "No revenue_col provided—using '# of Purchase' as proxy revenue."

    reach_nonzero = pd.to_numeric(dx["Reach"], errors="coerce").replace(0, np.nan)
    dx["_rpu"] = dx["_revenue"] / reach_nonzero

    rpu_A = dx.loc[dx["group"] == "A", "_rpu"].dropna()
    rpu_B = dx.loc[dx["group"] == "B", "_rpu"].dropna()

    if (len(rpu_A) >= 2) and (len(rpu_B) >= 2):
        tstat, tpval = ttest_ind(rpu_A, rpu_B, equal_var=False, nan_policy="omit")

        # Normal approx CI for mean difference
        z = 1.96
        mean_diff = float(rpu_B.mean() - rpu_A.mean())
        se_diff = np.sqrt(rpu_A.var(ddof=1) / len(rpu_A) + rpu_B.var(ddof=1) / len(rpu_B))
        ci = (float(mean_diff - z * se_diff), float(mean_diff + z * se_diff))

        # Bootstrap CI (optional)
        if bootstrap_rpu:
            rng = np.random.default_rng(random_state)
            boots = []
            nA, nB = len(rpu_A), len(rpu_B)
            rA, rB = rpu_A.to_numpy(), rpu_B.to_numpy()
            for _ in range(bootstrap_iter):
                mA = rng.choice(rA, size=nA, replace=True).mean()
                mB = rng.choice(rB, size=nB, replace=True).mean()
                boots.append(mB - mA)
            lo = float(np.percentile(boots, 2.5))
            hi = float(np.percentile(boots, 97.5))
            ci = (lo, hi)
            note += " CI via bootstrap of row-level RPU means."

        out["rpu_ttest"] = RPUTestResult(
            tstatistic=float(tstat),
            pvalue=float(tpval),
            rpu_A_mean=float(rpu_A.mean()),
            rpu_B_mean=float(rpu_B.mean()),
            mean_diff=float(mean_diff),
            ci_95=ci,
            note=note
        ).__dict__
    else:
        out["rpu_ttest"] = {
            "error": "Insufficient rows for RPU t-test.",
            "len_A": int(len(rpu_A)),
            "len_B": int(len(rpu_B)),
            "note": "Need at least 2 non-NaN rows per group."
        }

    return out
