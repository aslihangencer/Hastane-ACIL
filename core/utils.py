import pandas as pd
import numpy as np

def safe_int(value, default=0):
    """
    Safely converts values to int.
    Handles numpy.int64, None, NaN.
    """
    try:
        if pd.isna(value):
            return default
        return int(value)
    except (ValueError, TypeError):
        return default

def safe_float(value, default=0.0):
    """
    Safely converts values to float.
    """
    try:
        if pd.isna(value):
            return default
        return float(value)
    except (ValueError, TypeError):
        return default

def safe_str(value, default=""):
    """
    Safely converts values to string.
    """
    try:
        if value is None or pd.isna(value):
            return default
        return str(value).strip()
    except Exception:
        return default

def safe_df(df):
    """
    Returns empty dataframe if None.
    """
    if df is None:
        return pd.DataFrame()
    if not isinstance(df, pd.DataFrame):
        return pd.DataFrame()
    return df.copy()

def format_wait_time(minutes):
    """
    Formats minutes into dk, sa, or gün.
    """
    try:
        minutes = int(minutes)
        if minutes < 60:
            return f"{minutes} dk"
        hours = minutes // 60
        if hours < 24:
            return f"{hours} sa"
        days = hours // 24
        return f"{days} gün"
    except:
        return "-"
