import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime
import time

# --- Page Configuration ---
st.set_page_config(
    page_title="Haridas Master Terminal",
    layout="wide", # এটি স্ক্রিন অ্যাডজাস্ট করতে সাহায্য করে
    initial_sidebar_state="collapsed"
)

# --- Responsive CSS ---
st.markdown("""
    <style>
    [data-testid="stMetricValue"] { font-size: 1.5rem !important; }
    .main { background-color: #eaedf2; }
    div.stButton > button { width: 100%; border-radius: 5px; height: 3em; background-color: #007bff; color: white; }
    /* Table font size for mobile */
    .scaled-table { font-size: 0.8rem !important; }
    </style>
    """, unsafe_allow_html=True)

# --- Sector Map ---
SECTOR_MAP = {
    "NIFTY BANK 🏦": ["HDFCBANK.NS", "ICICIBANK.NS", "SBIN.NS", "KOTAKBANK.NS", "AXISBANK.NS"],
    "NIFTY IT 💻": ["TCS.NS", "INFY.NS", "HCLTECH.NS", "WIPRO.NS", "TECHM.NS"],
    "NIFTY AUTO 🚗": ["TATAMOTORS.NS", "MARUTI.NS", "M&M.NS", "BAJAJ-AUTO.NS", "EICHERMOT.NS"],
    "NIFTY METAL ⚙️": ["TATASTEEL.NS", "JSWSTEEL.NS", "HINDALCO.NS", "VEDL.NS"],
    "NIFTY ENERGY ⚡": ["RELIANCE.NS", "NTPC.NS", "POWERGRID.NS", "ONGC.NS"],
    "NIFTY PHARMA 💊": ["SUNPHARMA.NS", "CIPLA.NS", "DRREDDY.NS", "DIVISLAB.NS"],
    "NIFTY FMCG 🛒": ["ITC.NS", "HINDUNILVR.NS", "NESTLEIND.NS", "BRITANNIA.NS"],
    "NIFTY FIN SRV 💹": ["BAJFINANCE.NS", "BAJAJFINSV.NS", "CHOLAFIN.NS"]
}

# --- Header & Clock ---
c1, c2, c3 = st.columns([2, 1, 1])
with c1:
    st.subheader("📟 HARIDAS NSE TERMINAL v38.0")
with c2:
    st.write(f"🕒 **LIVE:** {datetime.now().strftime('%H:%M:%S')}")
with c3:
    if st.button('🔄 REFRESH NOW'):
        st.rerun()

# --- Auto Refresh Script (Every 60 Seconds) ---
st.markdown("""
    <script>
    setTimeout(function(){ window.location.reload(); }, 60000);
    </script>
    """, unsafe_allow_html=True)

# --- Market Indices ---
st.write("### 📊 Market Indices")
indices = {"NIFTY 50": "^NSEI", "BANK NIFTY": "^NSEBANK", "NIFTY IT": "^CNXIT", "SENSEX": "^BSESN", "NIFTY FIN": "NIFTY_FIN_SERVICE.NS"}
idx_cols = st.columns(len(indices))

for i, (name, sym) in enumerate(indices.items()):
    try:
        data = yf.Ticker(sym).history(period="2d")
        ltp = round(data['Close'].iloc[-1], 2)
        prev = data['Close'].iloc[-2]
        chg = round(((ltp - prev) / prev) * 100, 2)
        idx_cols[i].metric(label=name, value=ltp, delta=f"{chg}%")
    except:
        idx_cols[i].error("N/A")

st.divider()

# --- Main Data Fetching ---
all_stocks = []
sector_data = []
advances, declines = 0, 0

with st.spinner('Scanning NSE Stocks...'):
    for sector, stocks in SECTOR_MAP.items():
        sec_chgs = []
        for s in stocks:
            try:
                df = yf.Ticker(s).history(period="7d")
                if len(df) >= 4:
                    prices = df['Close'].values
                    ltp = round(prices[-1], 2)
                    prev = prices[-2]
                    chg = round(((ltp - prev) / prev) * 100, 2)
                    
                    if chg > 0: advances += 1
                    else: declines += 1
                    
                    # 3-Day Trend (Drastic Watch)
                    is_falling = (prices[-2] < prices[-3] < prices[-4])
                    is_rising = (prices[-2] > prices[-3] > prices[-4])
                    trend_status = "Normal"
                    if is_falling: trend_status = "৩ দিন পতন 📉"
                    elif is_rising: trend_status = "৩ দিন উত্থান 📈"
                    
                    # Signal Logic
                    signal = "-"
                    if chg >= 2.0 and not is_falling: signal = "BUY"
                    elif chg <= -2.0 and not is_rising: signal = "SELL"
                    
                    # Target & SL Logic
                    sl, t1, t2, t3 = 0, 0, 0, 0
                    if signal != "-":
                        sl = round(ltp * 0.985, 2) if signal == "BUY" else round(ltp * 1.015, 2)
                        t1 = round(ltp * 1.01, 2) if signal == "BUY" else round(ltp * 0.99, 2)
                        t3 = round(ltp * 1.03, 2) if signal == "BUY" else round(ltp * 0.97, 2)
                    
                    all_stocks.append({
                        "Stock": s, "LTP": ltp, "Chg%": chg, "Signal": signal, 
                        "SL": sl, "T1": t1, "T3": t3, "Trend": trend_status, "Time": datetime.now().strftime("%H:%M")
                    })
                    sec_chgs.append(chg)
            except: continue
        
        if sec_chgs:
            avg = round(sum(sec_chgs)/len(sec_chgs), 2)
            sector_data.append({"Sector": sector, "Avg%": avg})

# --- UI Layout ---
m1, m2 = st.columns([1, 1])
m1.success(f"📈 ADVANCES: {advances}")
m2.error(f"📉 DECLINES: {declines}")

st.write("### 💹 Trading Signals (Pankaj Strategy)")
sig_df = pd.DataFrame(all_stocks)

def color_signal(val):
    if val == "BUY": return 'background-color: #d4edda; color: #155724'
    if val == "SELL": return 'background-color: #f8d7da; color: #721c24'
    return ''

if not sig_df.empty:
    st.dataframe(sig_df.style.applymap(color_signal, subset=['Signal']), use_container_width=True, hide_index=True)

# --- Side by Side Sections ---
st.divider()
col_left, col_right = st.columns(2)

with col_left:
    st.write("### 🏢 Sector Performance")
    sec_df = pd.DataFrame(sector_data).sort_values(by="Avg%", ascending=False)
    st.table(sec_df)

with col_right:
    st.write("### ⚠️ Drastic Watch (3-Day Trend)")
    drastic = sig_df[sig_df["Trend"] != "Normal"][["Stock", "Trend"]]
    st.table(drastic)

# --- Export Section ---
st.write("### 📂 Export Data")
if not sig_df.empty:
    csv = sig_df.to_csv(index=False).encode('utf-8')
    st.download_button(label="DOWNLOAD EXCEL (CSV)", data=csv, file_name=f"Trade_{datetime.now().strftime('%d%m_%H%M')}.csv", mime="text/csv")
