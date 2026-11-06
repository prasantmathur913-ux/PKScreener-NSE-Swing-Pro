from pathlib import Path
import pandas as pd
import streamlit as st
from swingpro.providers import fetch_with_fallback
from swingpro.scanner import scan_symbols

ROOT = Path(__file__).parent
st.set_page_config(page_title="PKScreener NSE Swing Pro", layout="wide")
st.title("PKScreener · NSE Swing Pro")
st.caption("Research screener for 2–10 trading-day setups. No order placement; scores are heuristics, not win probabilities.")

universe_path = ROOT / "data" / "universe.csv"
if universe_path.exists():
    default_symbols = pd.read_csv(universe_path)["symbol"].dropna().astype(str).str.upper().tolist()
else:
    default_symbols = ["RELIANCE", "HDFCBANK", "ICICIBANK", "INFY", "TCS"]

with st.sidebar:
    st.header("Scan settings")
    symbols_text = st.text_area("NSE symbols (comma-separated)", ", ".join(default_symbols), height=150)
    min_score = st.slider("Minimum score", 0, 100, 60, 5)
    period = st.selectbox("History", ["1y", "2y", "5y"], index=0)
    run = st.button("Run scan", type="primary", use_container_width=True)

if run:
    symbols = list(dict.fromkeys(x.strip().upper().replace(".NS", "") for x in symbols_text.split(",") if x.strip()))
    with st.spinner(f"Scanning {len(symbols)} symbols..."):
        results, errors = scan_symbols(symbols, lambda s: fetch_with_fallback(s, period=period), min_score=min_score)
    st.session_state["results"] = results
    st.session_state["errors"] = errors

if "results" in st.session_state:
    df = st.session_state["results"]
    if df.empty:
        st.warning("No symbols met the configured minimum score. Try lowering the threshold or checking data-provider errors.")
    else:
        c1, c2, c3 = st.columns(3)
        c1.metric("Candidates", len(df))
        c2.metric("Shortlisted", int(df.Shortlist.sum()))
        c3.metric("Top score", int(df.Score.max()))
        st.dataframe(df, use_container_width=True, hide_index=True)
        st.download_button("Download CSV", df.to_csv(index=False), "nse_swing_candidates.csv", "text/csv")
    errors = st.session_state.get("errors", [])
    if errors:
        with st.expander(f"Provider / symbol errors ({len(errors)})"):
            st.write("\n".join(errors))
else:
    st.info("Configure your universe and select **Run scan**. Start with a small list to respect provider rate limits.")

st.divider()
st.subheader("Signal interpretation")
st.write("Entry is the latest close and should be treated as a reference level, not a live executable quote. Targets are +3% and +5%; stop is 1.5× ATR below the reference close. Recalculate with fresh data before acting.")
