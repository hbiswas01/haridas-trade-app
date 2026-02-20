import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime
import time

# ১. পেজ সেটআপ এবং প্রিমিয়াম লুক (সবার আগে থাকতে হবে)
st.set_page_config(page_title="Haridas Pro Master Terminal v38.0", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #eaedf2; }
    header {visibility: hidden;}
    /* টপ বার স্টাইলিং */
    .top-bar { 
        background-color: #0a192f; color: #00ffcc; padding: 12px; 
        border-radius: 5px; display: flex; justify-content: space-between; 
        align-items: center; margin-bottom: 10px; font-weight: bold;
    }
    .section-header {
        background-color: #4e73df; color: white; padding: 5px 10px;
        border-radius: 5px 5px 0 0; font-size: 14px; font-weight: bold;
    }
    .adv { color: #00ffcc; margin-right: 15px; }
    .dec { color: #ff4444; }
    /* মেট্রিক বক্স স্টাইলিং */
    div[data-testid="stMetricValue"] { font-size: 1.4rem !important; color: #1a1a1a; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# ২. অটো রিফ্রেশ জাভাস্ক্রিপ্ট (প্রতি ৬০ সেকেন্ডে অটো রিলোড হবে)
st.markdown("<script>setTimeout(function(){ window.location.reload(); }, 60000);</script>", unsafe_allow_html=True)

# ৩. সেক্টর ম্যাপ
SECTOR_MAP = {
    "NIFTY METAL ⚙️": ["HINDALCO.NS", "TATASTEEL.NS", "JSWSTEEL.NS", "VEDL.NS"],
    "NIFTY ENERGY ⚡": ["RELIANCE.NS", "NTPC.NS", "POWERGRID.NS", "ONGC.NS"],
    "NIFTY FMCG 🛒": ["ITC.NS", "HINDUNILVR.NS", "NESTLEIND.NS"],
    "NIFTY BANK 🏦": ["HDFCBANK.NS", "ICICIBANK.NS", "SBIN.NS", "AXISBANK.NS"],
    "NIFTY IT 💻": ["TCS.NS", "INFY.NS", "HCLTECH.NS", "WIPRO.NS"],
    "NIFTY AUTO 🚗": ["TATAMOTORS.NS", "MARUTI.NS", "M&M.NS"],
    "NIFTY PHARMA 💊": ["SUNPHARMA.NS", "CIPLA.NS", "DRREDDY.NS"]
}

# ৪. ডাটা ফেচিং এবং লজিক (সব ফিচার সহ)
all_stocks, sector_summary = [], []
adv, dec = 0, 0

with st.spinner('Scanning Live Market...'):
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
                    
                    # ৩ দিনের ট্রেন্ড চেক
                    is_falling = (p[-2] < p[-3] < p[-4])
                    is_rising = (p[-2] > p[-3] > p[-4])
                    trend = "Normal"
                    if is_falling: trend = "৩ দিন পতন 📉"
                    elif is_rising: trend = "৩ দিন উত্থান 📈"
                    
                    # সিগন্যাল লজিক (Pankaj Strategy)
                    sig = "-"
                    sl, t1, t2, t3 = 0, 0, 0, 0
                    if chg >= 2.0 and not is_falling:
                        sig = "BUY"
                        sl, t1, t2, t3 = round(ltp*0.985, 2), round(ltp*1.01, 2), round(ltp*1.02, 2), round(ltp*1.03, 2)
                    elif chg <= -2.0 and not is_rising:
                        sig = "SELL"
                        sl, t1, t2, t3 = round(ltp*1.015, 2), round(ltp*0.99, 2), round(ltp*0.98, 2), round(ltp*0.97, 2)
                    
                    all_stocks.append({
                        "Stock": s, "LTP": ltp, "Chg%": f"{chg}%", "Signal": sig, 
                        "SL": sl, "T1": t1, "T2": t2, "T3": t3, "Trend": trend,
                        "Time": datetime.now().strftime("%H:%M:%S")
                    })
                    sec_chgs.append(chg)
            except: continue
        if sec_chgs:
            avg_chg = round(sum(sec_chgs)/len(sec_chgs), 2)
            # সেক্টর ট্রেন্ড ভিজ্যুয়াল (█)
            bar = "█" * int(abs(avg_chg) * 5) if abs(avg_chg) > 0 else "▏"
            sector_summary.append({"Sector": sector, "%": f"{avg_chg}%", "Trend": bar})

full_df = pd.DataFrame(all_stocks)

# ৫. প্রিমিয়াম ইউজার ইন্টারফেস (Layout)
st.markdown(f"""
    <div class="top-bar">
        <div style="font-size: 20px;">HARIDAS PRO TERMINAL v38.0</div>
        <div style="color: #ffcc00;">LIVE CLOCK: {datetime.now().strftime('%H:%M:%S')}</div>
        <div>
            <span class="adv">ADVANCES: {adv}</span> <span class="dec">DECLINES: {dec}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

# কলাম বিন্যাস (৩ কলাম লেআউট)
c_left, c_mid, c_right = st.columns([1.3, 3, 1.2])

with c_left:
    st.markdown('<div class="section-header">SECTOR PERFORMANCE</div>', unsafe_allow_html=True)
    if sector_summary:
        st.table(pd.DataFrame(sector_summary))

with c_mid:
    # মার্কেট ইনডেক্স বক্স (অ্যামাউন্ট সহ)
    st.markdown('<div class="section-header">📉 MARKET INDICES</div>', unsafe_allow_html=True)
    i_cols = st.columns(3)
    idx_map = {"SENSEX": "^BSESN", "NIFTY 50": "^NSEI", "NIFTY BANK": "^NSEBANK"}
    for i, (n, s) in enumerate(idx_map.items()):
        try:
            d = yf.Ticker(s).history(period="2d")
            amt = d['Close'].iloc[-1]
            prev = d['Close'].iloc[-2]
            pct = ((amt - prev) / prev) * 100
            i_cols[i].metric(n, f"{amt:,.2f}", f"{pct:.2f}%")
        except: i_cols[i].error("No Sync")

    # ট্রেডিং সিগন্যাল (শুধুমাত্র সিগন্যাল থাকা স্টক দেখাবে)
    st.markdown('<div class="section-header">💹 TRADING SIGNALS (Pankaj Strategy)</div>', unsafe_allow_html=True)
    if not full_df.empty:
        sig_only = full_df[full_df["Signal"] != "-"]
        if not sig_only.empty:
            st.dataframe(sig_only, use_container_width=True, hide_index=True)
        else:
            st.info("No Active Signals at the moment.")

with c_right:
    # রিফ্রেশ বাটন (User Request)
    if st.button('🔄 FORCE REFRESH DATA'):
        st.rerun()

    st.markdown('<div class="section-header">🏆 TOP GAINERS</div>', unsafe_allow_html=True)
    if not full_df.empty:
        st.table(full_df.sort_values("Chg%", ascending=False).head(5)[["Stock", "Chg%"]])
    
    st.markdown('<div class="section-header">🚨 DRASTIC WATCH</div>', unsafe_allow_html=True)
    if not full_df.empty:
        st.table(full_df[full_df["Trend"] != "Normal"][["Stock", "Trend"]].head(5))

# ৬. এক্সপোর্ট বাটন
if not full_df.empty:
    st.download_button("📂 EXPORT EXCEL", full_df.to_csv(index=False).encode('utf-8'), f"Haridas_Trade_{datetime.now().strftime('%d%m_%H%M')}.csv", "text/csv")
