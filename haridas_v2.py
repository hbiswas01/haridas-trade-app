import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(page_title="Haridas Pro Terminal", layout="wide")

st.markdown("<h2 style='text-align: center; color: #007bff;'>🚀 HARIDAS TRADE TERMINAL V2</h2>", unsafe_allow_html=True)

# আপনার পছন্দের স্টক লিস্ট
stocks = ["HDFCBANK.NS", "SBIN.NS", "ICICIBANK.NS", "TATAMOTORS.NS", "RELIANCE.NS", "TCS.NS", "INFY.NS"]

st.write("---")
if st.button("🔍 SCAN MARKET NOW", use_container_width=True):
    with st.spinner('বাজার থেকে লেটেস্ট ডেটা আনছি...'):
        results = []
        for s in stocks:
            try:
                data = yf.Ticker(s).history(period="2d")
                if len(data) >= 2:
                    ltp = round(data['Close'].iloc[-1], 2)
                    prev = data['Close'].iloc[-2]
                    chg = round(((ltp - prev) / prev) * 100, 2)
                    
                    signal = "⚪ WAIT"
                    if chg >= 2.0: signal = "🟢 BUY"
                    elif chg <= -2.0: signal = "🔴 SELL"
                    
                    results.append({"Stock": s.replace(".NS",""), "LTP": ltp, "Change%": f"{chg}%", "Action": signal})
            except: continue
        
        if results:
            st.table(pd.DataFrame(results))
        else:
            st.warning("এই মুহূর্তে ডেটা পাওয়া যাচ্ছে না।")

st.caption("সোমবার সকাল ০৯:১৫-তে বাটনটি টিপুন।")
