# PKScreener NSE Swing Pro

A modular NSE swing-trading research screener designed to run alongside PKScreener without changing upstream internals.

## Features

- Primary market data: `jugaad_data.nse`; fallback: `yfinance`.
- EMA 20/50/200, RSI(14), MACD, ADX(14), ATR(14), average volume and relative volume.
- Breakout proximity, trend filters and transparent 0–100 heuristic ranking.
- Indicative entry, +3%/+5% targets and ATR-based stop reference.
- Streamlit dashboard, CSV export and simplified historical signal evaluation.
- No broker integration or order placement.

## Quick start

Python 3.12 is recommended.

```bash
python -m venv .venv
# Windows: .venv\\Scripts\\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

Edit `data/universe.csv` to set NSE symbols. Start with a small universe to respect data-provider rate limits.

## Data notes

The primary provider may be affected by NSE endpoint changes, throttling or availability. On errors or insufficient primary data, the application falls back to Yahoo Finance. The fallback is not guaranteed to be real-time. The initial release is intended for end-of-day screening.

## Running tests

```bash
pytest -q
```

## Integration approach

This release is a standalone companion/add-on. It does not yet import or patch PKScreener internals. A pinned-version adapter can be added after compatibility tests against a selected upstream PKScreener release.

## Risk notice

Scores are heuristic rankings, not calibrated probabilities or return forecasts. Backtests are simplified and omit brokerage, taxes, slippage, liquidity, gaps and survivorship bias. Validate strategies out of sample before relying on them. This software does not place trades.