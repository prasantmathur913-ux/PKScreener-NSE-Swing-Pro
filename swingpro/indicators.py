from __future__ import annotations
import numpy as np
import pandas as pd

def rsi(series: pd.Series, period: int = 14) -> pd.Series:
    delta = series.diff()
    gain = delta.clip(lower=0).ewm(alpha=1/period, adjust=False, min_periods=period).mean()
    loss = -delta.clip(upper=0).ewm(alpha=1/period, adjust=False, min_periods=period).mean()
    rs = gain / loss.replace(0, np.nan)
    out = 100 - (100 / (1 + rs))
    return out.fillna(100).where(loss.eq(0), out)

def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    close, high, low, volume = out.Close, out.High, out.Low, out.Volume
    out["EMA20"] = close.ewm(span=20, adjust=False).mean()
    out["EMA50"] = close.ewm(span=50, adjust=False).mean()
    out["EMA200"] = close.ewm(span=200, adjust=False).mean()
    out["RSI14"] = rsi(close)
    fast = close.ewm(span=12, adjust=False).mean()
    slow = close.ewm(span=26, adjust=False).mean()
    out["MACD"] = fast - slow
    out["MACD_SIGNAL"] = out.MACD.ewm(span=9, adjust=False).mean()
    out["MACD_HIST"] = out.MACD - out.MACD_SIGNAL
    prev_close = close.shift(1)
    tr = pd.concat([(high-low), (high-prev_close).abs(), (low-prev_close).abs()], axis=1).max(axis=1)
    out["ATR14"] = tr.ewm(alpha=1/14, adjust=False, min_periods=14).mean()
    up = high.diff()
    down = -low.diff()
    plus_dm = up.where((up > down) & (up > 0), 0.0)
    minus_dm = down.where((down > up) & (down > 0), 0.0)
    atr = out.ATR14.replace(0, np.nan)
    plus_di = 100 * plus_dm.ewm(alpha=1/14, adjust=False).mean() / atr
    minus_di = 100 * minus_dm.ewm(alpha=1/14, adjust=False).mean() / atr
    dx = 100 * (plus_di-minus_di).abs() / (plus_di+minus_di).replace(0, np.nan)
    out["ADX14"] = dx.ewm(alpha=1/14, adjust=False).mean()
    out["VOL_MA20"] = volume.rolling(20).mean()
    out["REL_VOLUME"] = volume / out.VOL_MA20.replace(0, np.nan)
    out["HIGH20_PREV"] = high.shift(1).rolling(20).max()
    out["HIGH55_PREV"] = high.shift(1).rolling(55).max()
    return out
