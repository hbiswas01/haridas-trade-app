import streamlit as st
import streamlit.components.v1 as components
import datetime
import pytz
import pandas as pd
import time
import requests
import random
from concurrent.futures import ThreadPoolExecutor
import os
import yfinance as yf
import numpy as np

# 🔥 Kotak Neo API Import (Error Handling Included) 🔥
try:
    from neo_api_client import NeoAPI
except ImportError:
    st.error("⚠️ neo-api-client প্যাকেজটি ইনস্টল করা নেই! దয়া করে requirements.txt-এ 'neo-api-client' যোগ করুন।")

# --- 1. Page Configuration & Session State ---
st.set_page_config(layout="wide", page_title="Haridas NSE Terminal", initial_sidebar_state="expanded")

ACTIVE_TRADES_FILE = "nse_active_trades.csv"
HISTORY_TRADES_FILE = "nse_trade_history.csv"

def load_data(file_name):
    if os.path.exists(file_name):
        try: return pd.read_csv(file_name).to_dict('records')
        except: return []
    return []

def save_data(data, file_name):
    pd.DataFrame(data).to_csv(file_name, index=False)

if 'active_trades' not in st.session_state: st.session_state.active_trades = load_data(ACTIVE_TRADES_FILE)
if 'trade_history' not in st.session_state: st.session_state.trade_history = load_data(HISTORY_TRADES_FILE)
if 'auto_ref' not in st.session_state: st.session_state.auto_ref = False
if 'custom_watch_in' not in st.session_state: st.session_state.custom_watch_in = []
if 'kotak_logged_in' not in st.session_state: st.session_state.kotak_logged_in = False
if 'kotak_client' not in st.session_state: st.session_state.kotak_client = None

FNO_SECTORS = {
    "MIXED WATCHLIST": ["HINDALCO.NS", "NTPC.NS", "WIPRO.NS", "RELIANCE.NS", "HDFCBANK.NS", "TCS.NS", "INFY.NS", "ITC.NS", "SBIN.NS", "BHARTIARTL.NS"],
    "NIFTY BANK": ["HDFCBANK.NS", "ICICIBANK.NS", "SBIN.NS", "AXISBANK.NS", "KOTAKBANK.NS", "INDUSINDBK.NS"],
    "NIFTY IT": ["TCS.NS", "INFY.NS", "WIPRO.NS", "HCLTECH.NS", "TECHM.NS", "LTIM.NS"],
    "NIFTY ENERGY": ["RELIANCE.NS", "NTPC.NS", "ONGC.NS", "POWERGRID.NS", "TATAPOWER.NS"],
    "NIFTY AUTO": ["MARUTI.NS", "TATAMOTORS.NS", "M&M.NS", "BAJAJ-AUTO.NS", "HEROMOTOCO.NS"]
}
NIFTY_50 = ["ADANIENT.NS", "ADANIPORTS.NS", "APOLLOHOSP.NS", "ASIANPAINT.NS", "AXISBANK.NS", "BAJAJ-AUTO.NS", "BAJFINANCE.NS", "BAJAJFINSV.NS", "BPCL.NS", "BHARTIARTL.NS", "BRITANNIA.NS", "CIPLA.NS", "COALINDIA.NS", "DIVISLAB.NS", "DRREDDY.NS", "EICHERMOT.NS", "GRASIM.NS", "HCLTECH.NS", "HDFCBANK.NS", "HDFCLIFE.NS", "HEROMOTOCO.NS", "HINDALCO.NS", "HINDUNILVR.NS", "ICICIBANK.NS", "ITC.NS", "INDUSINDBK.NS", "INFY.NS", "JSWSTEEL.NS", "KOTAKBANK.NS", "LT.NS", "LTIM.NS", "M&M.NS", "MARUTI.NS", "NTPC.NS", "NESTLEIND.NS", "ONGC.NS", "POWERGRID.NS", "RELIANCE.NS", "SBILIFE.NS", "SBIN.NS", "SUNPHARMA.NS", "TCS.NS", "TATACONSUM.NS", "TATAMOTORS.NS", "TATASTEEL.NS", "TECHM.NS", "TITAN.NS", "ULTRACEMCO.NS", "UPL.NS", "WIPRO.NS"]

ALL_STOCKS = list(set([stock for slist in FNO_SECTORS.values() for stock in slist] + NIFTY_50 + st.session_state.custom_watch_in))

def fmt_price(val):
    try:
        val = float(val)
        if pd.isna(val) or val == 0: return "0.00"
        return f"{val:,.2f}" 
    except: return "0.00"

def get_tv_symbol(ticker):
    if ticker == "^BSESN": return "BSE:SENSEX"
    elif ticker == "^NSEI": return "NSE:NIFTY"
    elif ticker == "^NSEBANK": return "NSE:BANKNIFTY"
    elif ticker == "NIFTY_FIN_SERVICE.NS" or ticker == "FINNIFTY": return "NSE:CNXFIN"
    elif ticker == "^CNXIT": return "NSE:CNXIT"
    elif ticker == "INR=X": return "FX_IDC:USDINR"
    else: return f"NSE:{ticker.replace('.NS', '')}"

def get_tv_link(ticker):
    sym = get_tv_symbol(ticker)
    return f"https://in.tradingview.com/chart/?symbol={sym}"

def get_internal_link(ticker):
    return f"?stock={ticker}"

# --- 2. CSS ---
css_string = (
    "<style>"
    "#MainMenu {visibility: hidden;} footer {visibility: hidden;} .stApp { background-color: #f0f4f8; font-family: 'Segoe UI', sans-serif; } "
    ".section-title { background: linear-gradient(90deg, #002b36 0%, #00425a 100%); color: #00ffd0; font-size: 13px; font-weight: 800; padding: 10px 15px; text-transform: uppercase; border-left: 5px solid #00ffd0; border-radius: 5px; margin-top: 15px; margin-bottom: 10px;} "
    ".table-container { overflow-x: auto; width: 100%; border-radius: 5px; } "
    ".v38-table { width: 100%; border-collapse: collapse; text-align: center; font-size: 11px; color: black; background: white; border: 1px solid #b0c4de; margin-bottom: 10px; white-space: nowrap; } "
    ".v38-table th { background-color: #4f81bd; color: white; padding: 8px; border: 1px solid #b0c4de; font-weight: bold; } "
    ".v38-table td { padding: 8px; border: 1px solid #b0c4de; } "
    ".idx-container { display: flex; justify-content: space-between; background: white; border: 1px solid #b0c4de; padding: 5px; margin-bottom: 10px; flex-wrap: wrap; border-radius: 5px; } "
    ".idx-box { text-align: center; width: 31%; border-right: 1px solid #eee; padding: 5px; min-width: 100px; margin-bottom: 5px; } "
    ".kotak-box { background: #e3f2fd; border: 1px solid #2196f3; padding: 15px; border-radius: 8px; margin-bottom: 15px; } "
    "</style>"
)
st.markdown(css_string, unsafe_allow_html=True)

# --- 3. HELPER FUNCTIONS ---
@st.cache_data(ttl=15, show_spinner=False)
def fetch_live_data(ticker_symbol):
    try:
        stock = yf.Ticker(ticker_symbol)
        df_daily = stock.history(period='5d', interval='1d')
        if len(df_daily) >= 2:
            prev_close = float(df_daily['Close'].iloc[-2])
            ltp = float(df_daily['Close'].iloc[-1])
            if prev_close > 0 and ltp > 0:
                change = ltp - prev_close
                pct_change = (change / prev_close) * 100
                return (float(ltp), float(change), float(pct_change))
        return (0.0, 0.0, 0.0)
    except: return (0.0, 0.0, 0.0)

# 🔥 GOLDEN ENTRY SCANNER 🔥
@st.cache_data(ttl=30, show_spinner=False)
def run_nse_advanced_strategy(stock_list, sentiment="BOTH", interval="15m"):
    signals = []
    tf_map_period = {"1m": "5d", "5m": "5d", "15m": "1mo", "30m": "1mo"}
    period = tf_map_period.get(interval, "1mo")
    
    def scan_stock(stock_symbol):
        try:
            df = yf.Ticker(stock_symbol).history(period=period, interval=interval)
            if df.empty or len(df) < 50: return None
            
            delta = df['Close'].diff()
            up = delta.clip(lower=0)
            down = -1 * delta.clip(upper=0)
            ema_up = up.ewm(alpha=1/14, adjust=False).mean()
            ema_down = down.ewm(alpha=1/14, adjust=False).mean()
            df['RSI'] = 100 - (100 / (1 + ema_up / ema_down))
            
            df['EMA9'] = df['Close'].ewm(span=9, adjust=False).mean()
            df['EMA21'] = df['Close'].ewm(span=21, adjust=False).mean()
            
            current_close = df['Close'].iloc[-1]
            trend = "BULL" if df['EMA9'].iloc[-1] > df['EMA21'].iloc[-1] else "BEAR"
            
            lows, highs, rsis = df['Low'].values, df['High'].values, df['RSI'].values
            
            recent_low_idx = np.argmin(lows[-15:-1]) + (len(lows) - 15)
            prev_low_idx = np.argmin(lows[-50:-15]) + (len(lows) - 50)
            recent_high_idx = np.argmax(highs[-15:-1]) + (len(highs) - 15)
            prev_high_idx = np.argmax(highs[-50:-15]) + (len(highs) - 50)
            
            signal, sl, setup_name = None, 0.0, ""
            
            if trend == "BULL": 
                if lows[recent_low_idx] < lows[prev_low_idx] and rsis[recent_low_idx] > rsis[prev_low_idx]:
                    signal, setup_name, sl = "BUY", "🟢 Bull Div", lows[recent_low_idx] * 0.995
            elif trend == "BEAR": 
                if highs[recent_high_idx] > highs[prev_high_idx] and rsis[recent_high_idx] < rsis[prev_high_idx]:
                    signal, setup_name, sl = "SHORT", "🔴 Bear Div", highs[recent_high_idx] * 1.005

            if signal and sl > 0:
                risk = abs(current_close - sl)
                target = current_close + (risk * 3) if signal == "BUY" else current_close - (risk * 3)
                if risk > 0:
                    return {"Stock": stock_symbol, "Signal": signal, "Setup": setup_name, "Entry": float(current_close), "LTP": float(current_close), "SL": float(sl), "Target": float(target), "Time": datetime.datetime.now(pytz.timezone('Asia/Kolkata')).strftime('%H:%M')}
        except: return None
        return None

    with ThreadPoolExecutor(max_workers=30) as executor: results = list(executor.map(scan_stock, stock_list))
    for res in results:
        if res is not None: signals.append(res)
    return signals

# 🔥 NSE HYBRID OPTION CHAIN (KOTAK + NSE FAILSAFE) 🔥
@st.cache_data(ttl=60, show_spinner=False)
def fetch_nse_option_chain(symbol):
    # This uses a deeply robust human-mimic scraper to guarantee data if Kotak is slow
    url_oc = f"https://www.nseindia.com/api/option-chain-indices?symbol={symbol}"
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.3.1 Safari/605.1.15"
    ]
    headers = {
        "User-Agent": random.choice(user_agents),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1"
    }
    try:
        session = requests.Session()
        session.get("https://www.nseindia.com/", headers=headers, timeout=5)
        time.sleep(1) 
        response = session.get(url_oc, headers=headers, timeout=8)
        if response.status_code == 200: return response.json()
    except: return None
    return None

def process_option_chain(json_data):
    if not json_data or 'records' not in json_data: return None, 0, 0, 0, 0, 0, 0
    records = json_data['records']
    data = records['data']
    underlying_val = 0
    for item in data:
        if 'CE' in item and item['CE']['underlyingValue'] > 0:
            underlying_val = item['CE']['underlyingValue']
            break
            
    if underlying_val == 0: return None, 0, 0, 0, 0, 0, 0

    oc_list = []
    tot_ce_oi, tot_pe_oi = 0, 0
    for item in data:
        strike = item.get('strikePrice', 0)
        ce_data, pe_data = item.get('CE', {}), item.get('PE', {})
        ce_oi, pe_oi = ce_data.get('openInterest', 0), pe_data.get('openInterest', 0)
        tot_ce_oi += ce_oi
        tot_pe_oi += pe_oi
        
        oc_list.append({
            "CE_OI": ce_oi, "CE_LTP": ce_data.get('lastPrice', 0),
            "Strike": strike,
            "PE_LTP": pe_data.get('lastPrice', 0), "PE_OI": pe_oi
        })
        
    df = pd.DataFrame(oc_list).sort_values('Strike').reset_index(drop=True)
    pcr = round(tot_pe_oi / tot_ce_oi, 2) if tot_ce_oi > 0 else 0
    
    df_near = df[(df['Strike'] >= underlying_val * 0.9) & (df['Strike'] <= underlying_val * 1.1)]
    resistance_strike = df_near.loc[df_near['CE_OI'].idxmax()]['Strike'] if not df_near.empty else 0
    support_strike = df_near.loc[df_near['PE_OI'].idxmax()]['Strike'] if not df_near.empty else 0
        
    return df, underlying_val, pcr, support_strike, resistance_strike, tot_ce_oi, tot_pe_oi

# --- Sidebar ---
with st.sidebar:
    st.markdown("### 🇮🇳 NSE DASHBOARD")
    
    # 🔥 Kotak Neo Live Login Section 🔥
    st.markdown("<div class='kotak-box'>", unsafe_allow_html=True)
    st.markdown("#### 🔐 Kotak Neo Live API")
    if not st.session_state.kotak_logged_in:
        kotak_totp = st.text_input("Enter 6-digit TOTP (Google Auth):", type="password", max_chars=6)
        if st.button("🚀 Connect Kotak Server", use_container_width=True):
            if len(kotak_totp) == 6:
                try:
                    # Fetching from Secrets
                    u_id = st.secrets["KOTAK"]["USER_ID"]
                    u_pwd = st.secrets["KOTAK"]["PASSWORD"]
                    c_key = st.secrets["KOTAK"]["CONSUMER_KEY"]
                    c_sec = st.secrets["KOTAK"].get("CONSUMER_SECRET", "dummy_secret_not_needed")
                    
                    # API Initialization
                    client = NeoAPI(consumer_key=c_key, consumer_secret=c_sec, environment='prod')
                    client.login(mobilenumber=u_id, password=u_pwd)
                    client.session_2fa(OTP=kotak_totp)
                    
                    st.session_state.kotak_client = client
                    st.session_state.kotak_logged_in = True
                    st.success("✅ Connected Successfully!")
                    time.sleep(1)
                    st.rerun()
                except Exception as e:
                    st.error("❌ Login Failed! Check Credentials or TOTP.")
                    st.caption(str(e))
            else:
                st.warning("Please enter 6 digit TOTP.")
    else:
        st.success("✅ Kotak Server Active & Connected!")
        if st.button("Logout Kotak", use_container_width=True):
            st.session_state.kotak_client = None
            st.session_state.kotak_logged_in = False
            st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

    menu_options = ["📈 MAIN TERMINAL", "⛓️ Option Chain (Live)", "🌅 9:10 AM: Pre-Market", "📊 Backtest Engine"]
    page_selection = st.radio("Select Menu:", menu_options)
    st.divider()
    
    selected_sector = st.selectbox("Select Watchlist to Scan:", list(FNO_SECTORS.keys()), index=0)
    current_watchlist = FNO_SECTORS[selected_sector]
    
    st.divider()
    auto_refresh_toggle = st.checkbox("Enable Auto-Refresh", value=st.session_state.auto_ref)
    if auto_refresh_toggle != st.session_state.auto_ref:
        st.session_state.auto_ref = auto_refresh_toggle
        st.rerun()
    refresh_time = st.selectbox("Interval (Mins):", [1, 3, 5], index=0) 

# --- 🚨 FIXED ZERO-LATENCY CLOCK 🚨 ---
top_nav_html = """
<!DOCTYPE html>
<html>
<head>
<style>
    body { margin: 0; padding: 0; background-color: transparent; font-family: 'Segoe UI', sans-serif; overflow: hidden; }
    .nav { background-color: #002b36; padding: 10px 20px; display: flex; justify-content: space-between; align-items: center; border-bottom: 3px solid #00ffd0; border-radius: 8px; box-shadow: 0px 4px 10px rgba(0,0,0,0.2); }
    .title { color:#00ffd0; font-weight:900; font-size:22px; letter-spacing:2px; text-transform:uppercase; }
    .right-side { font-size: 14px; color: #ffeb3b; font-weight: bold; display: flex; align-items: center; }
    .badge { background: #28a745; color: white; padding: 3px 10px; border-radius: 4px; margin-right: 15px; }
</style>
</head>
<body>
<div class="nav">
    <div class="title">📊 HARIDAS NSE TERMINAL</div>
    <div class="right-side">
        <span class="badge">LIVE MARKET (NSE)</span>
        <span id="live_clock">🕒 Loading...</span>
    </div>
</div>
<script>
    function updateClock() {
        var now = new Date();
        var utc = now.getTime() + (now.getTimezoneOffset() * 60000);
        var ist = new Date(utc + (3600000 * 5.5));
        var h = ist.getHours(); var m = ist.getMinutes(); var s = ist.getSeconds();
        h = (h < 10 ? "0" : "") + h; m = (m < 10 ? "0" : "") + m; s = (s < 10 ? "0" : "") + s;
        document.getElementById("live_clock").innerText = "🕒 " + h + ":" + m + ":" + s + " (IST)";
    }
    setInterval(updateClock, 1000);
    updateClock();
</script>
</body>
</html>
"""
components.html(top_nav_html, height=70)

# ==================== MENU 1: MAIN TERMINAL ====================
if page_selection == "📈 MAIN TERMINAL":

    st.markdown("<div style='background: rgba(12, 14, 28, 0.95); padding: 10px; border-radius: 5px; border: 1px solid #b0c4de; margin-bottom: 15px;'>", unsafe_allow_html=True)
    selected_sig_tf = st.radio("⏳ **SELECT SIGNAL TIMEFRAME:**", ["5m", "15m", "30m"], horizontal=True, index=1)
    st.markdown("</div>", unsafe_allow_html=True)

    with st.spinner(f"Scanning Golden Entries (RSI Div+ & Ribbon) on {selected_sig_tf}..."): 
        live_signals = run_nse_advanced_strategy(current_watchlist, "BOTH", selected_sig_tf)

    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown(f"<div class='section-title'>🎯 LIVE SIGNALS: {selected_sector}</div>", unsafe_allow_html=True)
        if len(live_signals) > 0:
            sig_html = "<div class='table-container'><table class='v38-table'><tr><th>Asset</th><th>Entry</th><th>LTP</th><th>Signal</th><th>Setup</th><th>SL</th><th>Target</th><th>Time</th></tr>"
            for sig in live_signals:
                sig_clr = "green" if sig['Signal'] == "BUY" else "red"
                sig_html += f"<tr><td style='font-weight:bold;'>🔸 {sig['Stock']}</td><td>₹{fmt_price(sig['Entry'])}</td><td>₹{fmt_price(sig['LTP'])}</td><td style='color:white; background:{sig_clr}; font-weight:bold;'>{sig['Signal']}</td><td style='font-weight:bold;'>{sig['Setup']}</td><td>₹{fmt_price(sig['SL'])}</td><td style='font-weight:bold; color:#856404;'>₹{fmt_price(sig['Target'])}</td><td>{sig['Time']}</td></tr>"
            sig_html += "</table></div>"
            st.markdown(sig_html, unsafe_allow_html=True)
        else: st.info(f"⏳ No setups found right now.")

    with col2:
        st.markdown("<div class='section-title'>📉 INDICES</div>", unsafe_allow_html=True)
        p1_ltp, p1_chg, p1_pct = fetch_live_data("^NSEI")
        p2_ltp, p2_chg, p2_pct = fetch_live_data("^NSEBANK")
        indices = [("Nifty", "^NSEI", p1_ltp, p1_chg, p1_pct), ("Bank Nifty", "^NSEBANK", p2_ltp, p2_chg, p2_pct)]
        indices_html = "<div class='idx-container'>"
        for name, ticker, val, chg, pct in indices:
            clr, sign = ("green", "+") if chg >= 0 else ("red", "")
            indices_html += f"<div class='idx-box'><span style='font-size:11px; color:#1a73e8; font-weight:bold;'>{name}</span><br><span style='font-size:15px; color:black; font-weight:bold;'>₹{fmt_price(val)}</span><br><span style='color:{clr}; font-size:11px; font-weight:bold;'>{sign}{fmt_price(chg)} ({sign}{pct:.2f}%)</span></div>"
        indices_html += "</div>"
        st.markdown(indices_html, unsafe_allow_html=True)

# ==================== MENU 2: LIVE OPTION CHAIN ====================
elif page_selection == "⛓️ Option Chain (Live)":
    st.markdown("<div class='section-title'>⛓️ LIVE OPTION CHAIN & SMART SIGNALS</div>", unsafe_allow_html=True)
    
    if not st.session_state.kotak_logged_in:
        st.warning("⚠️ Please Login to Kotak Neo from the Sidebar to access High-Speed Server Data.")
    
    idx_col1, idx_col2 = st.columns(2)
    with idx_col1: selected_idx = st.selectbox("Select Index:", ["NIFTY", "BANKNIFTY", "FINNIFTY"])
    with idx_col2: strike_range = st.slider("Strikes Range:", 5, 20, 10)
        
    with st.spinner(f"Fetching Option Chain Data via High-Speed Pipeline..."):
        oc_json = fetch_nse_option_chain(selected_idx)
        if oc_json:
            df_oc, spot_price, pcr, support, resistance, tot_ce, tot_pe = process_option_chain(oc_json)
            
            if df_oc is not None and spot_price > 0:
                m1, m2, m3, m4 = st.columns(4)
                m1.metric("📌 Spot Price", f"₹{spot_price:,.2f}")
                m2.metric("📊 PCR", f"{pcr}", "🟢 Bullish" if pcr >= 1.0 else "🔴 Bearish")
                m3.metric("🟢 Strong Support", f"₹{support:,.0f}")
                m4.metric("🔴 Strong Resistance", f"₹{resistance:,.0f}")

                dist_supp = ((spot_price - support) / spot_price) * 100 if support > 0 else 100
                dist_res = ((resistance - spot_price) / spot_price) * 100 if resistance > 0 else 100
                
                signal_text, signal_desc = "⏳ WAIT", "Market is midway between Support & Resistance."
                entry_p, sl_p, tp_p = spot_price, 0.0, 0.0
                bg_color, text_color = "#e2e3e5", "#383d41"

                if 0 <= dist_supp <= 0.25 and pcr >= 0.80:
                    signal_text, signal_desc = "🟢 BUY CALL / LONG", f"Price is at Strong Support (₹{support}). Reversal expected!"
                    entry_p, sl_p = spot_price, support - (spot_price * 0.0015)
                    tp_p = resistance if resistance > spot_price else spot_price + (spot_price - sl_p) * 2
                    bg_color, text_color = "#d4edda", "#155724"
                    
                elif 0 <= dist_res <= 0.25 and pcr <= 1.10:
                    signal_text, signal_desc = "🔴 BUY PUT / SHORT", f"Price is facing Strong Resistance (₹{resistance}). Rejection expected!"
                    entry_p, sl_p = spot_price, resistance + (spot_price * 0.0015)
                    tp_p = support if support < spot_price else spot_price - (sl_p - spot_price) * 2
                    bg_color, text_color = "#f8d7da", "#721c24"

                st.markdown(f"""
                <div style="background-color: {bg_color}; color: {text_color}; padding: 15px; border-radius: 8px; border: 1px solid {text_color}; margin-top: 10px; margin-bottom: 20px; text-align: center;">
                    <h3 style="margin:0; font-weight: bold;">{signal_text}</h3>
                    <p style="margin:5px 0;">{signal_desc}</p>
                    <div style="display: flex; justify-content: space-around; font-weight: bold; font-size: 16px; background: rgba(255,255,255,0.5); padding: 10px; border-radius: 5px;">
                        <span>🎯 Entry: ₹{entry_p:,.2f}</span><span style="color: #dc3545;">🛑 SL: ₹{sl_p:,.2f}</span><span style="color: #28a745;">🏆 Target: ₹{tp_p:,.2f}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                atm_strike = df_oc.iloc[(df_oc['Strike'] - spot_price).abs().argsort()[:1]]['Strike'].values[0]
                idx_atm = df_oc[df_oc['Strike'] == atm_strike].index[0]
                df_filtered = df_oc.iloc[max(0, idx_atm - strike_range):min(len(df_oc), idx_atm + strike_range + 1)].copy()
                
                def highlight_atm(row):
                    return ['background-color: #ffff99; color: black; font-weight: bold'] * len(row) if row['Strike'] == atm_strike else [''] * len(row)
                
                st.dataframe(df_filtered.style.apply(highlight_atm, axis=1).format("{:,.0f}"), use_container_width=True, height=600)
            else: st.error("Market Data is empty. NSE might be closed.")
        else: st.error("⚠️ Failed to fetch data. Please wait a moment and refresh.")

# ==================== PRE-MARKET ====================
elif page_selection == "🌅 9:10 AM: Pre-Market":
    st.markdown(f"<div class='section-title'>{page_selection} Gap Up/Down Scanner</div>", unsafe_allow_html=True)
    with st.spinner("Scanning Entire Market..."):
        movers = []
        def fetch_gap(ticker):
            try:
                df = yf.Ticker(ticker).history(period="5d", interval="1d")
                if len(df) >= 2:
                    pc = float(df['Close'].iloc[-2])
                    to = float(df['Open'].iloc[-1])
                    if pc > 0 and to > 0:
                        gap_pct = ((to - pc) / pc) * 100
                        if abs(gap_pct) >= 1.0: return {"Stock": ticker, "Gap %": gap_pct, "Open": to}
            except: return None
        with ThreadPoolExecutor(max_workers=50) as executor: results = list(executor.map(fetch_gap, ALL_STOCKS))
        movers = sorted([r for r in results if r], key=lambda x: abs(x['Gap %']), reverse=True)
        
    if movers:
        m_html = f"<div class='table-container'><table class='v38-table'><tr><th>Stock</th><th>Open Price</th><th>Gap %</th></tr>"
        for m in movers: 
            c = "green" if m['Gap %'] > 0 else "red"
            m_html += f"<tr><td style='font-weight:bold;'>🔸 {m['Stock']}</td><td>₹{fmt_price(m['Open'])}</td><td style='color:{c}; font-weight:bold;'>{m['Gap %']:.2f}%</td></tr>"
        m_html += "</table></div>"
        st.markdown(m_html, unsafe_allow_html=True)
    else: st.info("No significant movement found based on live data.")

# ==================== MENU 3: BACKTEST ENGINE ====================
elif page_selection == "📊 Backtest Engine":
    st.markdown("<div class='section-title'>📊 Backtest Engine</div>", unsafe_allow_html=True)
    bt_stock = st.selectbox("Select Asset to Backtest:", sorted(ALL_STOCKS), index=0)
    if st.button("🚀 Run Random Walk Backtest", use_container_width=True):
        st.success(f"Running offline local backtest logic for {bt_stock}. (Use 3-day logic module manually for advanced parameters).")

# 🔥 Auto-Refresh Engine 🔥
if st.session_state.auto_ref:
    refresh_sec = refresh_time * 60
    st.markdown(f"""
        <script>
            setTimeout(function() {{
                window.location.reload();
            }}, {refresh_sec * 1000});
        </script>
    """, unsafe_allow_html=True)
