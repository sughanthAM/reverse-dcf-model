markdown


# Reverse DCF Model — NSE Stock Valuation Tool
A Python-based Reverse DCF (Discounted Cash Flow) analyzer that finds the **implied growth rate** the market is pricing into any NSE stock — helping you identify overvalued and undervalued stocks.
## What it does
Normal DCF assumes a growth rate to find stock value.  
**Reverse DCF flips it** — takes the current market price and back-calculates what growth rate the market is silently assuming.
If that implied growth rate is unrealistic → stock is overvalued.  
If the company can easily beat it → stock is undervalued.
## Decision Framework
|
 Implied Growth 
|
 Verdict 
|
 Action 
|
|
---
|
---
|
---
|
|
 Below 8% 
|
 🟢 UNDERVALUED 
|
 Strong Buy 
|
|
 8% – 12% 
|
 🟢 FAIR 
|
 Buy / Hold 
|
|
 12% – 18% 
|
 🟡 EXPENSIVE 
|
 Hold only 
|
|
 18% – 22% 
|
 🔴 OVERVALUED 
|
 Avoid / Book profits 
|
|
 Above 22% 
|
 🔴 STRONG AVOID 
|
 Sell 
|
## Files
|
 File 
|
 Description 
|
|
---
|
---
|
|
`reverse_dcf.py`
|
 Core Python script — fetches data, calculates implied growth, prints verdict 
|
|
`reverse_dcf_app.py`
|
 Streamlit web app — interactive UI with charts and table 
|
## How to Run
**Script:**
```bash
python reverse_dcf.py
Web App:

bash


streamlit run reverse_dcf_app.py
Tech Stack
Python
yfinance — live NSE stock data
scipy — brentq optimization for implied growth calculation
Streamlit — web app UI
Matplotlib — visualization
Installation
bash


pip install yfinance scipy streamlit matplotlib pandas numpy
