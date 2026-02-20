import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime

# ১. পেজ সেটআপ
st.set_page_config(layout="wide", page_title="Haridas Pro Terminal")

# ২. স্টাইল (পরিষ্কার এবং সহজ লুক)
st.markdown("""
    <style>
    .main { background-color: #eaedf2; }
    .stButton>button { background-color: #007bff; color: white; width: 100%; border-radius: 5px; height: 3.5em; font-weight: bold; font-size: 18px; }
    .index-card { background-color: #ffffff; padding: 15px; border-radius: 10px; border: 1px solid #e3e6f0; text-align: center; box-shadow: 2px 2px 5px rgba(0,0,0,0.05); }
    </style>
    """, unsafe_allow_html=True)

# ৩. সেক্টর ও স্টক লিস্ট
SECTOR_MAP = {
    "BANK 🏦": ["HDFCBANK.NS", "ICICIBANK.NS", "SBIN.NS", "KOTAKBANK.NS", "AXISBANK.NS"],
    "IT 💻": ["TCS.NS", "INFY.NS", "HCLTECH.NS", "WIPRO.NS", "TECHM.NS"],
    "AUTO 🚗": ["TATAMOTORS.NS", "MARUTI.NS", "M&M.NS", "BAJAJ-AUTO.NS", "EICHERMOT.NS"],
    "ENERGY ⚡": ["RELIANCE.NS", "NTPC.NS", "POWERGRID.NS", "ONGC.NS"],
    "FMCG 🛒": ["ITC.NS", "HINDUNILVR.NS", "NESTLEIND.NS", "BRITANNIA.NS"],
    "PHARMA 💊": ["SUNPHARMA.NS", "CIPLA.NS", "DRREDDY.NS", "DIVISLAB.NS"]
}

# ৪. টাইটেল
st.markdown("<h1 style='text-align: center; color: #0a192f;'>📊 HARIDAS MASTER SCANNER</h1>", unsafe_allow_html=True)
st.markdown(f"<p style='text-align: center; font-size: 20px;'>🕒 সময়: {datetime.now().strftime('%H:%M:%S')}</p>", unsafe_allow_html=True)

# ৫. মার্কেট ইনডেক্স
st.markdown("### 📈 MARKET INDICES")
idx_cols = st.columns(5)
indices = {"SENSEX": "^BSESN", "NIFTY 50": "^NSEI", "NIFTY BANK": "^NSEBANK", "NIFTY IT": "^CNXIT", "NIFTY FIN": "NIFTY_FIN_SERVICE.NS"}

for i, (name, sym) in enumerate(indices.items()):
    try:
        idx_data = yf.Ticker(sym).history(period="2d")
        l_price = round(idx_data['Close'].iloc[-1], 2)
        l_chg = round(((l_price - idx_data['Close'].iloc[-2])/idx_data['Close'].iloc[-2])*100, 2)
        l_color = "green" if l_chg >= 0 else "red"
        with idx_cols[i]:
            st.markdown(f"""<div class='index-card'>
                <p style='color: gray; margin:0;'>{name}</p>
                <h3 style='margin:5px 0;'>{l_price}</h3>
                <p style='color: {l_color}; font-weight: bold;'>{l_chg}%</p>
            </div>""", unsafe_allow_html=True)
    except: continue

st.write("---")

# ৬. স্ক্যান বাটন
if st.button("🔍 SCAN MARKET NOW"):
    all_data = []
    sector_summary = []
    
    with st.spinner('বিশ্লেষণ চলছে...'):
        for sector, stocks in SECTOR_MAP.items():
            s_changes = []
            for s in stocks:
                try:
                    df = yf.Ticker(s).history(period="5d")
                    if len(df) >= 4:
                        prices = df['Close'].values
                        ltp = round(prices[-1], 2)
                        chg = round(((prices[-1] - prices[-2])/prices[-2])*100, 2)
                        
                        # ৩ দিনের মুভমেন্ট
                        status = "Normal"
                        if prices[-2] < prices[-3] < prices[-4]: status = "Falling 📉"
                        elif prices[-2] > prices[-3] > prices[-4]: status = "Rising 📈"
                        
                        # সিগন্যাল লজিক (২%)
                        signal = "WAIT"
                        if chg >= 2.0 and "Falling" not in status: signal = "🟢 BUY"
                        elif chg <= -2.0 and "Rising" not in status: signal = "🔴 SELL"
                        
                        sl = round(ltp * 0.985, 2) if "BUY" in signal else round(ltp * 1.015, 2)
                        t1 = round(ltp * 1.01, 2) if "BUY" in signal else round(ltp * 0.99, 2)
                        
                        all_data.append({
                            "Stock": s.replace(".NS",""), "LTP": ltp, "Change%": f"{chg}%", 
                            "Action": signal, "SL": sl, "Target": t1, "3D-Trend": status
                        })
                        s_changes.append(chg)
                except: continue
            
            if s_changes:
                sector_summary.append({"Sector": sector, "Avg%": round(sum(s_changes)/len(s_changes), 2)})

    # রেজাল্ট টেবিল
    col_a, col_b = st.columns([1, 3])
    with col_a:
        st.markdown("#### 🏢 Sectors")
        st.table(pd.DataFrame(sector_summary).sort_values(by="Avg%", ascending=False))
    
    with col_b:
        st.markdown("#### 🎯 Signals")
        st.dataframe(pd.DataFrame(all_data), use_container_width=True, hide_index=True)

st.markdown("---")
st.write("হরিদাস ভাই, সোমবার সকাল ৯:১৫ তে ক্লিক করবেন।")
