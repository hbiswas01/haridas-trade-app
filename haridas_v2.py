import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime
import time

# --- Page Config ---
st.set_page_config(page_title="Haridas Pro Terminal", layout="wide")

# --- CSS for Styling (Desktop Look) ---
st.markdown("""
    <style>
    .main { background-color: #eaedf2; }
    .stMetric { background-color: #ffffff; padding: 10px; border-radius: 5px; border: 1px solid #e3e6f0; }
    .buy-signal { color: #155724; background-color: #d4edda; font-weight: bold; padding: 5px; }
    .sell-signal { color: #721c24; background-color: #f8d7da; font-weight: bold; padding: 5px; }
    </style>
    """, unsafe_allow_html=True)

# --- Sector Map ---
SECTOR_MAP = {
    "BANK 🏦": ["HDFCBANK.NS", "ICICIBANK.NS", "SBIN.NS", "KOTAKBANK.NS", "AXISBANK.NS"],
    "IT 💻": ["TCS.NS", "INFY.NS", "HCLTECH.NS", "WIPRO.NS", "TECHM.NS"],
    "AUTO 🚗": ["TATAMOTORS.NS", "MARUTI.NS", "M&M.NS", "BAJAJ-AUTO.NS", "EICHERMOT.NS"],
    "METAL ⚙️": ["TATASTEEL.NS", "JSWSTEEL.NS", "HINDALCO.NS", "VEDL.NS"],
    "ENERGY ⚡": ["RELIANCE.NS", "NTPC.NS", "POWERGRID.NS", "ONGC.NS"],
    "PHARMA 💊": ["SUNPHARMA.NS", "CIPLA.NS", "DRREDDY.NS", "DIVISLAB.NS"],
    "FMCG 🛒": ["ITC.NS", "HINDUNILVR.NS", "NESTLEIND.NS", "BRITANNIA.NS"],
    "FIN SRV 💹": ["BAJFINANCE.NS", "BAJAJFINSV.NS", "CHOLAFIN.NS"]
}

# --- Header Section ---
t1, t2 = st.columns([3, 1])
with t1:
    st.title("📟 HARIDAS NSE TERMINAL v2")
with t2:
    st.write(f"**Last Sync:** {datetime.now().strftime('%H:%M:%S')}")
    if st.button('🔄 Force Refresh'):
        st.rerun()

# --- Auto Refresh Logic (Every 120 Seconds) ---
# Streamlit-এ সরাসরি লুপ চালানো যায় না, তাই টাইমার ব্যবহার করছি
# st.empty() দিয়ে কন্টেইনার আপডেট করা হয়

# --- Market Indices ---
indices = {"NIFTY 50": "^NSEI", "BANK NIFTY": "^NSEBANK", "NIFTY IT": "^CNXIT", "SENSEX": "^BSESN"}
cols = st.columns(len(indices))

for i, (name, sym) in enumerate(indices.items()):
    try:
        data = yf.Ticker(sym).history(period="2d")
        ltp = round(data['Close'].iloc[-1], 2)
        prev = data['Close'].iloc[-2]
        chg = round(((ltp - prev) / prev) * 100, 2)
        cols[i].metric(name, f"₹{ltp}", f"{chg}%")
    except:
        cols[i].error(f"Error {name}")

st.divider()

# --- Main Logic ---
all_stocks = []
sector_summary = []

with st.spinner('Fetching Live Data...'):
    for sector, stocks in SECTOR_MAP.items():
        sec_chgs = []
        for s in stocks:
            try:
                df = yf.Ticker(s).history(period="7d")
                if len(df) >= 4:
                    prices = df['Close'].values
                    ltp = round(prices[-1], 2)
                    prev_close = prices[-2]
                    change = round(((ltp - prev_close) / prev_close) * 100, 2)
                    
                    # 3-Day Trend (v2 Logic)
                    is_falling_3d = (prices[-2] < prices[-3] < prices[-4])
                    is_rising_3d = (prices[-2] > prices[-3] > prices[-4])
                    
                    trend = "Normal"
                    if is_falling_3d: trend = "৩ দিন পতন 📉"
                    elif is_rising_3d: trend = "৩ দিন উত্থান 📈"
                    
                    signal = "-"
                    if change >= 2.0 and not is_falling_3d: signal = "BUY"
                    elif change <= -2.0 and not is_rising_3d: signal = "SELL"
                    
                    all_stocks.append({
                        "Stock": s, "Sector": sector, "LTP": ltp, 
                        "Change%": change, "Trend": trend, "Signal": signal
                    })
                    sec_chgs.append(change)
            except: continue
        
        if sec_chgs:
            avg_chg = round(sum(sec_chgs)/len(sec_chgs), 2)
            sector_summary.append({"Sector": sector, "Avg Chg%": avg_chg})

# --- Display Section ---
c1, c2 = st.columns([1, 2])

with c1:
    st.subheader("🏢 Sector Performance")
    sec_df = pd.DataFrame(sector_summary).sort_values(by="Avg Chg%", ascending=False)
    st.dataframe(sec_df, use_container_width=True, hide_index=True)

with c2:
    st.subheader("💹 Trading Signals (Pankaj Strategy)")
    full_df = pd.DataFrame(all_stocks)
    
    # Highlight signals
    def highlight_signal(val):
        if val == "BUY": return 'background-color: #d4edda; color: #155724; font-weight: bold'
        if val == "SELL": return 'background-color: #f8d7da; color: #721c24; font-weight: bold'
        return ''

    if not full_df.empty:
        styled_df = full_df.style.applymap(highlight_signal, subset=['Signal'])
        st.dataframe(styled_df, use_container_width=True, hide_index=True)

# --- Drastic Watch & Gainers ---
st.divider()
st.subheader("⚠️ Drastic Watch & Top Moves")
k1, k2, k3 = st.columns(3)

if not full_df.empty:
    k1.write("**Top Gainers**")
    k1.dataframe(full_df.sort_values(by="Change%", ascending=False).head(5)[["Stock", "Change%"]], hide_index=True)
    
    k2.write("**Top Losers**")
    k2.dataframe(full_df.sort_values(by="Change%").head(5)[["Stock", "Change%"]], hide_index=True)
    
    k3.write("**3-Day Trend Alert**")
    k3.dataframe(full_df[full_df["Trend"] != "Normal"][["Stock", "Trend"]], hide_index=True)

# --- Auto-Refresh JavaScript ---
# এটি পেজটিকে প্রতি ১২০ সেকেন্ডে রিলোড করবে
st.markdown("""
    <script>
    setTimeout(function(){
       window.location.reload();
    }, 120000);
    </script>
    """, unsafe_allow_html=True)
