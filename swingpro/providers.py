from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol
import pandas as pd

REQUIRED = {"Open", "High", "Low", "Close", "Volume"}

class DataProvider(Protocol):
    name: str
    def history(self, symbol: str, period: str = "1y", interval: str = "1d") -> pd.DataFrame: ...

@dataclass
class FetchResult:
    symbol: str
    data: pd.DataFrame
    provider: str
    errors: list[str]

def normalize_ohlcv(frame: pd.DataFrame) -> pd.DataFrame:
    if frame is None or frame.empty:
        raise ValueError("Provider returned no OHLCV rows")
    df = frame.copy()
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = [c[0] if isinstance(c, tuple) else c for c in df.columns]
    aliases = {str(c).lower(): c for c in df.columns}
    rename = {}
    for standard in REQUIRED:
        key = standard.lower()
        if standard not in df.columns and key in aliases:
            rename[aliases[key]] = standard
    df = df.rename(columns=rename)
    missing = REQUIRED - set(df.columns)
    if missing:
        raise ValueError(f"Missing OHLCV columns: {sorted(missing)}")
    df = df[list(REQUIRED)].copy()
    df.index = pd.to_datetime(df.index)
    if getattr(df.index, "tz", None) is not None:
        df.index = df.index.tz_localize(None)
    for col in REQUIRED:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df = df.dropna(subset=["Open", "High", "Low", "Close", "Volume"])
    df = df[~df.index.duplicated(keep="last")].sort_index()
    if len(df) < 60:
        raise ValueError(f"Insufficient history: {len(df)} rows; need at least 60")
    return df

class JugaadNSEProvider:
    name = "jugaad_data.nse"
    def history(self, symbol: str, period: str = "1y", interval: str = "1d") -> pd.DataFrame:
        if interval != "1d":
            raise ValueError("Jugaad primary provider currently configured for daily OHLCV only")
        try:
            from jugaad_data.nse import stock_df
        except Exception as exc:
            raise RuntimeError(f"Could not import jugaad_data.nse.stock_df: {exc}") from exc
        end = pd.Timestamp.now().date()
        start = (pd.Timestamp.now() - pd.Timedelta(days=420)).date()
        frame = stock_df(symbol=symbol.upper(), from_date=start, to_date=end, series="EQ")
        if frame is None or frame.empty:
            raise ValueError("jugaad_data returned no data")
        frame = frame.rename(columns={c: str(c).strip().title() for c in frame.columns})
        date_col = next((c for c in frame.columns if c.lower() in {"date", "timestamp"}), None)
        if date_col:
            frame[date_col] = pd.to_datetime(frame[date_col], errors="coerce", dayfirst=True)
            frame = frame.set_index(date_col)
        return frame

class YahooFinanceProvider:
    name = "yfinance"
    def history(self, symbol: str, period: str = "1y", interval: str = "1d") -> pd.DataFrame:
        import yfinance as yf
        ticker = symbol.upper() if "." in symbol else f"{symbol.upper()}.NS"
        frame = yf.download(ticker, period=period, interval=interval, auto_adjust=False, progress=False, threads=False)
        return normalize_ohlcv(frame)

def fetch_with_fallback(symbol: str, period: str = "1y", interval: str = "1d") -> FetchResult:
    errors: list[str] = []
    for provider in (JugaadNSEProvider(), YahooFinanceProvider()):
        try:
            frame = normalize_ohlcv(provider.history(symbol, period, interval))
            return FetchResult(symbol=symbol.upper(), data=frame, provider=provider.name, errors=errors)
        except Exception as exc:
            errors.append(f"{provider.name}: {type(exc).__name__}: {exc}")
    raise RuntimeError("All OHLCV providers failed for " + symbol + " | " + " | ".join(errors))
