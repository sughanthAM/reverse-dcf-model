import streamlit as st
import yfinance as yf
import numpy as np
import pandas as pd
from scipy.optimize import brentq
import matplotlib.pyplot as plt

st.set_page_config(page_title="Reverse DCF Analyzer", layout="wide")
st.title("Reverse DCF — Implied Growth Rate Analyzer")
st.markdown("Find out what growth rate the market is already pricing into any NSE stock")

st.sidebar.header("Settings")
tickers_input = st.sidebar.text_input("Enter NSE Tickers (comma separated)", value="HAL.NS, BEL.NS, ICICIBANK.NS, MAZDOCK.NS, TATASTEEL.NS")
discount_rate = st.sidebar.slider("Discount Rate (%)", 8, 18, 12) / 100
terminal_growth = st.sidebar.slider("Terminal Growth Rate (%)", 2, 6, 4) / 100
years = st.sidebar.slider("Projection Years", 5, 15, 10)
run = st.sidebar.button("Analyze")

def get_stock_data(ticker):
    stock = yf.Ticker(ticker)
    info = stock.info
    return {
        "ticker": ticker,
        "price": info.get("currentPrice", None),
        "eps": info.get("trailingEps", None),
        "pe": info.get("trailingPE", None),
        "revenue": info.get("totalRevenue", None),
        "market_cap": info.get("marketCap", None)
    }

def reverse_dcf(current_price, eps, discount_rate, terminal_growth, years):
    def dcf_value(growth_rate):
        value = 0
        for t in range(1, years + 1):
            projected_eps = eps * (1 + growth_rate) ** t
            value += projected_eps / (1 + discount_rate) ** t
        terminal_eps = eps * (1 + growth_rate) ** years
        terminal_value = (terminal_eps * (1 + terminal_growth)) / (discount_rate - terminal_growth)
        value += terminal_value / (1 + discount_rate) ** years
        return value - current_price
    try:
        return round(brentq(dcf_value, -0.5, 5.0) * 100, 2)
    except:
        return None

if run:
    tickers = [t.strip().upper() for t in tickers_input.split(",")]
    st.info(f"Fetching data for {len(tickers)} stocks...")
    
    results = []
    for ticker in tickers:
        d = get_stock_data(ticker)
        if d["price"] and d["eps"] and d["eps"] > 0:
            implied = reverse_dcf(d["price"], d["eps"], discount_rate, terminal_growth, years)
            if implied is not None:
                if implied > 20:
                    verdict = "🔴 OVERVALUED"
                elif implied > 15:
                    verdict = "🟡 EXPENSIVE"
                elif implied > 10:
                    verdict = "🟢 FAIR"
                else:
                    verdict = "🟢 UNDERVALUED"
                results.append({
                    "Stock": ticker.replace(".NS", ""),
                    "Price (₹)": d["price"],
                    "EPS (₹)": d["eps"],
                    "PE Ratio": round(d["price"] / d["eps"], 1),
                    "Implied Growth %": implied,
                    "Verdict": verdict
                })

    if results:
        st.subheader("Results")
        cols = st.columns(len(results))
        for idx, r in enumerate(results):
            with cols[idx]:
                st.metric(r["Stock"], f"₹{r['Price (₹)']:.0f}", f"PE: {r['PE Ratio']}")
                if "OVERVALUED" in r["Verdict"]:
                    st.error(f"{r['Implied Growth %']}% — {r['Verdict']}")
                elif "EXPENSIVE" in r["Verdict"]:
                    st.warning(f"{r['Implied Growth %']}% — {r['Verdict']}")
                else:
                    st.success(f"{r['Implied Growth %']}% — {r['Verdict']}")

        st.subheader("Implied Growth Comparison")
        df = pd.DataFrame(results)
        
        stocks = df["Stock"].tolist()
        growths = df["Implied Growth %"].tolist()
        colors = ["#ff4444" if g > 20 else "#ffaa00" if g > 15 else "#00cc66" for g in growths]

        fig, ax = plt.subplots(figsize=(10, 5))
        fig.patch.set_facecolor("#0d1117")
        ax.set_facecolor("#0d1117")
        bars = ax.barh(stocks, growths, color=colors, edgecolor="white", linewidth=0.5)
        ax.axvline(x=discount_rate * 100, color="white", linestyle="--", linewidth=1, label=f"Discount Rate ({discount_rate*100:.0f}%)")
        for bar, g in zip(bars, growths):
            ax.text(bar.get_width() + 0.3, bar.get_y() + bar.get_height()/2, f"{g}%", va="center", color="white", fontweight="bold")
        ax.set_xlabel("Implied Growth Rate (%)", color="white")
        ax.set_title("What Growth Rate is the Market Pricing In?", color="white", fontsize=14, fontweight="bold")
        ax.tick_params(colors="white")
        ax.legend(facecolor="#0d1117", labelcolor="white")
        ax.grid(axis="x", alpha=0.2)
        plt.tight_layout()
        st.pyplot(fig)

        st.subheader("Full Data Table")
        st.dataframe(df, use_container_width=True)
    else:
        st.error("No valid data found for any ticker.")