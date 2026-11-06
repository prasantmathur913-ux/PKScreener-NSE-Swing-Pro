import numpy as np
import pandas as pd

from swingpro.providers import normalize_ohlcv


def test_normalize_nse_stock_df_columns():
    dates = pd.bdate_range("2025-01-01", periods=65)
    close = np.linspace(100, 110, len(dates))
    raw = pd.DataFrame(
        {
            "DATE": dates.strftime("%d-%m-%Y"),
            "SERIES": ["EQ"] * len(dates),
            "OPEN": close - 0.5,
            "HIGH": close + 1,
            "LOW": close - 1,
            "CLOSE": close,
            "VOLUME": np.full(len(dates), 100_000),
        }
    )
    raw = raw.set_index(pd.to_datetime(raw.pop("DATE"), dayfirst=True))
    result = normalize_ohlcv(raw)
    assert list(result.columns) == ["Open", "High", "Low", "Close", "Volume"]
    assert len(result) == 65


def test_normalize_yfinance_multiindex_columns():
    dates = pd.bdate_range("2025-01-01", periods=65)
    frame = pd.DataFrame(
        {
            ("Open", "ABC.NS"): np.full(65, 100.0),
            ("High", "ABC.NS"): np.full(65, 102.0),
            ("Low", "ABC.NS"): np.full(65, 99.0),
            ("Close", "ABC.NS"): np.full(65, 101.0),
            ("Volume", "ABC.NS"): np.full(65, 100_000),
        },
        index=dates,
    )
    result = normalize_ohlcv(frame)
    assert result.iloc[-1]["Close"] == 101.0
