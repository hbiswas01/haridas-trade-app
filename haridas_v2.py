import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime
import pytz

# ১. পেজ সেটআপ (মোবাইলে ফিট হওয়ার জন্য)
st.set_page_config(layout="wide", page_title="Haridas Pro Master")
IST = pytz.timezone('Asia/Kolkata')

# ২. মোবাইল ফ্রেন্ডলি কাস্টম ডিজাইন
st.markdown("""
    <style>
    .main { background-color: #f4f7f6; }
    div.stButton > button {
        background: linear-gradient(to right, #007bff, #00c6ff);
        color: white; font-weight: bold; border-radius: 12px;
        height: 3.5em; font-size: 20px !important; width: 100%;
    }
    html, body, [class*="css"] { font-size: 18px !important; }
    .idx-card {
        background-color: white; padding: 15px; border-radius: 15px;
        border: 1px solid #ddd; text-align: center; margin-bottom: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# আপনার অরিজিনাল সেক্টর ম্যাপ
SECTOR_MAP = {
    "BANK 🏦": ["HDFCBANK.NS", "ICICIBANK.NS", "SBIN.NS", "KOTAKBANK.NS", "AXISBANK.NS"],
    "IT 💻": ["TCS.NS", "INFY.NS", "HCLTECH.NS", "WIPRO.NS", "TECHM.NS"],
    "AUTO 🚗": ["TATAMOTORS.NS", "MARUTI.NS", "M&M.NS", "BAJAJ-AUTO.NS", "EICHERMOT.NS"],
    "ENERGY ⚡": ["RELIANCE.NS", "NTPC.NS", "POWERGRID.NS", "ONGC.NS"],
    "FIN 💹": ["BAJFINANCE.NS", "BAJAJFINSV.NS", "CHOLAFIN.NS"]
}

# ৩. বাজেট ইনপুট
st.sidebar.markdown("### 💰 Profit Analysis")
investment = st.sidebar.number_input("বাজেট (টাকা):", value=100000, step=5000)

# ৪. টাইটেল
st.markdown(f"<h1 style='text-align: center; color: #0a192f;'>📊 HARIDAS TERMINAL</h1>", unsafe_allow_html=True)
st.markdown(f"<p style='text-align: center;'>🕒 <b>{datetime.now(IST).strftime('%H:%M:%S')}</b></p>", unsafe_allow_html=True)

# ৫. মার্কেট ইনডেক্স
indices = {"NIFTY 50": "^NSEI", "BANK NIFTY": "^NSEBANK", "SENSEX": "^BSESN", "NIFTY IT": "^CNXIT"}
idx_cols = st.columns(2)
for i, (name, sym) in enumerate(indices.items()):
    try:
        idat = yf.Ticker(sym).history(period="2d")
        lp = round(idat['Close'].iloc[-1], 2)
        pct = round(((lp - idat['Close'].iloc[-2])/idat['Close'].iloc[-2])*100, 2)
        color = "green" if pct >= 0 else "red"
        idx_cols[i % 2].markdown(f"<div class='idx-card'><b>{name}</b><br>{lp}<br><span style='color:{color};'>{pct}%</span></div>", unsafe_allow_html=True)
    except: continue

# ৬. স্ক্যানার বাটন
st.write("---")
if st.button("🔍 SCAN MARKET NOW", use_container_width=True):
    all_res, sec_res = [], []
    adv, dec = 0, 0
    with st.spinner('Analysing...'):
        for sector, stocks in SECTOR_MAP.items():
            s_chgs = []
            for s in stocks:
                try:
                    df = yf.Ticker(s).history(period="7d")
                    if len(df) >= 4:
                        p = df['Close'].values
                        ltp, prev_c = round(p[-1], 2), p[-2]
                        chg = round(((ltp - prev_c) / prev_c) * 100, 2)
                        is_falling_3d = (p[-2] < p[-3] < p[-4])
                        sig = "🟢 BUY" if (chg >= 2.0 and not is_falling_3d) else ("🔴 SELL" if (chg <= -2.0) else "-")
                        qty = int(investment / ltp)
                        pl_amt = round((ltp - prev_c) * qty, 2)
                        all_res.append({"Stock": s.replace(".NS",""), "Price": ltp, "Change%": f"{chg}%", "Signal": sig, "P/L": f"₹{pl_amt}"})
                        if chg > 0: adv += 1
                        else: dec += 1
                        s_chgs.append(chg)
                except: continue
            if s_chgs: sec_res.append({"Sector": sector, "Avg%": f"{round(sum(s_chgs)/len(s_chgs), 2)}%"})
    
    st.success(f"🟢 Adv: {adv} | 🔴 Dec: {dec}")
    st.subheader("🎯 Signals & Amount")
    st.dataframe(pd.DataFrame(all_res), use_container_width=True, hide_index=True)
    st.subheader("🏢 Sectors")
    st.table(pd.DataFrame(sec_res))
