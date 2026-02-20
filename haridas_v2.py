import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime

# ১. পেজ কনফিগারেশন
st.set_page_config(page_title="Haridas Premium Terminal", layout="wide")

# ২. প্রিমিয়াম ডার্ক থিম ও রেসপনসিভ CSS
st.markdown("""
    <style>
    /* মেইন ব্যাকগ্রাউন্ড */
    .main { background-color: #f0f2f6; }
    header {visibility: hidden;}
    
    /* টপ বার প্রিমিয়াম লুক */
    .top-bar { 
        background: linear-gradient(90deg, #0a192f 0%, #112240 100%); 
        color: #00ffcc; 
        padding: 15px; 
        border-radius: 8px; 
        display: flex; 
        justify-content: space-between; 
        align-items: center;
        box-shadow: 0px 4px 10px rgba(0,0,0,0.3);
        margin-bottom: 20px;
    }
    
    /* মেট্রিক কার্ড ডিজাইন */
    div[data-testid="stMetric"] {
        background-color: #ffffff;
        border: 1px solid #e3e6f0;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.05);
    }
    
    /* সেকশন হেডার */
    .section-header {
        background-color: #4e73df;
        color: white;
        padding: 8px 15px;
        border-radius: 5px 5px 0 0;
        font-size: 14px;
        font-weight: bold;
        margin-top: 10px;
    }
    
    /* টেবিল স্টাইলিং */
    .stDataFrame { border-radius: 0 0 5px 5px; }
    </style>
    """, unsafe_allow_html=True)

# ৩. অটো রিফ্রেশ (৬০ সেকেন্ড)
st.markdown("<script>setTimeout(function(){ window.location.reload(); }, 60000);</script>", unsafe_allow_html=True)

# ৪. ডাটা সোর্স (SECTOR_MAP)
SECTOR_MAP = {
    "NIFTY BANK 🏦": ["HDFCBANK.NS", "ICICIBANK.NS", "SBIN.NS", "KOTAKBANK.NS", "AXISBANK.NS"],
    "NIFTY IT 💻": ["TCS.NS", "INFY.NS", "HCLTECH.NS", "WIPRO.NS", "TECHM.NS"],
    "NIFTY METAL ⚙️": ["HINDALCO.NS", "TATASTEEL.NS", "JSWSTEEL.NS", "VEDL.NS"],
    "NIFTY AUTO 🚗": ["TATAMOTORS.NS", "MARUTI.NS", "M&M.NS", "BAJAJ-AUTO.NS"],
    "NIFTY ENERGY ⚡": ["RELIANCE.NS", "NTPC.NS", "POWERGRID.NS", "ONGC.NS"],
    "NIFTY FIN SRV 💹": ["BAJFINANCE.NS", "BAJAJFINSV.NS", "CHOLAFIN.NS"]
}

# ৫. ডাটা প্রসেসিং
all_stocks, sector_summary = [], []
adv, dec = 0, 0

with st.spinner('Fetching Premium Data...'):
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
                        "SL": sl, "T1": t1, "T2": t2, "T3": t3, "Trend": trend
                    })
                    sec_chgs.append(chg)
            except: continue
        if sec_chgs:
            sector_summary.append({"Sector": sector, "%": round(sum(sec_chgs)/len(sec_chgs), 2)})

df_final = pd.DataFrame(all_stocks)

# ৬. প্রিমিয়াম ইউজার ইন্টারফেস
st.markdown(f"""
    <div class="top-bar">
        <div style="font-size: 22px; letter-spacing: 1px;">HARIDAS NSE TERMINAL</div>
        <div style="color: #ffcc00; font-family: monospace;">LIVE: {datetime.now().strftime('%H:%M:%S')}</div>
        <div style="font-size: 16px;">
            <span style="color: #00ffcc;">ADVANCES: {adv}</span> | 
            <span style="color: #ff4444;">DECLINES: {dec}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

# লেআউট ৩ কলামে ভাগ করা
c_left, c_mid, c_right = st.columns([1.3, 3, 1.3])

with c_left:
    st.markdown('<div class="section-header">SECTOR PERFORMANCE</div>', unsafe_allow_html=True)
    if sector_summary:
        st.table(pd.DataFrame(sector_summary).sort_values("%", ascending=False))

with c_mid:
    st.markdown('<div class="section-header">📊 MARKET INDICES</div>', unsafe_allow_html=True)
    i_cols = st.columns(3)
    # সঠিক সিম্বল যাতে অ্যামাউন্ট দেখা যায়
    indices = {"NIFTY 50": "^NSEI", "BANK NIFTY": "^NSEBANK", "SENSEX": "^BSESN"}
    for i, (n, s) in enumerate(indices.items()):
        try:
            d = yf.Ticker(s).history(period="2d")
            # অ্যামাউন্ট বা LTP ফেচ করা
            val = round(d['Close'].iloc[-1], 2)
            prev = d['Close'].iloc[-2]
            change = round(((val - prev) / prev) * 100, 2)
            i_cols[i].metric(n, f"{val:,.2f}", f"{change}%")
        except: i_cols[i].error("No Sync")

    st.markdown('<div class="section-header">💹 TRADING SIGNALS (Pankaj Strategy)</div>', unsafe_allow_html=True)
    if not df_final.empty:
        def highlight_sig(val):
            if val == 'BUY': return 'background-color: #d4edda; color: #155724; font-weight: bold'
            if val == 'SELL': return 'background-color: #f8d7da; color: #721c24; font-weight: bold'
            return ''
        st.dataframe(df_final.style.applymap(highlight_sig, subset=['Signal']), use_container_width=True, hide_index=True)

with c_right:
    st.markdown('<div class="section-header">TOP GAINERS</div>', unsafe_allow_html=True)
    if not df_final.empty:
        st.table(df_final.sort_values("Chg%", ascending=False).head(5)[["Stock", "Chg%"]])
    
    st.markdown('<div class="section-header">🚨 DRASTIC WATCH</div>', unsafe_allow_html=True)
    if not df_final.empty:
        st.table(df_final[df_final["Trend"] != "Normal"][["Stock", "Trend"]].head(5))

# রিফ্রেশ বাটন
if st.button('FORCE SYNC DATA'):
    st.rerun()
