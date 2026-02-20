import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime
import pytz  # ইন্ডিয়ান সময়ের জন্য

# ১. পেজ সেটআপ (মোবাইলে যাতে সুন্দর দেখায়)
st.set_page_config(layout="wide", page_title="Haridas Pro Web")

# ইন্ডিয়ান টাইম জোন সেটআপ
IST = pytz.timezone('Asia/Kolkata')
current_time = datetime.now(IST).strftime('%d %b, %H:%M:%S')

# কাস্টম স্টাইল: নীল হেডার ও সাদা ব্যাকগ্রাউন্ড
st.markdown("""
    <style>
    .main { background-color: #ffffff; }
    div.stButton > button:first-child { 
        background: linear-gradient(to right, #007bff, #00c6ff); 
        color: white; 
        font-weight: bold; 
        border-radius: 10px; 
        height: 3em;
        font-size: 18px;
    }
    .stMetric { background-color: #f0f2f6; border-radius: 10px; padding: 15px; border: 1px solid #d1d9e6; }
    </style>
    """, unsafe_allow_html=True)

# ২. স্টক লিস্ট এবং সেক্টর
SECTOR_MAP = {
    "NIFTY BANK 🏦": ["HDFCBANK.NS", "ICICIBANK.NS", "SBIN.NS", "KOTAKBANK.NS", "AXISBANK.NS"],
    "NIFTY IT 💻": ["TCS.NS", "INFY.NS", "HCLTECH.NS", "WIPRO.NS", "TECHM.NS"],
    "NIFTY AUTO 🚗": ["TATAMOTORS.NS", "MARUTI.NS", "M&M.NS", "BAJAJ-AUTO.NS", "EICHERMOT.NS"],
    "NIFTY METAL ⚙️": ["TATASTEEL.NS", "JSWSTEEL.NS", "HINDALCO.NS", "VEDL.NS"],
    "NIFTY ENERGY ⚡": ["RELIANCE.NS", "NTPC.NS", "POWERGRID.NS", "ONGC.NS"]
}

st.markdown(f"<h1 style='text-align: center; color: #007bff;'>📊 HARIDAS MOBILE TERMINAL</h1>", unsafe_allow_html=True)
st.markdown(f"<p style='text-align: center; font-weight: bold;'>🇮🇳 সর্বশেষ স্ক্যান: {current_time}</p>", unsafe_allow_html=True)

# ৩. স্ক্যান বাটন
if st.button("🚀 SCAN MARKET NOW (Mobile View)", use_container_width=True):
    # ইনডেক্স সেকশন
    st.subheader("📊 Market Indices")
    idx_cols = st.columns(3) # মোবাইলের জন্য ৩ কলাম
    indices = {"NIFTY 50": "^NSEI", "BANK NIFTY": "^NSEBANK", "NIFTY FIN": "NIFTY_FIN_SERVICE.NS"}
    
    for i, (name, sym) in enumerate(indices.items()):
        try:
            d = yf.Ticker(sym).history(period="5d").dropna()
            if not d.empty:
                ltp = round(d['Close'].iloc[-1], 2)
                prev = d['Close'].iloc[-2]
                chg = round(ltp - prev, 2)
                chg_pct = round((chg / prev) * 100, 2)
                idx_cols[i % 3].metric(name, f"{ltp}", f"{chg} ({chg_pct}%)")
        except: continue

    st.markdown("---")
    
    # সিগন্যাল প্রসেসিং
    all_sig = []
    with st.spinner('বাজার বিশ্লেষণ চলছে...'):
        for sector, stocks in SECTOR_MAP.items():
            for s in stocks:
                try:
                    hist = yf.Ticker(s).history(period="5d").dropna()
                    if len(hist) >= 4:
                        p = hist['Close'].values
                        ltp = round(float(p[-1]), 2)
                        prev_p = float(p[-2])
                        chg_pct = round(((ltp - prev_p) / prev_p) * 100, 2)
                        
                        # ৩ দিন পতন চেক
                        is_fall_3d = (p[-2] < p[-3] < p[-4])
                        # ৩ দিন উত্থান চেক
                        is_rise_3d = (p[-2] > p[-3] > p[-4])
                        
                        sig = "-"
                        if chg_pct >= 2.0 and not is_fall_3d: 
                            sig = "🟢 BUY"
                        elif chg_pct <= -2.0 and not is_rise_3d: 
                            sig = "🔴 SELL"
                        
                        if sig != "-":
                            all_sig.append({
                                "Stock": s.replace(".NS",""), 
                                "LTP": ltp, 
                                "Change%": f"{chg_pct}%", 
                                "Signal": sig, 
                                "T1 (1%)": round(ltp*1.01 if "BUY" in sig else ltp*0.99, 2), 
                                "T2 (2%)": round(ltp*1.02 if "BUY" in sig else ltp*0.98, 2), 
                                "SL (1.5%)": round(ltp*0.985 if "BUY" in sig else ltp*1.015, 2)
                            })
                except: continue

    if all_sig:
        st.subheader("🎯 Trading Signals")
        st.dataframe(pd.DataFrame(all_sig), use_container_width=True, hide_index=True)
    else:
        st.info("বাজারে এই মুহূর্তে আপনার স্ট্র্যাটেজি অনুযায়ী কোনো সিগন্যাল নেই।")

st.markdown("---")
st.write("হরিদাস ভাই, সোমবার সকাল ৯:১৫ তে ক্লিক করবেন।")
