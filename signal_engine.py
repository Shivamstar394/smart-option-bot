import pandas as pd
import numpy as np
from ta.trend import EMAIndicator
from ta.momentum import RSIIndicator
from ta.volatility import AverageTrueRange

def add_indicators(df: pd.DataFrame, ema_fast=20, ema_slow=50, rsi_period=14, atr_period=14) -> pd.DataFrame:
    df = df.copy()
    df["ema_fast"] = EMAIndicator(df["close"], window=ema_fast).ema_indicator()
    df["ema_slow"] = EMAIndicator(df["close"], window=ema_slow).ema_indicator()
    df["rsi"] = RSIIndicator(df["close"], window=rsi_period).rsi()
    atr = AverageTrueRange(df["high"], df["low"], df["close"], window=atr_period)
    df["atr"] = atr.average_true_range()
    return df

def generate_signals(df: pd.DataFrame, rsi_long=55, rsi_short=45) -> pd.DataFrame:
    df = df.copy()
    df["bias"] = np.where(df["ema_fast"] > df["ema_slow"], 1, -1)
    df["long_signal"] = (df["bias"] == 1) & (df["rsi"].shift(1) <= rsi_long) & (df["rsi"] > rsi_long)
    df["short_signal"] = (df["bias"] == -1) & (df["rsi"].shift(1) >= rsi_short) & (df["rsi"] < rsi_short)
    return df



