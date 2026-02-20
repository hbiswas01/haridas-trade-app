import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime

# ১. পেজ কনফিগারেশন (এটি সবার উপরে থাকতে হবে)
st.set_page_config(page_title="Haridas Terminal", layout="wide")

# ২. অটো রিফ্রেশ করার জন্য জাভাস্ক্রিপ্ট (প্রতি ৬০ সেকেন্ড)
st.markdown("""
    <script>
    setTimeout(function(){ window.location.reload(); }, 60000);
    </script>
    """, unsafe_allow_html=True)

st.title("📟 HARIDAS NSE TERMINAL v2")
st.write(f"সর্বশেষ আপডেট: {datetime.now().strftime('%H:%M:%S')}")

# ৩. সেক্টর ডাটা
SECTOR_MAP = {
    "BANK 🏦": ["HDFCBANK.NS", "ICICIBANK.NS", "SBIN.NS", "KOTAKBANK.NS", "AXISBANK.NS"],
    "IT 💻": ["TCS.NS", "INFY.NS", "HCLTECH.NS", "WIPRO.NS", "TECHM.NS"],
    "AUTO 🚗": ["TATAMOTORS.NS", "MARUTI.NS", "M&M.NS", "BAJAJ-AUTO.NS", "EICHERMOT.NS"],
    "METAL ⚙️": ["TATASTEEL.NS", "JSWSTEEL.NS", "HINDALCO.NS", "VEDL.NS"],
    "ENERGY ⚡": ["RELIANCE.NS", "NTPC.NS", "POWERGRID.NS", "ONGC.NS"],
    "FIN 💹": ["BAJFINANCE.NS", "BAJAJFINSV.NS", "CHOLAFIN.NS"]
}

# ৪. ইনডেক্স ডাটা (Nifty, BankNifty)
indices = {"NIFTY 50": "^NSEI", "BANK NIFTY": "^NSEBANK"}
idx_cols = st.columns(len(indices))

for i, (name, sym) in enumerate(indices.items()):
    try:
        idx_data = yf.Ticker(sym).history(period="2d")
        ltp = round(idx_data['Close'].iloc[-1], 2)
        prev = idx_data['Close'].iloc[-2]
        chg = round(((ltp - prev) / prev) * 100, 2)
        idx_cols[i].metric(name, f"₹{ltp}", f"{chg}%")
    except:
        idx_cols[i].error(f"{name} unavailable")

st.divider()

# ৫. মেইন ক্যালকুলেশন
all_stocks = []
with st.spinner('ডাটা লোড হচ্ছে...'):
    for sector, stocks in SECTOR_MAP.items():
        for s in stocks:
            try:
                df = yf.Ticker(s).history(period="5d")
                if len(df) >= 4:
                    p = df['Close'].values
                    ltp, chg = round(p[-1], 2), round(((p[-1]-p[-2])/p[-2])*100, 2)
                    
                    # ৩ দিনের ট্রেন্ড লজিক
                    is_falling = (p[-2] < p[-3] < p[-4])
                    is_rising = (p[-2] > p[-3] > p[-4])
                    trend = "Normal"
                    if is_falling: trend = "৩ দিন পতন 📉"
                    elif is_rising: trend = "৩ দিন উত্থান 📈"
                    
                    # সিগন্যাল ও টার্গেট
                    signal = "-"
                    sl, t1 = 0, 0
                    if chg >= 2.0 and not is_falling:
                        signal = "BUY"
                        sl, t1 = round(ltp*0.985, 2), round(ltp*1.02, 2)
                    elif chg <= -2.0 and not is_rising:
                        signal = "SELL"
                        sl, t1 = round(ltp*1.015, 2), round(ltp*0.98, 2)
                    
                    all_stocks.append([s, ltp, chg, signal, sl, t1, trend, sector])
            except: continue

# ৬. ডাটা প্রদর্শন (টেবিল আকারে)
if all_stocks:
    final_df = pd.DataFrame(all_stocks, columns=["Stock", "LTP", "Chg%", "Signal", "SL", "T1", "Trend", "Sector"])
    
    # সিগন্যাল অনুযায়ী হাইলাইট (সহজ পদ্ধতি)
    def color_rows(val):
        if val == "BUY": return 'color: green; font-weight: bold'
        if val == "SELL": return 'color: red; font-weight: bold'
        return ''

    st.subheader("💹 Trading Signals")
    # স্টাইলিং এরর এড়াতে সরাসরি dataframe ব্যবহার করছি
    st.dataframe(final_df.style.map(color_rows, subset=['Signal']), use_container_width=True)

    # ডাস্টিক ওয়াচ (৩ দিন টানা বাড়ছে/কমছে)
    st.subheader("⚠️ Drastic Watch")
    drastic_df = final_df[final_df["Trend"] != "Normal"]
    st.table(drastic_df[["Stock", "Trend", "Sector"]])

    # এক্সেল ডাউনলোড বাটন
    csv = final_df.to_csv(index=False).encode('utf-8')
    st.download_button("📂 Download Report", csv, "haridas_report.csv", "text/csv")
else:
    st.warning("কোনো ডাটা পাওয়া যায়নি। রিফ্রেশ করুন।")
