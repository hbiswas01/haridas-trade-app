import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime

# ১. পেজ সেটআপ (সবার উপরে থাকতে হবে)
st.set_page_config(page_title="Haridas Pro Terminal v38.0", layout="wide")

# ২. স্ক্রিনশটের মতো ডার্ক থিম এবং রেসপনসিভ CSS
st.markdown("""
    <style>
    .main { background-color: #eaedf2; }
    header {visibility: hidden;}
    /* টপ বার স্টাইলিং */
    .top-bar { background-color: #0a192f; color: #00ffcc; padding: 10px; border-radius: 5px; display: flex; justify-content: space-between; align-items: center; }
    .status-box { color: white; font-weight: bold; padding: 5px 15px; border-radius: 4px; }
    .adv { color: #00ffcc; }
    .dec { color: #ff4444; }
    /* টেবিল এবং কার্ড স্টাইলিং */
    div.stDataFrame, div.stTable { background-color: white; border-radius: 5px; border: 1px solid #ced4da; }
    h3 { color: #004085; font-size: 1.1rem !important; border-bottom: 2px solid #004085; padding-bottom: 5px; }
    </style>
    """, unsafe_allow_html=True)

# ৩. অটো রিফ্রেশ জাভাস্ক্রিপ্ট (প্রতি ৬০ সেকেন্ড)
st.markdown("<script>setTimeout(function(){ window.location.reload(); }, 60000);</script>", unsafe_allow_html=True)

# ৪. ডাটা সোর্স (SECTOR_MAP)
SECTOR_MAP = {
    "NIFTY METAL ⚙️": ["HINDALCO.NS", "TATASTEEL.NS", "JSWSTEEL.NS", "VEDL.NS"],
    "NIFTY ENERGY ⚡": ["RELIANCE.NS", "NTPC.NS", "POWERGRID.NS", "ONGC.NS"],
    "NIFTY IT 💻": ["TCS.NS", "INFY.NS", "HCLTECH.NS", "WIPRO.NS", "TECHM.NS"],
    "NIFTY BANK 🏦": ["HDFCBANK.NS", "ICICIBANK.NS", "SBIN.NS", "KOTAKBANK.NS", "AXISBANK.NS"],
    "NIFTY FMCG 🛒": ["ITC.NS", "HINDUNILVR.NS", "NESTLEIND.NS", "BRITANNIA.NS"],
    "NIFTY INFRA 🏗️": ["LT.NS", "ADANIPORTS.NS", "GRASIM.NS", "AMBUJACEM.NS"],
    "NIFTY PHARMA 💊": ["SUNPHARMA.NS", "CIPLA.NS", "DRREDDY.NS", "DIVISLAB.NS"],
    "NIFTY REALTY 🏢": ["DLF.NS", "GODREJPROP.NS", "OBEROIRLTY.NS", "PRESTIGE.NS"],
    "NIFTY FIN SRV 💹": ["BAJFINANCE.NS", "BAJAJFINSV.NS", "CHOLAFIN.NS"]
}

# ৫. ডাটা প্রসেসিং লজিক
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
                
                trend = "Normal"
                if p[-2] < p[-3] < p[-4]: trend = "৩ দিন পতন 📉"
                elif p[-2] > p[-3] > p[-4]: trend = "৩ দিন উত্থান 📈"
                
                sig, sl, t1, t2, t3 = "-", 0, 0, 0, 0
                if chg >= 2.0 and "পতন" not in trend:
                    sig = "BUY"
                    sl, t1, t2, t3 = round(ltp*0.985, 2), round(ltp*1.01, 2), round(ltp*1.02, 2), round(ltp*1.03, 2)
                elif chg <= -2.0 and "উত্থান" not in trend:
                    sig = "SELL"
                    sl, t1, t2, t3 = round(ltp*1.015, 2), round(ltp*0.99, 2), round(ltp*0.98, 2), round(ltp*0.97, 2)
                
                all_stocks.append({
                    "Stock": s, "LTP": ltp, "Chg%": chg, "Signal": sig, 
                    "SL": sl, "T1": t1, "T2": t2, "T3": t3, "Trend": trend, "Time": datetime.now().strftime("%H:%M")
                })
                sec_chgs.append(chg)
        except: continue
    if sec_chgs:
        sector_summary.append({"Sector": sector, "%": round(sum(sec_chgs)/len(sec_chgs), 2)})

df_final = pd.DataFrame(all_stocks)

# ৬. ইউজার ইন্টারফেস (Layout)
# টপ বার
st.markdown(f"""
    <div class="top-bar">
        <div style="font-size: 20px;">HARIDAS NSE TERMINAL</div>
        <div style="color: #ffcc00;">LIVE: {datetime.now().strftime('%H:%M:%S')}</div>
        <div>
            <span class="adv">ADVANCES: {adv}</span> | 
            <span class="dec">DECLINES: {dec}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

st.write("")

# মেইন লেআউট: ৩টি কলাম (স্ক্রিনশটের মতো)
col_left, col_mid, col_right = st.columns([1.2, 3, 1.2])

with col_left:
    st.subheader("SECTOR PERFORMANCE")
    if sector_summary:
        sec_df = pd.DataFrame(sector_summary).sort_values("%", ascending=False)
        st.table(sec_df)

with col_mid:
    st.subheader("📊 MARKET INDICES")
    idx_cols = st.columns(3)
    indices = {"NIFTY 50": "^NSEI", "BANK NIFTY": "^NSEBANK", "NIFTY IT": "^CNXIT"}
    for i, (n, s) in enumerate(indices.items()):
        try:
            d = yf.Ticker(s).history(period="2d")
            v, c = round(d['Close'].iloc[-1], 2), round(((d['Close'].iloc[-1]-d['Close'].iloc[-2])/d['Close'].iloc[-2])*100, 2)
            idx_cols[i].metric(n, f"₹{v}", f"{c}%")
        except: pass

    st.subheader("💹 TRADING SIGNALS (Pankaj Strategy)")
    if not df_final.empty:
        # শুধু BUY/SELL সিগন্যালগুলো হাইলাইট করা
        def highlight_sig(val):
            if val == 'BUY': return 'background-color: #d4edda; color: #155724; font-weight: bold'
            if val == 'SELL': return 'background-color: #f8d7da; color: #721c24; font-weight: bold'
            return ''
        st.dataframe(df_final.style.applymap(highlight_sig, subset=['Signal']), use_container_width=True, hide_index=True)

with col_right:
    st.subheader("TOP GAINERS")
    if not df_final.empty:
        st.table(df_final.sort_values("Chg%", ascending=False).head(5)[["Stock", "Chg%"]])
    
    st.subheader("TOP LOSERS")
    if not df_final.empty:
        st.table(df_final.sort_values("Chg%").head(5)[["Stock", "Chg%"]])
    
    st.subheader("DRASTIC WATCH")
    if not df_final.empty:
        drastic = df_final[df_final["Trend"] != "Normal"][["Stock", "Trend"]]
        st.table(drastic.head(5))

# ডাউনলোড এবং রিফ্রেশ বাটন
st.divider()
if not df_final.empty:
    st.download_button("📤 EXCEL EXPORT", df_final.to_csv(index=False).encode('utf-8'), f"Trade_{datetime.now().strftime('%d%m_%H%M')}.csv", "text/csv")
