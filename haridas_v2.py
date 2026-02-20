import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime
import pytz

# ১. পেজ সেটআপ
st.set_page_config(layout="wide", page_title="Haridas Pro Master Terminal v38.0")
IST = pytz.timezone('Asia/Kolkata')

# ২. আপনার অরিজিনাল Tkinter স্টাইল এবং কালার
st.markdown("""
    <style>
    .main { background-color: #eaedf2; }
    .stButton>button { background-color: #007bff; color: white; font-weight: bold; width: 100%; border-radius: 5px; height: 3em; }
    .idx-card { background-color: #f8f9fc; padding: 10px; border-radius: 8px; border: 1px solid #e3e6f0; text-align: center; }
    /* সিগন্যাল রো কালার */
    .buy-row { background-color: #d4edda !important; color: #155724 !important; }
    .sell-row { background-color: #f8d7da !important; color: #721c24 !important; }
    </style>
    """, unsafe_allow_html=True)

# ৩. আপনার অরিজিনাল সেক্টর ম্যাপ
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

# ৪. টপ বার
top_c = st.columns([2, 1, 1, 1])
top_c[0].markdown("<h2 style='color: #0a192f; margin:0;'>📡 HARIDAS NSE TERMINAL</h2>", unsafe_allow_html=True)
clock_spot = top_c[1].empty()
adv_spot = top_c[2].empty()
dec_spot = top_c[3].empty()
clock_spot.markdown(f"🕒 **LIVE: {datetime.now(IST).strftime('%H:%M:%S')}**")

# ৫. ইনডেক্স কার্ডস
st.write("---")
indices = {"SENSEX": "^BSESN", "NIFTY 50": "^NSEI", "NIFTY BANK": "^NSEBANK", "NIFTY IT": "^CNXIT", "NIFTY FIN": "NIFTY_FIN_SERVICE.NS"}
idx_cols = st.columns(5)
for i, (name, sym) in enumerate(indices.items()):
    try:
        idat = yf.Ticker(sym).history(period="2d")
        lp = round(idat['Close'].iloc[-1], 2)
        pct = round(((lp - idat['Close'].iloc[-2])/idat['Close'].iloc[-2])*100, 2)
        idx_cols[i].markdown(f"<div class='idx-card'><b>{name}</b><br>{lp}<br><span style='color:{'green' if pct>=0 else 'red'};'>{pct}%</span></div>", unsafe_allow_html=True)
    except: continue

# ৬. স্ক্যানার
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
                        
                        # আপনার অরিজিনাল ৩ দিন পতন/উত্থান লজিক
                        is_falling_3d = (p[-2] < p[-3] < p[-4])
                        is_rising_3d = (p[-2] > p[-3] > p[-4])
                        
                        trend = "-"
                        if is_falling_3d: trend = "৩ দিন পতন"
                        elif is_rising_3d: trend = "৩ দিন উত্থান"
                        if trend != "-": drastic_res.append({"Stock": s.replace(".NS",""), "Status": trend})

                        # পঙ্কজ স্ট্র্যাটেজি সিগন্যাল
                        sig = "-"
                        if chg >= 2.0 and not is_falling_3d: sig = "BUY"
                        elif chg <= -2.0 and not is_rising_3d: sig = "SELL"
                        
                        all_res.append({
                            "Stock": s.replace(".NS",""), "LTP": ltp, "Chg%": f"{chg}%", "Signal": sig,
                            "SL": round(ltp*0.985 if sig=="BUY" else ltp*1.015, 2),
                            "T1": round(ltp*1.01 if sig=="BUY" else ltp*0.99, 2),
                            "T2": round(ltp*1.02 if sig=="BUY" else ltp*0.98, 2),
                            "T3": round(ltp*1.03 if sig=="BUY" else ltp*0.97, 2),
                            "Time": datetime.now(IST).strftime('%H:%M:%S')
                        })
                        if chg > 0: adv += 1
                        else: dec += 1
                        s_chgs.append(chg)
                except: continue
            if s_chgs:
                sec_res.append({"Sector": sector, "Chg%": f"{round(sum(s_chgs)/len(s_chgs), 2)}%"})

    # আপডেট
    adv_spot.markdown(f"🟢 **ADVANCES: {adv}**")
    dec_spot.markdown(f"🔴 **DECLINES: {dec}**")

    # লেআউট
    c_l, c_m, c_r = st.columns([1, 2, 1])
    with c_l:
        st.subheader("🏢 SECTOR PERFORMANCE")
        st.table(pd.DataFrame(sec_res))
    with c_m:
        st.subheader("🎯 TRADING SIGNALS")
        st.dataframe(pd.DataFrame(all_res), use_container_width=True, hide_index=True)
    with c_r:
        st.subheader("🔥 TOP MOVERS")
        df_m = pd.DataFrame(all_res)
        st.write("**Gainers**")
        st.table(df_m.sort_values("LTP", ascending=False)[['Stock', 'Chg%']].head(5))
        st.subheader("⚠️ DRASTIC WATCH")
        st.table(pd.DataFrame(drastic_res))
else:
    st.info("Monday 09:15 AM - Press Button to Scan.")
