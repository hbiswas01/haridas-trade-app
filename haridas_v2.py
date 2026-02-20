import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime
import pytz

# ১. পেজ সেটআপ
st.set_page_config(layout="wide", page_title="Haridas Pro Master Terminal v38.0")
IST = pytz.timezone('Asia/Kolkata')

# ২. কাস্টম ডিজাইন
st.markdown("""
    <style>
    .main { background-color: #eaedf2; }
    .stButton>button { background: linear-gradient(to right, #007bff, #00c6ff); color: white; font-weight: bold; width: 100%; border-radius: 8px; height: 3.5em; font-size: 18px; }
    .idx-card { background-color: #f8f9fc; padding: 12px; border-radius: 10px; border: 1px solid #e3e6f0; text-align: center; box-shadow: 2px 2px 5px rgba(0,0,0,0.05); }
    </style>
    """, unsafe_allow_html=True)

# আপনার অরিজিনাল সেক্টর লিস্ট
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

# ৩. বাজেট ইনপুট (অ্যামাউন্ট দেখার জন্য)
st.sidebar.markdown("### 💰 Profit Analysis")
investment = st.sidebar.number_input("বাজেট (টাকা):", value=100000, step=5000)

# ৪. টপ বার
st.markdown(f"<h2 style='text-align: center; color: #0a192f;'>📡 HARIDAS MASTER SCANNER</h2>", unsafe_allow_html=True)
st.markdown(f"<p style='text-align: center; font-weight: bold;'>🕒 LIVE: {datetime.now(IST).strftime('%H:%M:%S')}</p>", unsafe_allow_html=True)

# ৫. ইনডেক্স
indices = {"SENSEX": "^BSESN", "NIFTY 50": "^NSEI", "NIFTY BANK": "^NSEBANK", "NIFTY IT": "^CNXIT", "NIFTY FIN": "NIFTY_FIN_SERVICE.NS"}
idx_cols = st.columns(5)
for i, (name, sym) in enumerate(indices.items()):
    try:
        idat = yf.Ticker(sym).history(period="2d")
        lp = round(idat['Close'].iloc[-1], 2)
        pct = round(((lp - idat['Close'].iloc[-2])/idat['Close'].iloc[-2])*100, 2)
        idx_cols[i].markdown(f"<div class='idx-card'><b>{name}</b><br>{lp}<br><span style='color:{'green' if pct>=0 else 'red'};'>{pct}%</span></div>", unsafe_allow_html=True)
    except: continue

# ৬. স্ক্যানার বাটন
st.write("---")
if st.button("🔍 SCAN MARKET (Pankaj Strategy)", use_container_width=True):
    all_res, sec_res, drastic_res = [], [], []
    adv, dec = 0, 0

    with st.spinner('বাজার বিশ্লেষণ চলছে...'):
        for sector, stocks in SECTOR_MAP.items():
            s_chgs = []
            for s in stocks:
                try:
                    df = yf.Ticker(s).history(period="7d")
                    if len(df) >= 4:
                        p = df['Close'].values
                        ltp, prev_c = round(p[-1], 2), p[-2]
                        chg = round(((ltp - prev_c) / prev_c) * 100, 2)
                        
                        # আপনার অরিজিনাল ৩ দিন পতন/উত্থান লজিক
                        is_falling_3d = (p[-2] < p[-3] < p[-4])
                        is_rising_3d = (p[-2] > p[-3] > p[-4])
                        
                        trend = "-"
                        if is_falling_3d: trend = "৩ দিন পতন"
                        elif is_rising_3d: trend = "৩ দিন উত্থান"
                        if trend != "-": drastic_res.append({"Stock": s.replace(".NS",""), "Status": trend})

                        sig = "-"
                        if chg >= 2.0 and not is_falling_3d: sig = "🟢 BUY"
                        elif chg <= -2.0 and not is_rising_3d: sig = "🔴 SELL"
                        
                        # প্রফিট/লস অ্যামাউন্ট ক্যালকুলেশন
                        qty = int(investment / ltp)
                        pl_amt = round((ltp - prev_c) * qty, 2)
                        
                        all_res.append({
                            "Stock": s.replace(".NS",""), 
                            "Price": ltp, 
                            "Change%": f"{chg}%", 
                            "Signal": sig,
                            "Profit/Loss": f"₹{pl_amt}",
                            "Qty": qty,
                            "SL": round(ltp*0.985 if "BUY" in sig else ltp*1.015, 2),
                            "T1": round(ltp*1.01 if "BUY" in sig else ltp*0.99, 2),
                            "Trend": trend
                        })
                        if chg > 0: adv += 1
                        else: dec += 1
                        s_chgs.append(chg)
                except: continue
            if s_chgs:
                sec_res.append({"Sector": sector, "Avg%": f"{round(sum(s_chgs)/len(s_chgs), 2)}%"})

    # আপডেট
    st.success(f"🟢 Advances: {adv} | 🔴 Declines: {dec}")

    # ডিসপ্লে লেআউট
    cl, cm, cr = st.columns([1, 2, 1])
    with cl:
        st.subheader("🏢 Sectors")
        st.dataframe(pd.DataFrame(sec_res), hide_index=True)
    with cm:
        st.subheader("🎯 Signals & Amount")
        st.dataframe(pd.DataFrame(all_res), use_container_width=True, hide_index=True)
    with cr:
        st.subheader("⚠️ Drastic")
        st.table(pd.DataFrame(drastic_res))
else:
    st.info("Monday 09:15 AM - Press Button to Scan.")
