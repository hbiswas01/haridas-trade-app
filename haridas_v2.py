import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime
import pytz

# ১. পেজ সেটআপ
st.set_page_config(layout="wide", page_title="Haridas Pro Master Terminal v38.0")
IST = pytz.timezone('Asia/Kolkata')

st.markdown("""
    <style>
    .main { background-color: #eaedf2; }
    header {visibility: hidden;}
    .stButton>button { background: linear-gradient(to right, #007bff, #00c6ff); color: white; font-weight: bold; width: 100%; border-radius: 8px; height: 3.5em; font-size: 18px; }
    .idx-card { background-color: #f8f9fc; padding: 12px; border-radius: 10px; border: 1px solid #e3e6f0; text-align: center; box-shadow: 2px 2px 5px rgba(0,0,0,0.05); }
    .stat-header { background-color: #4e73df; color: white; padding: 6px; border-radius: 5px; text-align: center; font-weight: bold; margin-bottom: 5px; font-size: 16px; }
    html, body, [class*="css"] { font-size: 17px !important; }
    </style>
    """, unsafe_allow_html=True)

# ২. সেক্টর ম্যাপ
SECTOR_MAP = {
    "NIFTY BANK 🏦": ["HDFCBANK.NS", "ICICIBANK.NS", "SBIN.NS", "KOTAKBANK.NS", "AXISBANK.NS"],
    "NIFTY IT 💻": ["TCS.NS", "INFY.NS", "HCLTECH.NS", "WIPRO.NS", "TECHM.NS"],
    "NIFTY AUTO 🚗": ["TATAMOTORS.NS", "MARUTI.NS", "M&M.NS", "BAJAJ-AUTO.NS", "EICHERMOT.NS"],
    "NIFTY METAL ⚙️": ["TATASTEEL.NS", "JSWSTEEL.NS", "HINDALCO.NS", "VEDL.NS"],
    "NIFTY ENERGY ⚡": ["RELIANCE.NS", "NTPC.NS", "POWERGRID.NS", "ONGC.NS"],
    "NIFTY PHARMA 💊": ["SUNPHARMA.NS", "CIPLA.NS", "DRREDDY.NS", "DIVISLAB.NS"],
    "NIFTY FMCG 🛒": ["ITC.NS", "HINDUNILVR.NS", "NESTLEIND.NS", "BRITANNIA.NS"],
    "NIFTY FIN SRV 💹": ["BAJFINANCE.NS", "BAJAJFINSV.NS", "CHOLAFIN.NS"]
}

# ৩. বাজেট ইনপুট
st.sidebar.markdown("### 💰 Profit & Quantity Settings")
investment = st.sidebar.number_input("আপনার বাজেট (টাকা):", value=100000, step=5000)

# ৪. টপ বার
t_col1, t_col2, t_col3, t_col4 = st.columns([2, 1, 1, 1])
with t_col1:
    st.markdown("<h2 style='color: #0a192f; margin:0;'>📡 HARIDAS NSE TERMINAL</h2>", unsafe_allow_html=True)
with t_col2:
    st.markdown(f"🕒 **LIVE: {datetime.now(IST).strftime('%H:%M:%S')}**")

adv_spot = t_col3.empty()
dec_spot = t_col4.empty()

# ৫. মার্কেট ইনডেক্স
st.write("---
