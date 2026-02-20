import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime
import pytz

# ১. পেজ সেটআপ
st.set_page_config(layout="wide", page_title="Haridas Pro Master Terminal v38.0")

# ইন্ডিয়ান টাইম জোন
IST = pytz.timezone('Asia/Kolkata')

# কাস্টম স্টাইল
st.markdown("""
    <style>
    .main { background-color: #eaedf2; }
    .stButton>button { background-color: #007bff; color: white; font-weight: bold; width: 100%; border-radius: 5px; height: 3em; }
    .metric-card { background-color: #ffffff; padding: 10px; border-radius: 10px; border: 1px solid #d1d9e6; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

# ২. সেক্টর ম্যাপ
SECTOR_MAP = {
    "NIFTY BANK 🏦": ["HDFCBANK.NS", "ICICIBANK.NS", "SBIN.NS", "KOTAKBANK.NS", "AXISBANK.NS"],
    "NIFTY IT 💻": ["TCS.NS", "INFY.NS", "HCLTECH.NS", "WIPRO.NS", "TECHM.NS"],
    "NIFTY AUTO 🚗": ["TATAMOTORS.NS", "MARUTI.NS", "M&M.NS", "BAJAJ-AUTO.NS", "EICHERMOT.NS"],
    "NIFTY ENERGY ⚡": ["RELIANCE.NS", "NTPC.NS", "POWERGRID.NS", "ONGC.NS"],
    "NIFTY FMCG 🛒": ["ITC.NS", "HINDUNILVR.NS", "NESTLEIND.NS", "BRITANNIA.NS"],
    "NIFTY FIN SRV 💹": ["BAJFINANCE.NS", "BAJAJFINSV.NS", "CHOLAFIN.NS"]
}

# ৩. হেডার
t1, t2 = st.columns([3, 1])
with t1:
    st.markdown("<h2 style='color: #0a192f;'>📡 HARIDAS NSE TERMINAL</h2>", unsafe_allow_html=True)
with t2:
    st.markdown(f"🕒 **LIVE: {datetime.now(IST).strftime('%H:%M:%S')}**")

# ৪. মার্কেট ইনডেক্স
st.write("---")
idx_cols = st.columns(5)
broad_indices = {"SENSEX": "^BSESN", "NIFTY 50": "^NSEI", "NIFTY BANK": "^NSEBANK", "NIFTY IT": "^CNXIT", "NIFTY FIN": "NIFTY_FIN_SERVICE.NS"}

for i, (name, sym) in enumerate(broad_indices.items()):
    try:
        df_idx = yf.Ticker(sym).history(period="2d")
        if not df_idx.empty:
            ltp = round(df_idx['Close'].iloc[-1], 2)
            prev = df_idx['Close'].iloc[-2]
            chg = round(ltp - prev, 2)
            pct = round((chg/prev)*100, 2)
            color = "green" if chg > 0 else "red"
            idx_cols[i].markdown(f"""<div class='metric-card'><b>{name}</b><br>{ltp}<br><span style='color:{color};'>{chg} ({pct}%)</span></div>""", unsafe_allow_html=True)
    except: continue

# ৫. স্ক্যান বাটন
st.write("---")
if st.button("🔍 SCAN MARKET NOW (ALL SECTORS)", use_container_width=True):
    all_stocks = []
    sector_results = []
    advances, declines = 0, 0

    with st.spinner('বিশ্লেষণ চলছে...'):
        for sector, stocks in SECTOR_MAP.items():
            sector_changes = []
            for stock in stocks:
                try:
                    df = yf.Ticker(stock).history(period="7d")
                    if len(df) >= 4:
                        prices = df['Close'].values
                        ltp = round(float(prices[-1]), 2)
                        prev_close = float(prices[-2])
                        change = round(((ltp - prev_close) / prev_close) * 100, 2)
                        
                        drastic = "-"
                        if prices[-2] < prices[-3] < prices[-4]: drastic = "৩ দিন পতন 📉"
                        elif prices[-2] > prices[-3] > prices[-4]: drastic = "৩ দিন উত্থান 📈"
                        
                        signal = "WAIT"
                        if change >= 2.0 and "পতন" not in drastic: signal = "🟢 BUY"
                        elif change <= -2.0 and "উত্থান" not in drastic: signal = "🔴 SELL"
                        
                        all_stocks.append({
                            "Stock": stock.replace(".NS",""), "LTP": ltp, "Chg%": change,
                            "Action": signal, "SL": round(ltp*0.985 if "BUY" in signal else ltp*1.015, 2),
                            "T1": round(ltp*1.01 if "BUY" in signal else ltp*0.99, 2),
                            "3D-Trend": drastic
                        })
                        sector_changes.append(change)
                        if change > 0: advances += 1
                        else: declines += 1
                except: continue
            
            if sector_changes:
                avg = round(sum(sector_changes)/len(sector_changes), 2)
                sector_results.append({"Sector": sector, "Avg%": avg})

    # ৬. ডিসপ্লে লেআউট
    st.write(f"✅ **Advances: {advances} | Declines: {declines}**")
    
    col_left, col_mid, col_right = st.columns([1, 2, 1])

    with col_left:
        st.subheader("🏢 Sectors")
        if sector_results:
            st.table(pd.DataFrame(sector_results).sort_values(by="Avg%", ascending=False))

    with col_mid:
        st.subheader("🎯 Trading Signals")
        if all_stocks:
            st.dataframe(pd.DataFrame(all_stocks), use_container_width=True, hide_index=True)

    with col_right:
        st.subheader("🔥 Top Gain/Loss")
        if all_stocks:
            df_all = pd.DataFrame(all_stocks)
            st.markdown("**GAINERS**")
            st.table(df_all.sort_values(by="Chg%", ascending=False)[['Stock', 'Chg%']].head(5))
            st.markdown("**LOSERS**")
            st.table(df_all.sort_values(by="Chg%", ascending=True)[['Stock', 'Chg%']].head(5))
            
            st.subheader("⚠️ Drastic Watch")
            st.table(df_all[df_all['3D-Trend'] != "-"][['Stock', '3D-Trend']])

st.markdown("---")
st.caption("হরিদাস ভাই, এই স্ক্যানারটি এখন আপনার মোবাইলের জন্য একদম রেডি।")
