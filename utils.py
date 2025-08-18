import pandas as pd
import numpy as np
from datetime import datetime, timedelta, timezone

def iv_percentile(iv_series, lookback=252):
    s = iv_series.tail(lookback).dropna()
    if s.empty:
        return np.nan
    latest = s.iloc[-1]
    pct = (s <= latest).sum() / len(s) * 100
    return pct



def to_ist(ts):
    return pd.to_datetime(ts).tz_localize("UTC").tz_convert("Asia/Kolkata")

def from_ist(ts):
    return pd.to_datetime(ts).tz_localize("Asia/Kolkata").tz_convert("UTC")



def pct_change(a, b):
    if b == 0 or np.isnan(a) or np.isnan(b):
        return np.nan
    return (a - b) / b



