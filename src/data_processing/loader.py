# src/data_processing/loader.py
import pandas as pd
from pathlib import Path

DATA_RAW = Path("data/raw/campaign_data.csv")

def load_data(path: str = None) -> pd.DataFrame:
    """
    Load raw CSV to pandas DataFrame.
    If path is None, uses DATA_RAW constant.
    """
    p = Path(path) if path else DATA_RAW
    df = pd.read_csv(p)
    return df
