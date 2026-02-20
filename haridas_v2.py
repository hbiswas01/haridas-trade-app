import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime
import pytz

# ১. পেজ সেটআপ ও স্টাইল (ল্যাপটপ ইন্টারফেস লুক)
st.set_page_config(layout="wide", page_title="Haridas Pro Master Terminal v38.0")

IST = pytz.timezone('Asia/Kolkata')

st.markdown("""
    <style>
    .main { background-color: #eaedf2; }
    .stButton>button { background-color: #007bff; color: white; font-weight: bold; width: 100%; border-radius: 5px; height: 3em; }
    .idx-label { background-color: #f8f9fc; padding: 10px; border-radius: 5px; border: 1px solid #e3e6f0; text-align: center; }
    .adv-label { color: #00e676; font-weight: bold; font-size: 18px; }
    .dec-label { color: #ff4444; font-weight: bold; font-size: 18px; }
    </style>
    """, unsafe_allow_html=True)

# ২. সেক্টর ম্যাপ
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

# ৩. টপ বার (টাইটেল, অ্যাডভান্স/ডিক্লাইন, ঘড়ি)
top_f = st.container()
with top_f:
    c1, c2, c3, c4 = st.columns([2, 1, 1, 1])
    c1.markdown("<h2 style='color: #0a192f; margin:0;'>📡 HARIDAS NSE TERMINAL</h2>", unsafe_allow_html=True)
    clock_spot = c2.empty()
    adv_spot = c3.empty()
    dec_spot = c4.empty()
    clock_spot.markdown(f"🕒 **LIVE: {datetime.now(IST).strftime('%H:%M:%S')}**")

# ৪. মার্কেট ইনডেক্স কার্ডস
st.write("---")
idx_cols = st.columns(5)
indices = {"SENSEX": "^BSESN", "NIFTY 50": "^NSEI", "NIFTY BANK": "^NSEBANK", "NIFTY IT": "^CNXIT", "NIFTY FIN": "NIFTY_FIN_SERVICE.NS"}

for i, (name, sym) in enumerate(indices.items()):
    try:
        idat = yf.Ticker(sym).history(period="2d")
        l_p = round(idat['Close'].iloc[-1], 2)
        l_c = round(l_p - idat['Close'].iloc[-2], 2)
        l_pct = round((l_c/idat['Close'].iloc[-2])*100, 2)
        col = "green" if l_c >= 0 else "red"
        idx_cols[i].markdown(f"<div class='idx-label'><b>{name}</b><br>{l_p}<br><span style='color:{col};'>{l_c} ({l_pct}%)</span></div>", unsafe_allow_html=True)
    except: continue

# ৫. মেইন বডি (৩ কলাম লেআউট)
st.write("---")
body_col1, body_col2, body_col3 = st.columns([1, 2, 1])

if st.button("🔍 SCAN MARKET NOW", use_container_width=True):
    all_res = []
    sec_res = []
    drastic_res = []
    adv, dec = 0, 0

    with st.spinner('Analysing Market...'):
        for sector, stocks in SECTOR_MAP.items():
            s_chgs = []
            for s in stocks:
                try:
                    df = yf.Ticker(s).history(period="7d")
                    if len(df) >= 4:
                        p = df['Close'].values
                        ltp, prev = round(p[-1], 2), p[-2]
                        chg = round(((ltp - prev) / prev) * 100, 2)
                        
                        # ৩ দিন ট্রেন্ড
                        trend = "-"
                        if p[-2] < p[-3] < p[-4]: trend = " Falling 📉"
                        elif p[-2] > p[-3] > p[-4]: trend = " Rising 📈"
                        if trend != "-": drastic_res.append({"Stock": s.replace(".NS",""), "Status": trend})

                        # সিগন্যাল
                        sig = "-"
                        if chg >= 2.0 and "Falling" not in trend: sig = "BUY"
                        elif chg <= -2.0 and "Rising" not in trend: sig = "SELL"
                        
                        all_res.append({
                            "Stock": s.replace(".NS",""), "LTP": ltp, "Chg%": chg, "Signal": sig,
                            "SL": round(ltp*0.985 if sig=="BUY" else ltp*1.015, 2),
                            "T1": round(ltp*1.01 if sig=="BUY" else ltp*0.99, 2),
                            "T2": round(ltp*1.02 if sig=="BUY" else ltp*0.98, 2),
                            "T3": round(ltp*1.03 if sig=="BUY" else ltp*0.97, 2),
                            "Time": datetime.now(IST).strftime('%H:%M:%S')
                        })
                        s_chgs.append(chg)
                        if chg > 0: adv += 1
                        else: dec += 1
                except: continue
            if s_chgs:
                sec_res.append({"Sector": sector, "Chg%": round(sum(s_chgs)/len(s_chgs), 2)})

    # ডাটা ডিসপ্লে
    adv_spot.markdown(f"<span class='adv-label'>ADVANCES: {adv}</span>", unsafe_allow_html=True)
    dec_spot.markdown(f"<span class='dec-label'>DECLINES: {dec}</span>", unsafe_allow_html=True)

    with body_col1:
        st.subheader("🏢 SECTOR PERFORMANCE")
        st.dataframe(pd.DataFrame(sec_res).sort_values("Chg%", ascending=False), hide_index=True)

    with body_col2:
        st.subheader("🎯 TRADING SIGNALS")
        st.dataframe(pd.DataFrame(all_res), use_container_width=True, hide_index=True)

    with body_col3:
        st.subheader("🔥 TOP MOVERS")
        df_m = pd.DataFrame(all_res).sort_values("Chg%", ascending=False)
        st.write("**Top Gainers**")
        st.table(df_m[['Stock', 'Chg%']].head(5))
        st.write("**Top Losers**")
        st.table(df_m[['Stock', 'Chg%']].tail(5))
        st.subheader("⚠️ DRASTIC WATCH")
        st.table(pd.DataFrame(drastic_res))

else:
    st.info("Monday 09:15 AM - Press the Button to Scan.")
