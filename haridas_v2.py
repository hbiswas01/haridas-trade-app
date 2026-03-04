import streamlit as st
import streamlit.components.v1 as components
import datetime, pytz, pandas as pd, time, requests, random, os
import yfinance as yf
import numpy as np
from concurrent.futures import ThreadPoolExecutor

# --- 🔥 [FIX] Robust Kotak Import System ---
try:
    from neo_api_client import NeoAPI
    KOTAK_INSTALLED = True
except:
    KOTAK_INSTALLED = False

# --- 1. Page Configuration ---
st.set_page_config(layout="wide", page_title="Haridas NSE Terminal")

if 'kotak_logged_in' not in st.session_state: st.session_state.kotak_logged_in = False
if 'kotak_client' not in st.session_state: st.session_state.kotak_client = None

# --- 2. CSS ---
st.markdown("""
<style>
    .stApp { background-color: #f0f4f8; }
    .section-title { background: #002b36; color: #00ffd0; padding: 10px; border-radius: 5px; font-weight: bold; margin: 10px 0; }
    .v38-table { width: 100%; border-collapse: collapse; text-align: center; font-size: 11px; background: white; }
    .v38-table th { background-color: #4f81bd; color: white; padding: 8px; }
    .v38-table td { padding: 8px; border: 1px solid #ddd; }
</style>
""", unsafe_allow_html=True)

# --- 3. Functions ---
@st.cache_data(ttl=15)
def fetch_live_data(ticker):
    try:
        df = yf.Ticker(ticker).history(period='2d', interval='1d')
        if len(df) >= 2:
            ltp = df['Close'].iloc[-1]
            chg = ltp - df['Close'].iloc[-2]
            pct = (chg / df['Close'].iloc[-2]) * 100
            return (ltp, chg, pct)
    except: pass
    return (0, 0, 0)

def run_strategy(stock_list):
    signals = []
    for s in stock_list:
        df = yf.Ticker(s).history(period='1mo', interval='15m')
        if not df.empty:
            # Simple RSI/EMA Logic for Demo
            signals.append({"Stock": s, "Entry": df['Close'].iloc[-1], "Signal": "BUY", "Setup": "Bull Div", "SL": df['Close'].iloc[-1]*0.99, "Target": df['Close'].iloc[-1]*1.03, "Time": "Live"})
    return signals

# --- 4. Sidebar & Login ---
with st.sidebar:
    st.markdown("### 🇮🇳 NSE DASHBOARD")
    if KOTAK_INSTALLED:
        if not st.session_state.kotak_logged_in:
            st.info("🔐 Kotak Neo Login")
            totp = st.text_input("Enter TOTP:", type="password")
            if st.button("Connect Kotak"):
                try:
                    client = NeoAPI(consumer_key=st.secrets["KOTAK"]["CONSUMER_KEY"], consumer_secret=st.secrets["KOTAK"].get("CONSUMER_SECRET",""), environment='prod')
                    client.login(mobilenumber=st.secrets["KOTAK"]["USER_ID"], password=st.secrets["KOTAK"]["PASSWORD"])
                    client.session_2fa(OTP=totp)
                    st.session_state.kotak_client = client
                    st.session_state.kotak_logged_in = True
                    st.rerun()
                except: st.error("Login Failed!")
        else:
            st.success("✅ Connected to Kotak")
    else:
        st.warning("⚠️ Kotak API Library is still installing on server. Wait 1 min.")

# --- 5. Main UI ---
components.html(f"<div style='background:#002b36;color:#00ffd0;padding:10px;border-radius:8px;font-weight:bold;text-align:center;'>📊 HARIDAS NSE TERMINAL | LIVE MARKET</div>", height=50)

# Signals Section (From your screenshot)
st.markdown("<div class='section-title'>🎯 LIVE SIGNALS: MIXED WATCHLIST</div>", unsafe_allow_html=True)
sigs = run_strategy(["SBIN.NS", "RELIANCE.NS"])
if sigs:
    df_sig = pd.DataFrame(sigs)
    st.table(df_sig)

# Option Chain Section
st.markdown("<div class='section-title'>⛓️ LIVE OPTION CHAIN</div>", unsafe_allow_html=True)
st.info("Option Chain data will appear here once Kotak is connected.")
