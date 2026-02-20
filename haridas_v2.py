import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime

# Page configuration
st.set_page_config(page_title="Haridas Trade App", layout="wide")

st.title("🚀 Haridas Pro Master Terminal v2")
st.write(f"Live Market Analysis - {datetime.now().strftime('%H:%M:%S')}")

# Sector Data
SECTOR_MAP = {
    "NIFTY BANK 🏦": ["HDFCBANK.NS", "ICICIBANK.NS", "SBIN.NS", "KOTAKBANK.NS", "AXISBANK.NS"],
    "NIFTY IT 💻": ["TCS.NS", "INFY.NS", "HCLTECH.NS", "WIPRO.NS", "TECHM.NS"],
    "NIFTY AUTO 🚗": ["TATAMOTORS.NS", "MARUTI.NS", "M&M.NS", "BAJAJ-AUTO.NS", "EICHERMOT.NS"]
}

if st.button('SCAN MARKET'):
    all_data = []
    
    with st.spinner('Fetching Data from NSE...'):
        for sector, stocks in SECTOR_MAP.items():
            for stock in stocks:
                try:
                    df = yf.Ticker(stock).history(period="5d")
                    if not df.empty:
                        ltp = round(df['Close'].iloc[-1], 2)
                        prev_close = df['Close'].iloc[-2]
                        chg = round(((ltp - prev_close) / prev_close) * 100, 2)
                        
                        # 3-Day Trend Logic
                        is_falling = (df['Close'].iloc[-2] < df['Close'].iloc[-3] < df['Close'].iloc[-4])
                        is_rising = (df['Close'].iloc[-2] > df['Close'].iloc[-3] > df['Close'].iloc[-4])
                        
                        status = "Normal"
                        if is_falling: status = "৩ দিন পতন 📉"
                        elif is_rising: status = "৩ দিন উত্থান 📈"
                        
                        signal = "-"
                        if chg >= 2.0 and not is_falling: signal = "BUY"
                        elif chg <= -2.0 and not is_rising: signal = "SELL"
                        
                        all_data.append([stock, sector, ltp, f"{chg}%", status, signal])
                except:
                    continue

    # Create DataFrame
    res_df = pd.DataFrame(all_data, columns=["Stock", "Sector", "LTP", "Change%", "3-Day Trend", "Signal"])
    
    # Show Results in Table
    st.table(res_df)
    
    # Download Button
    csv = res_df.to_csv(index=False).encode('utf-8')
    st.download_button("Download Report", csv, "haridas_report.csv", "text/csv")
