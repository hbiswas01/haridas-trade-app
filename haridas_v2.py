import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime
import pytz

# ১. পেজ সেটআপ (ল্যাপটপের মতো চওড়া ভিউ)
st.set_page_config(layout="wide", page_title="Haridas Pro Master Terminal v38.0")

# ইন্ডিয়ান টাইম জোন
IST = pytz.timezone('Asia/Kolkata')

# কাস্টম ডিজাইন (ল্যাপটপ লুকের জন্য)
st.markdown("""
    <style>
    .main { background-color: #eaedf2; }
    header {visibility: hidden;}
    .stButton>button { background-color: #007bff; color: white; font-weight: bold; width: 100%; border-radius: 5px; height: 3em; }
    .idx-box { background-color: #f8f9fc; padding: 10px; border-radius: 8px; border: 1px solid #e3e6f0; text-align: center; margin-bottom: 10px; }
    .buy-row { background-color: #d4edda; color: #155724; font-weight: bold; padding: 5px; }
    .sell-row { background-color: #f8d7da; color: #721c24; font-weight: bold; padding: 5px; }
    </style>
    """, unsafe_allow_html=True)

# ২. সেক্টর ম্যাপ (আপনার কোড অনুযায়ী)
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

# ৩. টপ বার (টাইটেল, ঘড়ি, অ্যাডভান্স/ডিক্লাইন)
top_col1, top_col2, top_col3 = st.columns([2, 1, 1])
with top_col1:
    st.markdown("<h2 style='color: #0a192f; margin:0;'>📡 HARIDAS NSE TERMINAL</h2>", unsafe_allow_html=True)
with top_col2:
    st.markdown(f"🕒 **LIVE: {datetime.now(IST).strftime('%H:%M:%S')}**")

# ৪. মার্কেট ইনডেক্স সেকশন (Market Indices)
st.write("---")
idx_cols = st.columns(5)
broad_indices = {"SENSEX": "^BSESN", "NIFTY 50": "^NSEI", "NIFTY BANK": "^NSEBANK", "NIFTY IT": "^CNXIT", "NIFTY FIN": "NIFTY_FIN_SERVICE.NS"}

for i, (name, sym) in enumerate(broad_indices.items()):
    try:
        idx_data = yf.Ticker(sym).history(period="2d")
        ltp = round(idx_data['Close'].iloc[-1], 2)
        prev = idx_data['Close'].iloc[-2]
        chg = round(ltp - prev, 2)
        pct = round((chg/prev)*100, 2)
        color = "#28a745" if chg > 0 else "#dc3545"
        idx_cols[i].markdown(f"""<div class='idx-box'>
            <small>{name}</small><br><b>{ltp}</b><br><span style='color:{color};'>{chg} ({pct}%)</span>
        </div>""", unsafe_allow_html=True)
    except: continue

# ৫. স্ক্যান বাটন
if st.button("🔍 SCAN MARKET", use_container_width=True):
    all_stocks = []
    sector_perf = []
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
                        drastic = "-"
                        if prices[-2] < prices[-3] < prices[-4]: drastic = "৩ দিন পতন"
                        elif prices[-2] > prices[-3] > prices[-4]: drastic = "৩ দিন উত্থান"
                        
                        # পঙ্কজ স্ট্র্যাটেজি সিগন্যাল
                        sig = "-"
                        if chg >= 2.0 and "পতন" not in drastic: sig = "BUY"
                        elif chg <= -2.0 and "উত্থান" not in drastic: sig = "SELL"
                        
                        stock_data = {
                            "Stock": s.replace(".NS",""), "LTP": ltp, "Chg%": chg,
                            "Signal": sig, 
                            "SL": round(ltp*0.985 if sig=="BUY" else ltp*1.015, 2),
                            "T1": round(ltp*1.01 if sig=="BUY" else ltp*0.99, 2),
                            "T2": round(ltp*1.02 if sig=="BUY" else ltp*0.98, 2),
                            "T3": round(ltp*1.03 if sig=="BUY" else ltp*0.97, 2),
                            "Trend": drastic
                        }
                        all_stocks.append(stock_data)
                        s_chgs.append(chg)
                        if chg > 0: advances += 1
                        else: declines += 1
                except: continue
            if s_chgs:
                sector_perf.append({"Sector": sector, "Avg%": round(sum(s_chgs)/len(s_chgs), 2)})

    # ৬. ল্যাপটপের মতো ৩-কলাম লেআউট
    st.write(f"🟢 Advances: {advances} | 🔴 Declines: {declines}")
    col_left, col_mid, col_right = st.columns([1, 2, 1])

    with col_left:
        st.subheader("🏢 SECTOR PERFORMANCE")
        sec_df = pd.DataFrame(sector_perf).sort_values(by="Avg%", ascending=False)
        st.dataframe(sec_df, hide_index=True, use_container_width=True)

    with col_mid:
        st.subheader("🎯 TRADING SIGNALS")
        sig_df = pd.DataFrame(all_stocks)
        # শুধু যেখানে সিগন্যাল আছে সেগুলোকে হাইলাইট করা
        st.dataframe(sig_df, use_container_width=True, hide_index=True)

    with col_right:
        st.subheader("🔥 GAINERS / LOSERS")
        res_df = pd.DataFrame(all_stocks).sort_values(by="Chg%", ascending=False)
        st.write("**Top 5 Gainers**")
        st.table(res_df[['Stock', 'Chg%']].head(5))
        st.write("**Top 5 Losers**")
        st.table(res_df[['Stock', 'Chg%']].tail(5))
        
        st.subheader("⚠️ DRASTIC WATCH")
        st.table(sig_df[sig_df['Trend'] != "-"][['Stock', 'Trend']])
else:
    st.info("স্ক্যান শুরু করতে উপরের নীল বাটনটি টিপুন।")
