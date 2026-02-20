import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime
import pytz

# ১. পেজ সেটআপ ও মোবাইল অপ্টিমাইজেশন
st.set_page_config(layout="wide", page_title="Haridas Master Terminal")
IST = pytz.timezone('Asia/Kolkata')

st.markdown("""
    <style>
    .main { background-color: #eaedf2; }
    header {visibility: hidden;}
    .stButton>button { background: linear-gradient(to right, #007bff, #00c6ff); color: white; font-weight: bold; width: 100%; border-radius: 10px; height: 3.5em; font-size: 18px; }
    .idx-card { background-color: #ffffff; padding: 15px; border-radius: 12px; border: 1px solid #e3e6f0; text-align: center; box-shadow: 2px 2px 5px rgba(0,0,0,0.05); }
    .stat-header { background-color: #4e73df; color: white; padding: 6px; border-radius: 5px; text-align: center; font-weight: bold; margin-bottom: 5px; }
    html, body, [class*="css"] { font-size: 18px !important; }
    </style>
    """, unsafe_allow_html=True)

# ২. সেক্টর লিস্ট
SECTOR_MAP = {
    "NIFTY BANK 🏦": ["HDFCBANK.NS", "ICICIBANK.NS", "SBIN.NS", "KOTAKBANK.NS", "AXISBANK.NS"],
    "NIFTY IT 💻": ["TCS.NS", "INFY.NS", "HCLTECH.NS", "WIPRO.NS", "TECHM.NS"],
    "NIFTY AUTO 🚗": ["TATAMOTORS.NS", "MARUTI.NS", "M&M.NS", "BAJAJ-AUTO.NS", "EICHERMOT.NS"],
    "NIFTY ENERGY ⚡": ["RELIANCE.NS", "NTPC.NS", "POWERGRID.NS", "ONGC.NS"],
    "NIFTY FIN 💹": ["BAJFINANCE.NS", "BAJAJFINSV.NS", "CHOLAFIN.NS"]
}

# ৩. বাজেট সেটিংস
st.sidebar.markdown("### 💰 Investment Settings")
budget = st.sidebar.number_input("আপনার বাজেট (টাকা):", value=100000, step=5000)

# ৪. টপ বার
st.markdown(f"<h1 style='text-align: center; color: #0a192f;'>📡 HARIDAS LIVE TERMINAL</h1>", unsafe_allow_html=True)
st.markdown(f"<p style='text-align: center; font-weight: bold;'>🕒 ইন্ডিয়ান সময়: {datetime.now(IST).strftime('%H:%M:%S')}</p>", unsafe_allow_html=True)

# ৫. মার্কেট ইনডেক্স উইথ অ্যামাউন্ট (Nifty/Sensex Point Change)
st.write("---")
st.subheader("📊 Market Indices Status")
indices = {"SENSEX": "^BSESN", "NIFTY 50": "^NSEI", "NIFTY BANK": "^NSEBANK", "NIFTY IT": "^CNXIT"}
idx_cols = st.columns(4)

for i, (name, sym) in enumerate(indices.items()):
    try:
        idat = yf.Ticker(sym).history(period="2d")
        lp = round(idat['Close'].iloc[-1], 2)
        prev = idat['Close'].iloc[-2]
        pts = round(lp - prev, 2)
        pct = round((pts/prev)*100, 2)
        color = "#28a745" if pts >= 0 else "#dc3545"
        idx_cols[i].markdown(f"""<div class='idx-card'>
            <b>{name}</b><br><span style='font-size: 22px;'>{lp}</span><br>
            <span style='color:{color}; font-weight: bold;'>{'+' if pts > 0 else ''}{pts} ({pct}%)</span>
        </div>""", unsafe_allow_html=True)
    except: continue

# ৬. মেইন স্ক্যানার বাটন
st.write("---")
if st.button("🔍 SCAN MARKET NOW (LIVE PROFIT)", use_container_width=True):
    all_res, sec_res, drastic_res = [], [], []
    adv, dec = 0, 0

    with st.spinner('Analysing Live Market...'):
        for sector, stocks in SECTOR_MAP.items():
            s_chgs = []
            for s in stocks:
                try:
                    df = yf.Ticker(s).history(period="7d")
                    if len(df) >= 4:
                        p = df['Close'].values
                        ltp, prev_c = round(float(p[-1]), 2), float(p[-2])
                        chg_pct = round(((ltp - prev_c) / prev_c) * 100, 2)
                        
                        # ৩ দিন ট্রেন্ড
                        trend = "Normal"
                        if p[-2] < p[-3] < p[-4]: trend = "Falling 📉"
                        elif p[-2] > p[-3] > p[-4]: trend = "Rising 📈"
                        
                        # সিগন্যাল ও এন্ট্রি প্রাইজ
                        sig = "WAIT"
                        entry_price = ltp
                        if chg_pct >= 2.0 and "Falling" not in trend: sig = "🟢 BUY"
                        elif chg_pct <= -2.0 and "Rising" not in trend: sig = "🔴 SELL"
                        
                        # লাইভ প্রফিট ক্যালকুলেশন
                        qty = int(budget / ltp)
                        current_pl = round((ltp - prev_c) * qty, 2)
                        
                        all_res.append({
                            "Stock": s.replace(".NS",""), 
                            "Live Price": ltp, 
                            "Entry At": entry_price,
                            "Move%": f"{chg_pct}%",
                            "Signal": sig,
                            "Live P/L": f"₹{current_pl}",
                            "Qty": qty,
                            "StopLoss": round(ltp*0.985 if "BUY" in sig else ltp*1.015, 2) if sig != "WAIT" else "-"
                        })
                        if chg_pct > 0: adv += 1
                        else: dec += 1
                        s_chgs.append(chg_pct)
                        if trend != "Normal": drastic_res.append({"Stock": s.replace(".NS",""), "Trend": trend})
                except: continue
            if s_chgs:
                sec_res.append({"Sector": sector, "Avg%": f"{round(sum(s_chgs)/len(s_chgs), 2)}%"})

    # ফলাফল ডিসপ্লে
    st.success(f"🟢 Advances: {adv} | 🔴 Declines: {dec}")
    
    st.markdown("<div class='stat-header'>🎯 LIVE SIGNALS & PROFIT ANALYSIS</div>", unsafe_allow_html=True)
    st.dataframe(pd.DataFrame(all_res), use_container_width=True, hide_index=True)

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("<div class='stat-header'>🏢 SECTOR PERFORMANCE</div>", unsafe_allow_html=True)
        st.table(pd.DataFrame(sec_res))
    with c2:
        st.markdown("<div class='stat-header'>⚠️ DRASTIC WATCH</div>", unsafe_allow_html=True)
        if drastic_res: st.table(pd.DataFrame(drastic_res))
        else: st.write("No drastic trends found.")
else:
    st.info("সোমবার সকাল ৯:১৫ তে বাজার খুললে স্ক্যান বাটনে চাপ দিন।")
