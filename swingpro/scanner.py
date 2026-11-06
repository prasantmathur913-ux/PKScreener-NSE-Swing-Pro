from __future__ import annotations
import pandas as pd
from .indicators import add_indicators

def score_row(row: pd.Series) -> tuple[int, list[str]]:
    score, reasons = 0, []
    checks = [
        (row.EMA20 > row.EMA50 and row.Close > row.EMA20, 20, "EMA20 > EMA50; close > EMA20"),
        (row.EMA50 > row.EMA200, 10, "EMA50 > EMA200"),
        (55 <= row.RSI14 <= 70, 15, "RSI 55–70"),
        (row.MACD_HIST > 0, 10, "Positive MACD histogram"),
        (row.ADX14 >= 20, 10, "ADX >= 20"),
        (row.REL_VOLUME >= 1.5, 15, "Relative volume >= 1.5x"),
        (row.Close >= row.HIGH20_PREV * 0.98, 10, "Within 2% of prior 20-day high"),
        (row.Close >= row.HIGH55_PREV * 0.95, 10, "Within 5% of prior 55-day high"),
    ]
    for passed, points, label in checks:
        if bool(passed):
            score += points
            reasons.append(label)
    return score, reasons

def analyse_symbol(symbol: str, ohlcv: pd.DataFrame, provider: str = "unknown") -> dict:
    data = add_indicators(ohlcv)
    row = data.iloc[-1]
    score, reasons = score_row(row)
    entry = float(row.Close)
    atr = float(row.ATR14)
    stop = max(0.0, entry - 1.5 * atr)
    risk = entry - stop
    return {
        "Symbol": symbol.upper(), "Date": data.index[-1].date().isoformat(),
        "CMP": round(entry, 2), "Score": int(score), "RSI": round(float(row.RSI14), 1),
        "ADX": round(float(row.ADX14), 1), "Rel Volume": round(float(row.REL_VOLUME), 2),
        "EMA20": round(float(row.EMA20), 2), "EMA50": round(float(row.EMA50), 2),
        "EMA200": round(float(row.EMA200), 2), "Breakout 20D": bool(row.Close > row.HIGH20_PREV),
        "Entry": round(entry, 2), "Target 3%": round(entry * 1.03, 2),
        "Target 5%": round(entry * 1.05, 2), "Stop Loss": round(stop, 2),
        "Risk %": round((risk / entry) * 100, 2) if entry else None,
        "Provider": provider, "Reasons": "; ".join(reasons),
        "Shortlist": bool(score >= 60 and row.Close > row.EMA20 and 50 <= row.RSI14 <= 75 and row.REL_VOLUME >= 1.2),
    }

def scan_symbols(symbols: list[str], fetcher, min_score: int = 60) -> tuple[pd.DataFrame, list[str]]:
    rows, errors = [], []
    for symbol in symbols:
        try:
            result = fetcher(symbol)
            rows.append(analyse_symbol(symbol, result.data, result.provider))
        except Exception as exc:
            errors.append(f"{symbol}: {exc}")
    frame = pd.DataFrame(rows)
    if not frame.empty:
        frame = frame[frame.Score >= min_score].sort_values(["Score", "Rel Volume"], ascending=False).reset_index(drop=True)
    return frame, errors
