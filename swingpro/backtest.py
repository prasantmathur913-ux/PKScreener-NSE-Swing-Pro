from __future__ import annotations
import pandas as pd
from .indicators import add_indicators

def evaluate_signals(ohlcv: pd.DataFrame, horizon: int = 10, target_pct: float = 0.03, atr_multiple: float = 1.5) -> pd.DataFrame:
    """Simplified EOD signal test; conservative stop-first on same-bar target/stop touches."""
    data = add_indicators(ohlcv)
    records = []
    for i in range(60, len(data) - horizon - 1):
        row = data.iloc[i]
        if not (row.EMA20 > row.EMA50 and row.Close > row.EMA20 and 50 <= row.RSI14 <= 75
                and row.REL_VOLUME >= 1.2 and row.ADX14 >= 15):
            continue
        entry_bar = data.iloc[i + 1]
        entry = float(entry_bar.Open)
        stop = entry - atr_multiple * float(row.ATR14)
        target = entry * (1 + target_pct)
        exit_price, exit_date, outcome = float(data.iloc[i+horizon].Close), data.index[i+horizon], "time_exit"
        for j in range(i+1, i+horizon+1):
            bar = data.iloc[j]
            if bar.Low <= stop:
                exit_price, exit_date, outcome = stop, data.index[j], "stop"
                break
            if bar.High >= target:
                exit_price, exit_date, outcome = target, data.index[j], "target"
                break
        records.append({"Signal Date": data.index[i], "Entry Date": data.index[i+1], "Exit Date": exit_date,
                        "Entry": entry, "Exit": exit_price, "Outcome": outcome,
                        "Return %": (exit_price / entry - 1) * 100})
    return pd.DataFrame(records)
