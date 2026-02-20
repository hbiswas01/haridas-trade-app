import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime

# ১. পেজ সেটআপ (ল্যাপটপের মতো চওড়া ভিউ)
st.set_page_config(layout="wide", page_title="Haridas Pro Master Terminal v38.0")

# সিএসএস দিয়ে কালার ডিজাইন
st.markdown("""
    <style>
    .main { background-color: #eaedf2; }
    .stButton>button { background-color: #007bff; color: white; width: 100%; border-radius: 5px; }
    .index-card { background-color: #f8f9fc; padding: 10px; border-radius: 10px; border: 1px solid #e3e6f0; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

# ২. সেক্টর ম্যাপ
SECTOR_MAP = {
    "NIFTY BANK 🏦": ["HDFCBANK.NS", "ICICIBANK.NS", "SBIN.NS", "KOTAKBANK.NS", "AXISBANK.NS"],
    "NIFTY IT 💻": ["TCS.NS", "INFY.NS", "HCLTECH.NS", "WIPRO.NS", "TECHM.NS"],
    "NIFTY AUTO 🚗": ["TATAMOTORS.NS", "MARUTI.NS", "M&M.NS", "BAJAJ-AUTO.NS", "EICHERMOT.NS"],
    "NIFTY ENERGY ⚡": ["RELIANCE.NS", "NTPC.NS", "POWERGRID.NS", "ONGC.NS"],
    "NIFTY FMCG 🛒": ["ITC.NS", "HINDUNILVR.NS", "NESTLEIND.NS", "BRITANNIA.NS"]
}

# ৩. টাইটেল ও ঘড়ি
col_t1, col_t2 = st.columns([3, 1])
with col_t1:
    st.markdown("<h2 style='color: #0a192f;'>📊 HARIDAS NSE TERMINAL</h2>", unsafe_allow_html=True)
with col_t2:
    st.write(f"🕒 {datetime.now().strftime('%H:%M:%S')}")

# ৪. মার্কেট ইনডেক্স সেকশন
st.markdown("### 📈 MARKET INDICES")
idx_cols = st.columns(5)
indices = {"SENSEX": "^BSESN", "NIFTY 50": "^NSEI", "NIFTY BANK": "^NSEBANK", "NIFTY IT": "^CNXIT", "NIFTY FIN": "NIFTY_FIN_SERVICE.NS"}

for i, (name, sym) in enumerate(indices.items()):
    try:
        data = yf.Ticker(sym).history(period="2d")
        ltp = round(data['Close'].iloc[-1], 2)
        chg = round(((ltp - data['Close'].iloc[-2])/data['Close'].iloc[-2])*100, 2)
        color = "green" if chg >= 0 else "red"
        with idx_cols[i]:
            st.markdown(f"""<div class='index-card'>
                <p style='color: gray;'>{name}</p>
                <h4 style='margin:0;'>{ltp}</h4>
                <p style='color: {color};'>{chg}%</p>
            </div>""", unsafe_allow_html=True)
    except: continue

st.write("---")

# ৫. মেইন স্ক্যানার বাটন
if st.button("🚀 SCAN MARKET (PANKAJ STRATEGY)"):
    all_stocks = []
    sector_perf = []

    with st.spinner('পুরো বাজার স্ক্যান হচ্ছে...'):
        for sector, stocks in SECTOR_MAP.items():
            sector_chgs = []
            for s in stocks:
                try:
                    df = yf.Ticker(s).history(period="5d")
                    prices = df['Close'].values
                    ltp = round(prices[-1], 2)
                    chg = round(((prices[-1] - prices[-2])/prices[-2])*100, 2)
                    
                    # ৩ দিনের ড্রাস্টিক পতন/উত্থান চেক
                    status = "-"
                    if prices[-2] < prices[-3] < prices[-4]: status = "৩ দিন পতন"
                    elif prices[-2] > prices[-3] > prices[-4]: status = "৩ দিন উত্থান"
                    
                    # পঙ্কজ স্ট্র্যাটেজি সিগন্যাল
                    signal = "-"
                    if chg >= 2.0 and "পতন" not in status: signal = "🟢 BUY"
                    elif chg <= -2.0 and "উত্থান" not in status: signal = "🔴 SELL"
                    
                    sl = round(ltp * 0.985, 2) if "BUY" in signal else round(ltp * 1.015, 2)
                    t1 = round(ltp * 1.01, 2) if "BUY" in signal else round(ltp * 0.99, 2)
                    
                    all_stocks.append({
                        "Stock": s.replace(".NS",""), "LTP": ltp, "Chg%": f"{chg}%", 
                        "Signal": signal, "SL": sl, "Target": t1, "Status": status
                    })
                    sector_chgs.append(chg)
                except: continue
            
            if sector_chgs:
                sector_perf.append({"Sector": sector, "Avg Chg%": round(sum(sector_chgs)/len(sector_chgs), 2)})

    # ৬. ডিসপ্লে লেআউট (৩ কলাম)
    col1, col2, col3 = st.columns([1, 2, 1])

    with col1:
        st.markdown("#### 🏢 Sector Performance")
        st.table(pd.DataFrame(sector_perf).sort_values(by="Avg Chg%", ascending=False))

    with col2:
        st.markdown("#### 🎯 Trading Signals")
        sig_df = pd.DataFrame(all_stocks)
        # শুধু যেখানে সিগন্যাল আছে সেগুলো দেখাবে
        active_sigs = sig_df[sig_df['Signal'] != "-"]
        if not active_sigs.empty:
            st.dataframe(active_sigs, use_container_width=True)
        else:
            st.info("এই মুহূর্তে কোনো কনফার্ম সিগন্যাল নেই।")

    with col3:
        st.markdown("#### ⚠️ Drastic Watch")
        st.table(sig_df[sig_df['Status'] != "-"][["Stock", "Status"]])

st.caption("হরিদাস ভাই, এই স্ক্যানারটি পঙ্কজ সিনহা এবং পঙ্কজ ভরদ্বাজ এর লজিক মেনে তৈরি।")
