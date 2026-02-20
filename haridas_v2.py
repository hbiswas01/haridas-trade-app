import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime
import pytz

# ১. পেজ সেটআপ
st.set_page_config(layout="wide", page_title="Haridas Pro Master Terminal v38.0")

# ইন্ডিয়ান টাইম জোন
IST = pytz.timezone('Asia/Kolkata')

# কাস্টম ডিজাইন
st.markdown("""
    <style>
    .main { background-color: #eaedf2; }
    header {visibility: hidden;}
    .stButton>button { background-color: #007bff; color: white; font-weight: bold; width: 100%; border-radius: 5px; height: 3.5em; font-size: 18px; }
    .idx-box { background-color: #ffffff; padding: 12px; border-radius: 10px; border: 1px solid #e3e6f0; text-align: center; box-shadow: 2px 2px 5px rgba(0,0,0,0.05); }
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

# ৩. টপ বার
top_col1, top_col2 = st.columns([3, 1])
with top_col1:
    st.markdown("<h2 style='color: #0a192f; margin:0;'>📡 HARIDAS MASTER SCANNER</h2>", unsafe_allow_html=True)
with top_col2:
    st.markdown(f"🕒 **LIVE: {datetime.now(IST).strftime('%H:%M:%S')}**")

# ৪. ইনডেক্স
st.write("---")
idx_cols = st.columns(5)
broad_indices = {"SENSEX": "^BSESN", "NIFTY 50": "^NSEI", "NIFTY BANK": "^NSEBANK", "NIFTY IT": "^CNXIT", "NIFTY FIN": "NIFTY_FIN_SERVICE.NS"}

for i, (name, sym) in enumerate(broad_indices.items()):
    try:
        idx_data = yf.Ticker(sym).history(period="2d")
        ltp = round(idx_data['Close'].iloc[-1], 2)
        prev = idx_data['Close'].iloc[-2]
        pct = round(((ltp-prev)/prev)*100, 2)
        color = "#28a745" if pct > 0 else "#dc3545"
        idx_cols[i].markdown(f"""<div class='idx-box'><small>{name}</small><br><b>{ltp}</b><br><span style='color:{color};'>{pct}%</span></div>""", unsafe_allow_html=True)
    except: continue

# ৫. স্ক্যান বাটন
if st.button("🔍 SCAN FOR BUY/SELL SIGNALS", use_container_width=True):
    active_signals = []
    sector_perf = []
    drastic_list = []
    advances, declines = 0, 0

    with st.spinner('বাজার বিশ্লেষণ চলছে...'):
        for sector, stocks in SECTOR_MAP.items():
            s_chgs = []
            for s in stocks:
                try:
                    df = yf.Ticker(s).history(period="7d")
                    if len(df) >= 4:
                        prices = df['Close'].values
                        ltp = round(float(prices[-1]), 2)
                        prev_c = float(prices[-2])
                        chg = round(((ltp - prev_c) / prev_c) * 100, 2)
                        
                        # ৩ দিন পতন/উত্থান
                        trend = "-"
                        if prices[-2] < prices[-3] < prices[-4]: trend = " Falling 📉"
                        elif prices[-2] > prices[-3] > prices[-4]: trend = " Rising 📈"
                        
                        if trend != "-": drastic_list.append({"Stock": s.replace(".NS",""), "Status": trend})

                        # সিগন্যাল লজিক
                        sig = "-"
                        if chg >= 2.0 and "Falling" not in trend: sig = "🟢 BUY"
                        elif chg <= -2.0 and "Rising" not in trend: sig = "🔴 SELL"
                        
                        # শুধু সিগন্যাল থাকলে লিস্টে ঢোকাও
                        if sig != "-":
                            active_signals.append({
                                "Stock": s.replace(".NS",""), "LTP": ltp, "Chg%": f"{chg}%",
                                "Signal": sig, 
                                "SL": round(ltp*0.985 if "BUY" in sig else ltp*1.015, 2),
                                "T1": round(ltp*1.01 if "BUY" in sig else ltp*0.99, 2),
                                "T2": round(ltp*1.02 if "BUY" in sig else ltp*0.98, 2),
                                "Time": datetime.now(IST).strftime('%H:%M:%S')
                            })
                        
                        s_chgs.append(chg)
                        if chg > 0: advances += 1
                        else: declines += 1
                except: continue
            if s_chgs:
                sector_perf.append({"Sector": sector, "Avg%": round(sum(s_chgs)/len(s_chgs), 2)})

    # ৬. ফলাফল প্রদর্শন
    st.write(f"🟢 Advances: {advances} | 🔴 Declines: {declines}")
    col_l, col_r = st.columns([1, 2])

    with col_l:
        st.subheader("🏢 Sector Performance")
        st.dataframe(pd.DataFrame(sector_perf).sort_values(by="Avg%", ascending=False), hide_index=True)
        
        st.subheader("⚠️ Drastic Watch")
        if drastic_list: st.table(pd.DataFrame(drastic_list))
        else: st.write("No drastic moves.")

    with col_r:
        st.subheader("🎯 Active Trading Signals")
        if active_signals:
            st.dataframe(pd.DataFrame(active_signals), use_container_width=True, hide_index=True)
        else:
            st.warning("এই মুহূর্তে কোনো BUY বা SELL সিগন্যাল নেই।")

else:
    st.info("স্ক্যান শুরু করতে উপরের বাটনটি টিপুন।")
