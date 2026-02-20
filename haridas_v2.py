import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime
import pytz

# ১. পেজ সেটআপ ও ডিজাইন
st.set_page_config(layout="wide", page_title="Haridas Pro Master Terminal v38.0")

# ইন্ডিয়ান টাইম জোন সেটআপ
IST = pytz.timezone('Asia/Kolkata')

st.markdown("""
    <style>
    .main { background-color: #eaedf2; }
    .stButton>button { background-color: #007bff; color: white; font-weight: bold; width: 100%; border-radius: 5px; height: 3.5em; }
    .idx-card { background-color: #f8f9fc; padding: 10px; border-radius: 10px; border: 1px solid #e3e6f0; text-align: center; }
    .status-up { color: #155724; font-weight: bold; }
    .status-down { color: #721c24; font-weight: bold; }
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

# ৩. টপ বার: টাইটেল ও ঘড়ি
top_c1, top_c2 = st.columns([3, 1])
with top_c1:
    st.markdown("<h2 style='color: #0a192f; margin:0;'>📡 HARIDAS NSE MASTER TERMINAL</h2>", unsafe_allow_html=True)
with top_c2:
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
        pct = round(((ltp - prev)/prev)*100, 2)
        color = "green" if pct >= 0 else "red"
        with idx_cols[i]:
            st.markdown(f"<div class='idx-card'><b>{name}</b><br>{ltp}<br><span style='color:{color};'>{pct}%</span></div>", unsafe_allow_html=True)
    except: continue

# ৫. স্ক্যান বাটন
st.write("---")
if st.button("🔍 SCAN MARKET (ALL FEATURES)", use_container_width=True):
    all_stocks = []
    sector_perf = []
    drastic_watch = []
    advances, declines = 0, 0

    with st.spinner('বাজার বিশ্লেষণ চলছে...'):
        for sector, stocks in SECTOR_MAP.items():
            sector_chgs = []
            for s in stocks:
                try:
                    df = yf.Ticker(s).history(period="7d")
                    if len(df) >= 4:
                        prices = df['Close'].values
                        ltp = round(float(prices[-1]), 2)
                        prev_c = float(prices[-2])
                        change = round(((ltp - prev_c) / prev_c) * 100, 2)
                        
                        # ৩ দিন পতন/উত্থান
                        trend = "-"
                        if prices[-2] < prices[-3] < prices[-4]: trend = " Falling 📉"
                        elif prices[-2] > prices[-3] > prices[-4]: trend = " Rising 📈"
                        
                        if trend != "-": drastic_watch.append({"Stock": s.replace(".NS",""), "Status": trend})

                        # সিগন্যাল লজিক
                        sig = "-"
                        if change >= 2.0 and "Falling" not in trend: sig = "🟢 BUY"
                        elif change <= -2.0 and "Rising" not in trend: sig = "🔴 SELL"
                        
                        all_stocks.append({
                            "Stock": s.replace(".NS",""), "LTP": ltp, "Chg%": change,
                            "Signal": sig, 
                            "SL": round(ltp*0.985 if "BUY" in sig else ltp*1.015, 2),
                            "T1": round(ltp*1.01 if "BUY" in sig else ltp*0.99, 2),
                            "T2": round(ltp*1.02 if "BUY" in sig else ltp*0.98, 2),
                            "Time": datetime.now(IST).strftime('%H:%M:%S'),
                            "Trend": trend
                        })
                        
                        sector_chgs.append(change)
                        if change > 0: advances += 1
                        else: declines += 1
                except: continue
            if sector_chgs:
                sector_perf.append({"Sector": sector, "Avg%": round(sum(sector_chgs)/len(sector_chgs), 2)})

    # ৬. ল্যাপটপের মতো ৩-কলাম আউটপুট (Full Layout)
    st.write(f"✅ Advances: {advances} | ❌ Declines: {declines}")
    c_left, c_mid, c_right = st.columns([1, 2, 1])

    with c_left:
        st.subheader("🏢 Sectors")
        st.dataframe(pd.DataFrame(sector_perf).sort_values(by="Avg%", ascending=False), hide_index=True)
        
        st.subheader("⚠️ Drastic")
        if drastic_watch: st.table(pd.DataFrame(drastic_watch))
        else: st.write("No drastic moves.")

    with c_mid:
        st.subheader("🎯 Active Signals")
        df_all = pd.DataFrame(all_stocks)
        # সব স্টকই দেখাবে আপনার অ্যাপের মতো, শুধু সিগন্যাল হাইলাইট হবে
        st.dataframe(df_all, use_container_width=True, hide_index=True)

    with c_right:
        st.subheader("🔥 Top Movers")
        df_sort = df_all.sort_values(by="Chg%", ascending=False)
        st.markdown("**Gainers**")
        st.table(df_sort[['Stock', 'Chg%']].head(5))
        st.markdown("**Losers**")
        st.table(df_sort[['Stock', 'Chg%']].tail(5))

else:
    st.info("স্ক্যান করতে উপরের বাটনটি টিপুন।")

st.markdown("---")
st.write("হরিদাস ভাই, এটি আপনার ল্যাপটপের সেই Tkinter অ্যাপের হুবহু ওয়েব ভার্সন।")
