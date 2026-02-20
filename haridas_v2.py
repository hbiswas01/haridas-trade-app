import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime
import pytz

# ১. পেজ সেটআপ ও ডিজাইন (Tkinter লুকের জন্য)
st.set_page_config(layout="wide", page_title="Haridas Pro Master Terminal v38.0")
IST = pytz.timezone('Asia/Kolkata')

st.markdown("""
    <style>
    .main { background-color: #eaedf2; }
    header {visibility: hidden;}
    .stButton>button { background: linear-gradient(to right, #007bff, #00c6ff); color: white; font-weight: bold; width: 100%; border-radius: 8px; height: 3.5em; font-size: 18px; }
    .idx-card { background-color: #f8f9fc; padding: 12px; border-radius: 10px; border: 1px solid #e3e6f0; text-align: center; box-shadow: 2px 2px 5px rgba(0,0,0,0.05); }
    .stat-header { background-color: #4e73df; color: white; padding: 6px; border-radius: 5px; text-align: center; font-weight: bold; margin-bottom: 5px; font-size: 16px; }
    /* মোবাইলের জন্য ফন্ট সাইজ অ্যাডজাস্ট */
    html, body, [class*="css"] { font-size: 17px !important; }
    </style>
    """, unsafe_allow_html=True)

# ২. আপনার অরিজিনাল সেক্টর ম্যাপ
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

# ৩. বাজেট সাইডবার (অ্যামাউন্ট দেখার জন্য)
st.sidebar.markdown("### 💰 Profit & Quantity Settings")
investment = st.sidebar.number_input("আপনার বাজেট (টাকা):", value=100000, step=5000)

# ৪. টপ বার (টাইটেল, ঘড়ি, অ্যাডভান্স/ডিক্লাইন)
t_col1, t_col2, t_col3, t_col4 = st.columns([2, 1, 1, 1])
with t_col1:
    st.markdown("<h2 style='color: #0a192f; margin:0;'>📡 HARIDAS NSE TERMINAL</h2>", unsafe_allow_html=True)
with t_col2:
    st.markdown(f"🕒 **LIVE: {datetime.now(IST).strftime('%H:%M:%S')}**")

adv_spot = t_col3.empty()
dec_spot = t_col4.empty()

# ৫. মার্কেট ইনডেক্স কার্ডস
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

# ৬. মেইন স্ক্যানার বাটন
st.write("---")
if st.button("🔍 SCAN MARKET NOW (FULL ANALYSIS)", use_container_width=True):
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
                        ltp, prev_c = round(float(p[-1]), 2), float(p[-2])
                        chg = round(((ltp - prev_c) / prev_c) * 100, 2)
                        
                        # আপনার অরিজিনাল ৩ দিনের ড্রাস্টিক লজিক
                        trend = "-"
                        if p[-2] < p[-3] < p[-4]: trend = "Falling 📉"
                        elif p[-2] > p[-3] > p[-4]: trend = "Rising 📈"
                        if trend != "-": drastic_res.append({"Stock": s.replace(".NS",""), "Status": trend})

                        # সিগন্যাল লজিক (পঙ্কজ ২% স্ট্র্যাটেজি)
                        sig = "-"
                        if chg >= 2.0 and "Falling" not in trend: sig = "🟢 BUY"
                        elif chg <= -2.0 and "Rising" not in trend: sig = "🔴 SELL"
                        
                        # প্রফিট/লস অ্যামাউন্ট ক্যালকুলেশন (বাজেট অনুযায়ী)
                        qty = int(investment / ltp)
                        pl_amt = round((ltp - prev_c) * qty, 2)
                        
                        all_res.append({
                            "Stock": s.replace(".NS",""), "LTP": ltp, "Chg%": f"{chg}%", 
                            "Signal": sig, "Qty": qty, "P/L": f"₹{pl_amt}",
                            "SL": round(ltp*0.985 if "BUY" in sig else ltp*1.015, 2),
                            "T1": round(ltp*1.01 if "BUY" in sig else ltp*0.99, 2),
                            "Time": datetime.now(IST).strftime('%H:%M:%S')
                        })
                        if chg > 0: adv += 1
                        else: dec += 1
                        s_chgs.append(chg)
                except: continue
            if s_chgs:
                sec_res.append({"Sector": sector, "Avg%": f"{round(sum(s_chgs)/len(s_chgs), 2)}%"})

    # টপ বার আপডেট
    adv_spot.markdown(f"🟢 **ADVANCES: {adv}**")
    dec_spot.markdown(f"🔴 **DECLINES: {dec}**")

    # ৭. আপনার অরিজিনাল ৩-কলাম রেসপনসিভ লেআউট
    c_left, c_mid, c_right = st.columns([1, 2, 1])

    with c_left:
        st.markdown("<div class='stat-header'>🏢 SECTOR PERFORMANCE</div>", unsafe_allow_html=True)
        st.dataframe(pd.DataFrame(sec_res).sort_values("Avg%", ascending=False), hide_index=True, use_container_width=True)

    with c_mid:
        st.markdown("<div class='stat-header'>🎯 TRADING SIGNALS & PROFIT</div>", unsafe_allow_html=True)
        st.dataframe(pd.DataFrame(all_res), use_container_width=True, hide_index=True)

    with c_right:
        st.markdown("<div class='stat-header'>🔥 TOP MOVERS</div>", unsafe_allow_html=True)
        df_m = pd.DataFrame(all_res)
        st.write("**Top 5 Gainers**")
        st.table(df_m.sort_values("Chg%", ascending=False)[['Stock', 'Chg%']].head(5))
        
        st.markdown("<div class='stat-header'>⚠️ DRASTIC WATCH</div>", unsafe_allow_html=True)
        if drastic_res: st.table(pd.DataFrame(drastic_res))
        else: st.write("No drastic moves.")
else:
    st.info("Monday 09:15 AM - Press Button to Scan Market.")
