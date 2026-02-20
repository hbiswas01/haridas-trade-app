import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime

# ১. পেজ সেটআপ এবং ডার্ক থিম CSS (সবার আগে)
st.set_page_config(page_title="Haridas Pro Master Terminal v38.0", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #eaedf2; }
    header {visibility: hidden;}
    .top-bar { 
        background-color: #0a192f; color: #00ffcc; padding: 15px; 
        border-radius: 5px; display: flex; justify-content: space-between; 
        align-items: center; margin-bottom: 10px; font-weight: bold;
    }
    .section-header {
        background-color: #4e73df; color: white; padding: 5px 10px;
        border-radius: 5px 5px 0 0; font-size: 14px; font-weight: bold;
    }
    .adv { color: #00ffcc; }
    .dec { color: #ff4444; }
    </style>
    """, unsafe_allow_html=True)

# ২. অটো রিফ্রেশ জাভাস্ক্রিপ্ট (প্রতি ৬০ সেকেন্ড)
st.markdown("<script>setTimeout(function(){ window.location.reload(); }, 60000);</script>", unsafe_allow_html=True)

# ৩. সেক্টর ম্যাপ (তোমার ছবি অনুযায়ী)
SECTOR_MAP = {
    "NIFTY METAL ⚙️": ["HINDALCO.NS", "TATASTEEL.NS", "JSWSTEEL.NS", "VEDL.NS"],
    "NIFTY ENERGY ⚡": ["RELIANCE.NS", "NTPC.NS", "POWERGRID.NS", "ONGC.NS"],
    "NIFTY FMCG 🛒": ["ITC.NS", "HINDUNILVR.NS", "BRITANNIA.NS"],
    "NIFTY IT 💻": ["TCS.NS", "INFY.NS", "HCLTECH.NS", "WIPRO.NS", "TECHM.NS"],
    "NIFTY BANK 🏦": ["HDFCBANK.NS", "ICICIBANK.NS", "SBIN.NS", "KOTAKBANK.NS", "AXISBANK.NS"],
    "NIFTY AUTO 🚗": ["TATAMOTORS.NS", "MARUTI.NS", "M&M.NS", "BAJAJ-AUTO.NS"],
    "NIFTY PHARMA 💊": ["SUNPHARMA.NS", "CIPLA.NS", "DRREDDY.NS"],
    "NIFTY INFRA 🏗️": ["LT.NS", "ADANIPORTS.NS", "GRASIM.NS"]
}

# ৪. ডাটা ফেচিং এবং লজিক
all_stocks, sector_summary = [], []
adv, dec = 0, 0

for sector, stocks in SECTOR_MAP.items():
    sec_chgs = []
    for s in stocks:
        try:
            df = yf.Ticker(s).history(period="7d")
            if not df.empty and len(df) >= 4:
                p = df['Close'].values
                ltp, chg = round(p[-1], 2), round(((p[-1]-p[-2])/p[-2])*100, 2)
                if chg > 0: adv += 1
                else: dec += 1
                
                # ৩ দিনের ট্রেন্ড চেক (Drastic Watch)
                trend = "Normal"
                if p[-2] < p[-3] < p[-4]: trend = "৩ দিন পতন 📉"
                elif p[-2] > p[-3] > p[-4]: trend = "৩ দিন উত্থান 📈"
                
                # সিগন্যাল লজিক (শুধু BUY/SELL থাকলে দেখাবে)
                sig = "-"
                sl, t1, t2, t3 = 0, 0, 0, 0
                if chg >= 2.0 and "পতন" not in trend:
                    sig = "BUY"
                    sl, t1, t2, t3 = round(ltp*0.985, 2), round(ltp*1.01, 2), round(ltp*1.02, 2), round(ltp*1.03, 2)
                elif chg <= -2.0 and "উত্থান" not in trend:
                    sig = "SELL"
                    sl, t1, t2, t3 = round(ltp*1.015, 2), round(ltp*0.99, 2), round(ltp*0.98, 2), round(ltp*0.97, 2)
                
                all_stocks.append({
                    "Stock": s, "LTP": ltp, "Chg%": chg, "Signal": sig, 
                    "SL": sl, "T1": t1, "T2": t2, "T3": t3, "Trend": trend
                })
                sec_chgs.append(chg)
        except: continue
    if sec_chgs:
        sector_summary.append({"Sector": sector, "%": round(sum(sec_chgs)/len(sec_chgs), 2)})

full_df = pd.DataFrame(all_stocks)

# ৫. ইউজার ইন্টারফেস (Layout)
st.markdown(f"""
    <div class="top-bar">
        <div style="font-size: 22px;">HARIDAS NSE TERMINAL</div>
        <div style="color: #ffcc00;">LIVE: {datetime.now().strftime('%H:%M:%S')}</div>
        <div>
            <span class="adv">ADVANCES: {adv}</span> | <span class="dec">DECLINES: {dec}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

# কলাম বিন্যাস
col_left, col_mid, col_right = st.columns([1.3, 3, 1.2])

with col_left:
    st.markdown('<div class="section-header">SECTOR PERFORMANCE</div>', unsafe_allow_html=True)
    if sector_summary:
        st.table(pd.DataFrame(sector_summary).sort_values("%", ascending=False))

with col_mid:
    st.markdown('<div class="section-header">📊 MARKET INDICES</div>', unsafe_allow_html=True)
    i_cols = st.columns(3)
    idx = {"NIFTY 50": "^NSEI", "BANK NIFTY": "^NSEBANK", "SENSEX": "^BSESN"}
    for i, (n, s) in enumerate(idx.items()):
        try:
            d = yf.Ticker(s).history(period="2d")
            ltp_idx = d['Close'].iloc[-1]
            chg_idx = ((ltp_idx - d['Close'].iloc[-2]) / d['Close'].iloc[-2]) * 100
            i_cols[i].metric(n, f"{ltp_idx:,.2f}", f"{chg_idx:.2f}%")
        except: pass

    st.markdown('<div class="section-header">💹 TRADING SIGNALS (Pankaj Strategy)</div>', unsafe_allow_html=True)
    if not full_df.empty:
        # শুধুমাত্র সিগন্যাল থাকা স্টকগুলো দেখাবে (তোমার ছবির মতো)
        sig_only = full_df[full_df["Signal"] != "-"]
        st.dataframe(sig_only, use_container_width=True, hide_index=True)

with col_right:
    st.markdown('<div class="section-header">TOP GAINERS</div>', unsafe_allow_html=True)
    if not full_df.empty:
        st.table(full_df.sort_values("Chg%", ascending=False).head(5)[["Stock", "Chg%"]])
    
    st.markdown('<div class="section-header">🚨 DRASTIC WATCH</div>', unsafe_allow_html=True)
    if not full_df.empty:
        st.table(full_df[full_df["Trend"] != "Normal"][["Stock", "Trend"]].head(5))

# ৬. এক্সপোর্ট বাটন
if not full_df.empty:
    st.download_button("📂 EXPORT EXCEL (CSV)", full_df.to_csv(index=False).encode('utf-8'), "Trade_Report.csv", "text/csv")
