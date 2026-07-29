import yfinance as yf
import numpy as np
import pandas as pd
from scipy.optimize import brentq

tickers = ["HAL.NS", "BEL.NS", "ICICIBANK.NS", "MAZDOCK.NS", "TATASTEEL.NS"]

def get_stock_data(ticker):
    stock = yf.Ticker(ticker)
    info = stock.info
    return {
        "ticker": ticker,
        "price": info.get("currentPrice", None),
        "eps": info.get("trailingEps", None),
        "revenue": info.get("totalRevenue", None),
        "market_cap": info.get("marketCap", None)
    }

def reverse_dcf(current_price, eps, discount_rate=0.12, terminal_growth=0.04, years=10):
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
        implied_growth = brentq(dcf_value, -0.5, 5.0)
        return round(implied_growth * 100, 2)
    except:
        return None

print("="*60)
print("REVERSE DCF — IMPLIED GROWTH RATES")
print("="*60)

results = []
for ticker in tickers:
    d = get_stock_data(ticker)
    if d["price"] and d["eps"] and d["eps"] > 0:
        implied = reverse_dcf(d["price"], d["eps"])
        results.append({
            "Stock": ticker.replace(".NS", ""),
            "Price": d["price"],
            "EPS": d["eps"],
            "PE Ratio": round(d["price"] / d["eps"], 1),
            "Implied Growth %": implied
        })
        print(f"{ticker.replace('.NS',''):>12} | ₹{d['price']:>8.0f} | EPS: {d['eps']:>7.1f} | PE: {d['price']/d['eps']:>5.1f} | Implied Growth: {implied}%")
    else:
        print(f"{ticker.replace('.NS',''):>12} | Data missing — skipped")

df = pd.DataFrame(results)
df.to_csv("d:/reverse_dcf_results.csv", index=False)
print("\nSaved to d:/reverse_dcf_results.csv")
print("\n" + "="*60)
print("VERDICT — Is the market realistic?")
print("="*60)

for r in results:
    g = r["Implied Growth %"]
    stock = r["Stock"]
    if g is None:
        verdict = "❓ Can't calculate"
    elif g > 20:
        verdict = "🔴 OVERVALUED — market expects unrealistic growth"
    elif g > 15:
        verdict = "🟡 EXPENSIVE — priced for high growth, risky"
    elif g > 10:
        verdict = "🟢 FAIR — reasonable growth expectation"
    else:
        verdict = "🟢 UNDERVALUED — market expects very little"
    print(f"{stock:>12} | Implied: {g}% | {verdict}")