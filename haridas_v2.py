import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime

# ১. পেজ সেটআপ (সবার আগে)
st.set_page_config(page_title="Haridas Pro Master Terminal v38.0", layout="wide")

# ২. প্রিমিয়াম ডার্ক থিম ও রেসপনসিভ CSS
st.markdown("""
    <style>
    .main { background-color: #eaedf2; }
    header {visibility: hidden;}
    .top-bar { 
        background-color: #0a192f; color: #00ffcc; padding: 12px; 
        border-radius: 5px; display: flex; justify-content: space-between; 
        align-items: center; margin-bottom: 15px; font-weight: bold;
    }
    .section-header {
        background-color: #4e73df; color: white; padding: 5px 10px;
        border-radius: 5px 5px 0 0; font-size: 14px; font-weight: bold;
    }
    .adv { color: #00ffcc; font-size: 16px; margin-right: 20px; }
    .dec { color: #ff4444; font-size: 16px; }
    /* মেট্রিক বক্স স্টাইলিং */
    div[data-testid="stMetricValue"] { font-size: 1.5rem !important; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# ৩. অটো রিফ্রেশ জাভাস্ক্রিপ্ট (৬০ সেকেন্ড)
st.markdown("<script>setTimeout(function(){ window.location.reload(); }, 60000);</script>", unsafe_allow_html=True)

# ৪. সেক্টর ম্যাপ (Updated)
SECTOR_MAP = {
    "NIFTY METAL ⚙️": ["HINDALCO.NS", "TATASTEEL.NS", "JSWSTEEL.NS", "VEDL.NS"],
    "NIFTY ENERGY ⚡": ["RELIANCE.NS", "NTPC.NS", "POWERGRID.NS", "ONGC.NS"],
    "NIFTY FMCG 🛒": ["ITC.NS", "HINDUNILVR.NS", "NESTLEIND.NS"],
    "NIFTY BANK 🏦": ["HDFCBANK.NS", "ICICIBANK.NS", "SBIN.NS", "AXISBANK.NS"],
    "NIFTY IT 💻": ["TCS.NS", "INFY.NS", "HCLTECH.NS", "WIPRO.NS"],
    "NIFTY AUTO 🚗": ["TATAMOTORS.NS", "MARUTI.NS", "M&M.NS"],
    "NIFTY FIN SRV 💹": ["BAJFINANCE.NS", "BAJAJFINSV.NS", "CHOLAFIN.NS"]
}

# ৫. ডাটা প্রসেসিং লজিক
all_stocks, sector_summary = [], []
adv, dec = 0, 0

with st.spinner('Scanning Premium Market Data...'):
    for sector, stocks in SECTOR_MAP.items():
        sec_chgs = []
        for s in stocks:
            try:
                df = yf.Ticker(s).history(period="7d")
                if not df.empty and len(df) >= 4:
                    prices = df['Close'].values
                    ltp, chg = round(prices[-1], 2), round(((prices[-1]-prices[-2])/prices[-2])*100, 2)
                    if chg > 0: adv += 1
                    else: dec += 1
                    
                    # ৩ দিনের ট্রেন্ড লজিক
                    is_falling = (prices[-2] < prices[-3] < prices[-4])
                    is_rising = (prices[-2] > prices[-3] > prices[-4])
                    trend = "Normal"
                    if is_falling: trend = "৩ দিন পতন 📉"
                    elif is_rising: trend = "৩ দিন উত্থান 📈"
                    
                    # পঙ্কজ স্ট্রেটেজি সিগন্যাল
                    sig, sl, t1, t2, t3 = "-", 0, 0, 0, 0
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
            sector_summary.append({"Sector": sector, "%": f"{avg_chg}%", "chg_val": avg_chg})

full_df = pd.DataFrame(all_stocks)

# ৬. ইউজার ইন্টারফেস (Layout)
st.markdown(f"""
    <div class="top-bar">
        <div style="font-size: 20px;">HARIDAS NSE TERMINAL</div>
        <div style="color: #ffcc00;">LIVE: {datetime.now().strftime('%H:%M:%S')}</div>
        <div>
            <span class="adv">ADVANCES: {adv}</span> <span class="dec">DECLINES: {dec}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

c_left, c_mid, c_right = st.columns([1.3, 3, 1.2])

with c_left:
    st.markdown('<div class="section-header">SECTOR PERFORMANCE</div>', unsafe_allow_html=True)
    if sector_summary:
        for item in sorted(sector_summary, key=lambda x: x['chg_val'], reverse=True):
            color = "#155724" if item['chg_val'] > 0 else "#721c24"
            bar = "█" * int(abs(item['chg_val']) * 5) if abs(item['chg_val']) > 0 else "▏"
            st.markdown(f"**{item['Sector']}** {item['%']}  \n<span style='color:{color}; font-size:20px;'>{bar}</span>", unsafe_allow_html=True)

with c_mid:
    # মার্কেট ইনডেক্স বক্স (অ্যামাউন্ট এবং গেইন/লস ফিক্সড)
    st.markdown('<div class="section-header">📊 MARKET INDICES</div>', unsafe_allow_html=True)
    i_cols = st.columns(3)
    idx_map = {"SENSEX": "^BSESN", "NIFTY 50": "^NSEI", "BANK NIFTY": "^NSEBANK"}
    for i, (n, s) in enumerate(idx_map.items()):
        try:
            d = yf.Ticker(s).history(period="2d")
            amt, prev = d['Close'].iloc[-1], d['Close'].iloc[-2]
            diff = amt - prev
            pct = (diff / prev) * 100
            i_cols[i].metric(n, f"{amt:,.2f}", f"{diff:+.2f} ({pct:+.2f}%)")
        except: i_cols[i].error("No Sync")

    # ট্রেডিং সিগন্যাল (শুধুমাত্র সিগন্যাল থাকলে দেখাবে)
    st.markdown('<div class="section-header">💹 TRADING SIGNALS (Pankaj Strategy)</div>', unsafe_allow_html=True)
    if not full_df.empty:
        sig_only = full_df[full_df["Signal"] != "-"]
        if not sig_only.empty:
            st.dataframe(sig_only, use_container_width=True, hide_index=True)
        else:
            st.info("No Active Signals.")

with c_right:
    if st.button('🔄 FORCE SYNC'): st.rerun()
    
    st.markdown('<div class="section-header">🏆 TOP GAINERS</div>', unsafe_allow_html=True)
    if not full_df.empty:
        st.table(full_df.sort_values("Chg%", ascending=False).head(5)[["Stock", "Chg%"]])
    
    st.markdown('<div class="section-header">🚨 DRASTIC WATCH</div>', unsafe_allow_html=True)
    if not full_df.empty:
        st.table(full_df[full_df["Trend"] != "Normal"][["Stock", "Trend"]].head(5))

# ডাউনলোড বাটন
if not full_df.empty:
    st.download_button("📂 EXPORT EXCEL", full_df.to_csv(index=False).encode('utf-8'), f"Haridas_Trade_{datetime.now().strftime('%d%m_%H%M')}.csv", "text/csv")
