import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime
import pytz

# ১. পেজ সেটআপ (মোবাইলে যাতে সুন্দর দেখায়)
st.set_page_config(layout="wide", page_title="Haridas Pro Master")
IST = pytz.timezone('Asia/Kolkata')

# ২. মোবাইল ফ্রেন্ডলি কাস্টম ডিজাইন
st.markdown("""
    <style>
    .main { background-color: #f4f7f6; }
    /* বাটন বড় করা */
    div.stButton > button {
        background: linear-gradient(to right, #007bff, #00c6ff);
        color: white;
        font-weight: bold;
        border-radius: 12px;
        height: 3.5em;
        font-size: 20px !important;
        width: 100%;
        margin-bottom: 20px;
    }
    /* ফন্ট সাইজ বড় করা */
    html, body, [class*="css"] {
        font-size: 18px !important;
    }
    /* ইনডেক্স কার্ড ডিজাইন */
    .idx-card {
        background-color: white;
        padding: 15px;
        border-radius: 15px;
        border: 1px solid #ddd;
        text-align: center;
        margin-bottom: 10px;
        box-shadow: 2px 2px 8px rgba(0,0,0,0.05);
    }
    .idx-name { font-size: 16px; color: #666; }
    .idx-price { font-size: 22px; font-weight: bold; color: #333; }
    /* টেবিলের ফন্ট সাইজ */
    .stDataFrame, .stTable {
        font-size: 16px !important;
    }
    </style>
    """, unsafe_allow_html=True)

# আপনার অরিজিনাল সেক্টর ম্যাপ
SECTOR_MAP = {
    "BANK 🏦": ["HDFCBANK.NS", "ICICIBANK.NS", "SBIN.NS", "KOTAKBANK.NS", "AXISBANK.NS"],
    "IT 💻": ["TCS.NS", "INFY.NS", "HCLTECH.NS", "WIPRO.NS", "TECHM.NS"],
    "AUTO 🚗": ["TATAMOTORS.NS", "MARUTI.NS", "M&M.NS", "BAJAJ-AUTO.NS", "EICHERMOT.NS"],
    "ENERGY ⚡": ["RELIANCE.NS", "NTPC.NS", "POWERGRID.NS", "ONGC.NS"],
    "FMCG 🛒": ["ITC.NS", "HINDUNILVR.NS", "NESTLEIND.NS", "BRITANNIA.NS"]
}

# ৩. বাজেট সাইডবার (মোবাইলে উপরে থাকবে)
st.sidebar.markdown("### 💰 Profit Analysis")
investment = st.sidebar.number_input("বাজেট (টাকা):", value=100000, step=5000)

# ৪. টাইটেল ও ঘড়ি (পরিষ্কার ফন্টে)
st.markdown(f"<h1 style='text-align: center; color: #0a192f; font-size: 28px;'>📊 HARIDAS TERMINAL</h1>", unsafe_allow_html=True)
st.markdown(f"<p style='text-align: center; font-size: 20px;'>🕒 <b>{datetime.now(IST).strftime('%H:%M:%S')}</b></p>", unsafe_allow_html=True)

# ৫. মার্কেট ইনডেক্স (মোবাইলে ২ কলামে সুন্দর দেখাবে)
indices = {"NIFTY 50": "^NSEI", "BANK NIFTY": "^NSEBANK", "SENSEX": "^BSESN", "NIFTY FIN": "NIFTY_FIN_SERVICE.NS"}
idx_cols = st.columns(2)
for i, (name, sym) in enumerate(indices.items()):
    try:
        idat = yf.Ticker(sym).history(period="2d")
        lp = round(idat['Close'].iloc[-1], 2)
        pct = round(((lp - idat['Close'].iloc[-2])/idat['Close'].iloc[-2])*100, 2)
        color = "green" if pct >= 0 else "red"
        idx_cols[i % 2].markdown(f"""
            <div class='idx-card'>
                <div class='idx-name'>{name}</div>
                <div class='idx-price'>{lp}</div>
                <div style='color:{color}; font-weight:bold;'>{pct}%</div>
            </div>
        """, unsafe_allow_html=True)
    except: continue

# ৬. স্ক্যানার বাটন
st.write("---")
if st.button("🔍 SCAN MARKET NOW", use_container_width=True):
    all_res, sec_res, drastic_res = [], [], []
    adv, dec = 0, 0

    with st.spinner('Analysing Market...'):
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
                        trend = "Falling 📉" if is_falling_3d else ("Rising 📈" if (p[-2] > p[-3] >
