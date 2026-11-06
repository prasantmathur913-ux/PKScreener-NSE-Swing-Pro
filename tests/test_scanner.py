import numpy as np
import pandas as pd
from swingpro.indicators import add_indicators
from swingpro.scanner import analyse_symbol
from swingpro.backtest import evaluate_signals

def sample_data(n=260):
    idx = pd.bdate_range("2024-01-01", periods=n)
    close = pd.Series(np.linspace(100, 160, n) + np.sin(np.arange(n)/5), index=idx)
    return pd.DataFrame({"Open": close*0.999, "High": close*1.015, "Low": close*0.985,
                         "Close": close, "Volume": np.full(n, 200000)}, index=idx)

def test_indicators_added():
    out = add_indicators(sample_data())
    for col in ["EMA20", "EMA50", "RSI14", "MACD_HIST", "ATR14", "ADX14", "REL_VOLUME"]:
        assert col in out.columns
    assert out.iloc[-1]["ATR14"] > 0

def test_analyse_symbol_has_risk_levels():
    result = analyse_symbol("TEST", sample_data(), "unit-test")
    assert 0 <= result["Score"] <= 100
    assert result["Target 3%"] > result["CMP"]
    assert result["Target 5%"] > result["Target 3%"]
    assert result["Stop Loss"] < result["CMP"]

def test_backtest_returns_dataframe():
    result = evaluate_signals(sample_data())
    assert isinstance(result, pd.DataFrame)
