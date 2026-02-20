import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime

# --- ১. পেজ সেটআপ (সবার আগে থাকতে হবে) ---
st.set_page_config(
    page_title="Haridas Pro Terminal",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- ২. মোবাইল রেসপনসিভ CSS ---
st.markdown("""
    <style>
    .main { background-color: #eaedf2; }
    div[data-testid="stMetricValue"] { font-size: 1.8rem; font-weight: bold; }
    .stDataFrame { width: 100%; }
    /* মোবাইল স্ক্রিনে টেবিল ফন্ট ঠিক করার জন্য */
    @media (max-width: 600px) {
        div[data-testid="stMetricValue"] { font-size: 1.2rem; }
    }
    </style>
    """, unsafe_allow_html=True)

# --- ৩. সেক্টর ম্যাপ ---
SECTOR_MAP = {
    "BANK 🏦": ["HDFCBANK.NS", "ICICIBANK.NS", "SBIN.NS", "KOTAKBANK.NS", "AXISBANK.NS"],
    "IT 💻": ["TCS.NS", "INFY.NS", "HCLTECH.NS", "WIPRO.NS", "TECHM.NS"],
    "AUTO 🚗": ["TATAMOTORS.NS", "MARUTI.NS", "M&M.NS", "BAJAJ-AUTO.NS", "EICHERMOT.NS"],
    "METAL ⚙️": ["TATASTEEL.NS", "JSWSTEEL.NS", "HINDALCO.NS", "VEDL.NS"],
    "ENERGY ⚡": ["RELIANCE.NS", "NTPC.NS", "POWERGRID.NS", "ONGC.NS"],
    "PHARMA 💊": ["SUNPHARMA.NS", "CIPLA.NS", "DRREDDY.NS", "DIVISLAB.NS"],
    "FMCG 🛒": ["ITC.NS", "HINDUNILVR.NS", "NESTLEIND.NS", "BRITANNIA.NS"],
    "FIN 💹": ["BAJFINANCE.NS", "BAJAJFINSV.NS", "CHOLAFIN.NS"]
}

# --- ৪. অটো রিফ্রেশ স্ক্রিপ্ট (১ মিনিট পর পর) ---
st.markdown("""
    <script>
    setTimeout(function(){ window.location.reload(); }, 60000);
    </script>
    """, unsafe_allow_html=True)

# --- ৫. হেডার ---
c1, c2 = st.columns([3, 1])
with c1:
    st.title("📟 HARIDAS NSE TERMINAL v38.0")
with c2:
    st.write(f"🕒 **LIVE:** {datetime.now().strftime('%H:%M:%S')}")
    if st.button('🔄 REFRESH'):
        st.rerun()

# --- ৬. মার্কেট ইনডেক্স ---
st.subheader("📊 Market Indices")
indices = {"NIFTY 50": "^NSEI", "BANK NIFTY": "^NSEBANK", "SENSEX": "^BSESN"}
idx_cols = st.columns(len(indices))

for i, (name, sym) in enumerate(indices.items()):
    try:
        data = yf.Ticker(sym).history(period="2d")
        if not data.empty:
            ltp = round(data['Close'].iloc[-1], 2)
            prev = data['Close'].iloc[-2]
            chg = round(((ltp - prev) / prev) * 100, 2)
            idx_cols[i].metric(label=name, value=f"₹{ltp}", delta=f"{chg}%")
    except:
        idx_cols[i].error("No Data")

st.divider()

# --- ৭. মেইন ডেটা ফেচিং লজিক ---
all_stocks = []
sector_summary = []
adv, dec = 0, 0

with st.spinner('Scanning NSE Market...'):
    for sector, stocks in SECTOR_MAP.items():
        sec_chgs = []
        for s in stocks:
            try:
                df = yf.Ticker(s).history(period="7d")
                if len(df) >= 4:
                    prices = df['Close'].values
                    ltp = round(prices[-1], 2)
                    chg = round(((ltp - prices[-2]) / prices[-2]) * 100, 2)
                    
                    if chg > 0: adv += 1
                    else: dec += 1
                    
                    # ৩ দিন পতন/উত্থান চেক
                    is_falling = (prices[-2] < prices[-3] < prices[-4])
                    is_rising = (prices[-2] > prices[-3] > prices[-4])
                    trend = "Normal"
                    if is_falling: trend = "৩ দিন পতন 📉"
                    elif is_rising: trend = "৩ দিন উত্থান 📈"
                    
                    # সিগন্যাল লজিক
                    signal = "-"
                    sl, t1, t3 = 0, 0, 0
                    if chg >= 2.0 and not is_falling: 
                        signal = "BUY"
                        sl, t1, t3 = round(ltp*0.985, 2), round(ltp*1.01, 2), round(ltp*1.03, 2)
                    elif chg <= -2.0 and not is_rising: 
                        signal = "SELL"
                        sl, t1, t3 = round(ltp*1.015, 2), round(ltp*0.99, 2), round(ltp*0.97, 2)
                    
                    all_stocks.append({
                        "Stock": s, "LTP": ltp, "Chg%": chg, 
                        "Signal": signal, "SL": sl, "T1": t1, "T3": t3, 
                        "Trend": trend, "Sector": sector
                    })
                    sec_chgs.append(chg)
            except: continue
        
        if sec_chgs:
            sector_summary.append({"Sector": sector, "Avg%": round(sum(sec_chgs)/len(sec_chgs), 2)})

# --- ৮. ডিসপ্লে সেকশন ---
st.write(f"✅ **Advances:** {adv} | ❌ **Declines:** {dec}")

st.subheader("💹 Trading Signals (Pankaj Strategy)")
if all_stocks:
    df_final = pd.DataFrame(all_stocks)
    
    # সিগন্যাল হাইলাইট করার ফাংশন
    def style_signals(row):
        color = ''
        if row.Signal == 'BUY': color = 'background-color: #d4edda; color: #155724'
        elif row.Signal == 'SELL': color = 'background-color: #f8d7da; color: #721c24'
        return [color if col == 'Signal' else '' for col in row.index]

    st.dataframe(df_final.style.apply(style_signals, axis=1), use_container_width=True, hide_index=True)

# --- ৯. ডাস্টিক ওয়াচ ও এক্সপোর্ট ---
st.divider()
k1, k2 = st.columns(2)
with k1:
    st.subheader("🏢 Sector Performance")
    st.table(pd.DataFrame(sector_summary).sort_values(by="Avg%", ascending=False))
with k2:
    st.subheader("⚠️ Drastic Watch")
    st.table(df_final[df_final["Trend"] != "Normal"][["Stock", "Trend"]])

# এক্সেল ডাউনলোড
csv = df_final.to_csv(index=False).encode('utf-8')
st.download_button("📂 Download Today's Report", csv, "haridas_trade.csv", "text/csv")
