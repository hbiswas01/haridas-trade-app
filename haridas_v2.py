import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime
import pytz

# ১. পেজ সেটআপ (Wide Layout - Responsive)
st.set_page_config(layout="wide", page_title="Haridas Pro Master Terminal v38.0")

IST = pytz.timezone('Asia/Kolkata')

# কাস্টম ডিজাইন (Tkinter লুকের মতো পরিষ্কার ডিজাইন)
st.markdown("""
    <style>
    .main { background-color: #eaedf2; }
    header {visibility: hidden;}
    .stButton>button { background: linear-gradient(to right, #007bff, #00c6ff); color: white; font-weight: bold; width: 100%; border-radius: 8px; height: 3.5em; font-size: 18px; }
    .idx-card { background-color: #f8f9fc; padding: 12px; border-radius: 10px; border: 1px solid #e3e6f0; text-align: center; box-shadow: 2px 2px 5px rgba(0,0,0,0.05); }
    .stat-header { background-color: #4e73df; color: white; padding: 5px; border-radius: 5px; text-align: center; font-weight: bold; margin-bottom: 5px; }
    </style>
    """, unsafe_allow_html=True)

# ২. সেক্টর ম্যাপ (আপনার অরিজিনাল লিস্ট)
SECTOR_MAP = {
    "NIFTY BANK 🏦": ["HDFCBANK.NS", "ICICIBANK.NS", "SBIN.NS", "KOTAKBANK.NS", "AXISBANK.NS"],
    "NIFTY IT 💻": ["TCS.NS", "INFY.NS", "HCLTECH.NS", "WIPRO.NS", "TECHM.NS"],
    "NIFTY AUTO 🚗": ["TATAMOTORS.NS", "MARUTI.NS", "M&M.NS", "BAJAJ-AUTO.NS", "EICHERMOT.NS"],
    "NIFTY METAL ⚙️": ["TATASTEEL.NS", "JSWSTEEL.NS", "HINDALCO.NS", "VEDL.NS"],
    "NIFTY ENERGY ⚡": ["RELIANCE.NS", "NTPC.NS", "POWERGRID.NS", "ONGC.NS"],
    "NIFTY PHARMA 💊": ["SUNPHARMA.NS", "CIPLA.NS", "DRREDDY.NS", "DIVISLAB.NS"],
    "NIFTY FMCG 🛒": ["ITC.NS", "HINDUNILVR.NS", "NESTLEIND.NS", "BRITANNIA.NS"],
    "NIFTY INFRA 🏗️": ["LT.NS", "ADANIPORTS.NS", "GRASIM.NS", "AMBUJACEM.NS"],
    "NIFTY REALTY 🏢": ["DLF.NS", "GODREJPROP.NS", "OBEROIRLTY.NS", "PRESTIGE.NS"],
    "NIFTY FIN SRV 💹": ["BAJFINANCE.NS", "BAJAJFINSV.NS", "CHOLAFIN.NS"]
}

# ৩. টপ বার (টাইটেল, অ্যাডভান্স/ডিক্লাইন, লাইভ ঘড়ি)
top_col1, top_col2, top_col3, top_col4 = st.columns([2, 1, 1, 1])
with top_col1:
    st.markdown("<h2 style='color: #0a192f; margin:0;'>📡 HARIDAS NSE TERMINAL</h2>", unsafe_allow_html=True)
with top_col2:
    st.markdown(f"🕒 **LIVE: {datetime.now(IST).strftime('%H:%M:%S')}**")

adv_spot = top_col3.empty()
dec_spot = top_col4.empty()

# ৪. মার্কেট ইনডেক্স কার্ডস
st.write("---")
indices = {"SENSEX": "^BSESN", "NIFTY 50": "^NSEI", "NIFTY BANK": "^NSEBANK", "NIFTY IT": "^CNXIT", "NIFTY FIN": "NIFTY_FIN_SERVICE.NS"}
idx_cols = st.columns(len(indices))

for i, (name, sym) in enumerate(indices.items()):
    try:
        idat = yf.Ticker(sym).history(period="2d")
        lp = round(idat['Close'].iloc[-1], 2)
        pct = round(((lp - idat['Close'].iloc[-2])/idat['Close'].iloc[-2])*100, 2)
        color = "#28a745" if pct >= 0 else "#dc3545"
        idx_cols[i].markdown(f"<div class='idx-card'><small>{name}</small><br><b>{lp}</b><br><span style='color:{color};'>{pct}%</span></div>", unsafe_allow_html=True)
    except: continue

# ৫. মেইন স্ক্যানার বাটন
st.write("---")
if st.button("🔍 SCAN MARKET NOW", use_container_width=True):
    all_res, sec_res, drastic_res = [], [], []
    adv, dec = 0, 0

    with st.spinner('Analysing Market Data...'):
        for sector, stocks in SECTOR_MAP.items():
            s_chgs = []
            for s in stocks:
                try:
                    df = yf.Ticker(s).history(period="7d")
                    if len(df) >= 4:
                        p = df['Close'].values
                        ltp, prev_c = round(p[-1], 2), p[-2]
                        chg = round(((ltp - prev_c) / prev_c) * 100, 2)
                        
                        # ৩ দিন ট্রেন্ড (Drastic Watch)
                        trend = "-"
                        if p[-2] < p[-3] < p[-4]: trend = "Falling 📉"
                        elif p[-2] > p[-3] > p[-4]: trend = "Rising 📈"
                        if trend != "-": drastic_res.append({"Stock": s.replace(".NS",""), "Status": trend})

                        # সিগন্যাল লজিক (পঙ্কজ ২% স্ট্র্যাটেজি)
                        sig = "-"
                        if chg >= 2.0 and "Falling" not in trend: sig = "🟢 BUY"
                        elif chg <= -2.0 and "Rising" not in trend: sig = "🔴 SELL"
                        
                        all_res.append({
                            "Stock": s.replace(".NS",""), "LTP": ltp, "Chg%": chg, "Signal": sig,
                            "SL": round(ltp*0.985 if "BUY" in sig else ltp*1.015, 2),
                            "T1": round(ltp*1.01 if "BUY" in sig else ltp*0.99, 2),
                            "T2": round(ltp*1.02 if "BUY" in sig else ltp*0.98, 2),
                            "Time": datetime.now(IST).strftime('%H:%M:%S')
                        })
                        if chg > 0: adv += 1
                        else: dec += 1
                        s_chgs.append(chg)
                except: continue
            if s_chgs:
                sec_res.append({"Sector": sector, "Avg%": round(sum(s_chgs)/len(s_chgs), 2)})

    # ডাটা আপডেট
    adv_spot.markdown(f"🟢 **ADVANCES: {adv}**")
    dec_spot.markdown(f"🔴 **DECLINES: {dec}**")

    # ৬. রেসপনসিভ লেআউট (Auto-Adaptive)
    col_left, col_mid, col_right = st.columns([1, 2, 1])

    with col_left:
        st.markdown("<div class='stat-header'>🏢 SECTOR PERFORMANCE</div>", unsafe_allow_html=True)
        st.dataframe(pd.DataFrame(sec_res).sort_values("Avg%", ascending=False), hide_index=True, use_container_width=True)

    with col_mid:
        st.markdown("<div class='stat-header'>🎯 TRADING SIGNALS</div>", unsafe_allow_html=True)
        # শুধু সিগন্যাল থাকলে হাইলাইট করে দেখাবে
        st.dataframe(pd.DataFrame(all_res), use_container_width=True, hide_index=True
