# src/data_processing/cleaner.py
import pandas as pd
from pathlib import Path

def extract_group(campaign_name: str) -> str:
    """
    Heuristic: if 'Control' in campaign_name => 'A' (control),
    if 'Test' in campaign_name => 'B' (variant/test).
    Returns 'unknown' if cannot determine.
    """
    name = str(campaign_name).lower()
    if "control" in name:
        return "A"
    if "test" in name or "variant" in name:
        return "B"
    return "unknown"

def clean_data(df: pd.DataFrame, save_path: str = "data/processed/cleaned_campaign.csv") -> pd.DataFrame:
    """
    Clean raw DataFrame:
      - Normalize column names
      - Convert numeric columns to numeric
      - Parse date
      - Extract group (A/B) from Campaign Name
      - Drop rows where Reach is zero or NaN (can't compute CR)
      - Save cleaned CSV
    """
    df = df.copy()
    # Normalize column names
    df.columns = [c.strip() for c in df.columns]

    # Parse date
    try:
        df['Date'] = pd.to_datetime(df['Date'], dayfirst=True, errors='coerce')
    except Exception:
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')

    # Extract group
    df['group'] = df['Campaign Name'].apply(extract_group)

    # Numeric conversions for measured columns
    numeric_cols = ['Spend [USD]', '# of Impressions', 'Reach',
                    '# of Website Clicks', '# of Searches', '# of View Content',
                    '# of Add to Cart', '# of Purchase']

    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')

    # Basic cleaning: drop rows without Reach or purchases
    df = df.dropna(subset=['Reach'])  # need reach to compute CR
    df = df[df['Reach'] > 0]

    # Fill NaN purchases with 0
    if '# of Purchase' in df.columns:
        df['# of Purchase'] = df['# of Purchase'].fillna(0).astype(int)

    # Save processed file
    Path(save_path).parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(save_path, index=False)

    return df
