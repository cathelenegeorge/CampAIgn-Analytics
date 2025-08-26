# src/analysis_engine/visualization.py
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import pandas as pd
from typing import Dict, Any

sns.set(style="whitegrid")

def ensure_reports_dir():
    Path("reports/charts").mkdir(parents=True, exist_ok=True)

def conversion_rate_chart(df: pd.DataFrame, save_path="reports/charts/conversion_rate_by_group.png"):
    ensure_reports_dir()
    agg = df.groupby('group').apply(lambda d: d['# of Purchase'].sum() / d['Reach'].sum()).reset_index(name='conversion_rate')
    plt.figure(figsize=(6,4))
    sns.barplot(x='group', y='conversion_rate', data=agg)
    plt.title("Conversion Rate by Group")
    plt.ylabel("Conversion Rate (purchases / reach)")
    plt.xlabel("Group")
    plt.tight_layout()
    plt.savefig(save_path)
    plt.close()
    return save_path

def roi_comparison_chart(metrics: Dict[str, Any], save_path="reports/charts/roi_comparison.png"):
    ensure_reports_dir()
    groups = []
    rois = []
    for g, info in metrics['groups'].items():
        groups.append(g)
        rois.append(info['roi'])
    plt.figure(figsize=(6,4))
    sns.barplot(x=groups, y=rois)
    plt.title("ROI by Group")
    plt.ylabel("ROI ( (revenue - spend) / spend )")
    plt.xlabel("Group")
    plt.tight_layout()
    plt.savefig(save_path)
    plt.close()
    return save_path

def revenue_distribution(df: pd.DataFrame, save_path="reports/charts/revenue_distribution.png", revenue_col=None):
    ensure_reports_dir()
    if revenue_col and revenue_col in df.columns:
        col = revenue_col
    else:
        df['revenue_est'] = df['# of Purchase']  # fallback
        col = 'revenue_est'

    plt.figure(figsize=(8,4))
    sns.histplot(df[col], kde=True)
    plt.title("Revenue (or Purchase Proxy) Distribution")
    plt.tight_layout()
    plt.savefig(save_path)
    plt.close()
    return save_path

def generate_charts(df: pd.DataFrame, metrics: Dict[str,Any], stats_results: Dict[str,Any]) -> Dict[str,str]:
    """
    Generate key charts and return dict of paths.
    """
    paths = {}
    paths['conversion_rate'] = conversion_rate_chart(df)
    paths['roi_comparison'] = roi_comparison_chart(metrics)
    paths['revenue_distribution'] = revenue_distribution(df)
    # optional more plots can be added here
    return paths
