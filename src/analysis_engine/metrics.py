# src/analysis_engine/metrics.py
import pandas as pd
from typing import Dict, Any

def compute_kpis(df: pd.DataFrame, avg_order_value: float = 50.0) -> Dict[str, Any]:
    """
    Compute KPIs aggregated by group and overall.
    avg_order_value: fallback to compute revenue = purchases * aov if revenue is absent.
    Returns a dict with group-level metrics and overall metrics.
    """

    df = df.copy()
    # If a revenue column exists, use it. Otherwise estimate revenue from purchases.
    revenue_col = None
    for candidate in ['Revenue', 'Revenue [USD]', 'revenue', 'revenue_usd']:
        if candidate in df.columns:
            revenue_col = candidate
            break

    if revenue_col is None:
        df['revenue_est'] = df['# of Purchase'] * avg_order_value
        revenue_col = 'revenue_est'

    # compute per-row metrics
    df['conversion_rate'] = df['# of Purchase'] / df['Reach']  # purchases per reached user
    df['revenue_per_user'] = df[revenue_col] / df['Reach']
    df['cost_per_purchase'] = df['Spend [USD]'] / (df['# of Purchase'].replace(0, pd.NA))

    # Aggregations by group
    agg_funcs = {
        'Spend [USD]': 'sum',
        '# of Impressions': 'sum',
        'Reach': 'sum',
        '# of Purchase': 'sum',
        revenue_col: 'sum',
    }

    group_agg = df.groupby('group').agg(agg_funcs).rename(columns={revenue_col: 'revenue'})

    result = {}
    for group, row in group_agg.iterrows():
        spend = row['Spend [USD]']
        revenue = row['revenue']
        purchases = row['# of Purchase']
        reach = row['Reach']
        impressions = row['# of Impressions']

        cr = purchases / reach if reach > 0 else 0
        rpu = revenue / reach if reach > 0 else 0
        roi = (revenue - spend) / spend if spend != 0 else None
        cpp = spend / purchases if purchases > 0 else None

        result[group] = {
            'spend': float(spend),
            'revenue': float(revenue),
            'purchases': int(purchases),
            'reach': int(reach),
            'impressions': int(impressions),
            'conversion_rate': float(cr),
            'revenue_per_user': float(rpu),
            'roi': float(roi) if roi is not None else None,
            'cost_per_purchase': float(cpp) if cpp is not None else None
        }

    # Lift calculations (B vs A)
    if 'A' in result and 'B' in result:
        a = result['A']
        b = result['B']
        lift = {
            'cr_lift_absolute': b['conversion_rate'] - a['conversion_rate'],
            'cr_lift_relative': (b['conversion_rate'] - a['conversion_rate']) / a['conversion_rate'] if a['conversion_rate'] else None,
            'roi_diff': b['roi'] - a['roi'] if (b['roi'] is not None and a['roi'] is not None) else None
        }
    else:
        lift = {}

    return {'groups': result, 'lift': lift}
