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
    ".block-container { padding-top: 3rem !important; padding-bottom: 1rem !important; padding-left: 1rem !important; padding-right: 1rem !important; } "
    ".section-title { background: linear-gradient(90deg, #002b36 0%, #00425a 100%); color: #00ffd0; font-size: 13px; font-weight: 800; padding: 10px 15px; text-transform: uppercase; border-left: 5px solid #00ffd0; border-radius: 5px; margin-top: 15px; margin-bottom: 10px;} "
    ".table-container { overflow-x: auto; width: 100%; border-radius: 5px; } "
    ".v38-table { width: 100%; border-collapse: collapse; text-align: center; font-size: 11px; color: black; background: white; border: 1px solid #b0c4de; margin-bottom: 10px; white-space: nowrap; } "
    ".v38-table th { background-color: #4f81bd; color: white; padding: 8px; border: 1px solid #b0c4de; font-weight: bold; } "
    ".v38-table td { padding: 8px; border: 1px solid #b0c4de; } .v38-table a { text-decoration: none; cursor: pointer; color: #1a73e8 !important; } "
    ".idx-container { display: flex; justify-content: space-between; background: white; border: 1px solid #b0c4de; padding: 5px; margin-bottom: 10px; flex-wrap: wrap; border-radius: 5px; } "
    ".idx-box { text-align: center; width: 31%; border-right: 1px solid #eee; padding: 5px; min-width: 100px; margin-bottom: 5px; } "
    ".idx-box a { text-decoration: none; font-size: 11px; color: #1a73e8; font-weight: bold; } "
    ".adv-dec-container { background: white; border: 1px solid #b0c4de; padding: 10px; margin-bottom: 10px; text-align: center; border-radius: 5px; } "
    ".adv-dec-bar { display: flex; height: 14px; border-radius: 4px; overflow: hidden; margin: 8px 0; border: 1px solid #ccc; } "
    ".bar-green { background-color: #2e7d32; } .bar-red { background-color: #d32f2f; } "
    ".bar-bg { background: #e0e0e0; width: 100%; height: 14px; min-width: 50px; border-radius: 3px; } "
    ".bar-fg-green { background: #276a44; height: 100%; border-radius: 3px; } .bar-fg-red { background: #8b0000; height: 100%; border-radius: 3px; } "
    "details.sector-details { border: 1px solid #b0c4de; margin-bottom: 5px; background: white; border-radius: 4px; } "
    "summary.sector-summary { padding: 8px; font-weight: bold; cursor: pointer; display: flex; align-items: center; background-color: #f4f6f9; font-size: 11px; } "
    ".sector-content { padding: 8px; border-top: 1px solid #eee; display: flex; flex-wrap: wrap; gap: 5px; background: #fafafa; } "
    ".stock-chip { font-size: 10px; padding: 4px 6px; border-radius: 4px; border: 1px solid #ccc; background: #fff; text-decoration: none !important; font-weight: bold;} "
    "</style>"
)
st.markdown(css_string, unsafe_allow_html=True)

# --- 3. HELPER FUNCTIONS & MATH ---
@st.cache_data(ttl=15, show_spinner=False)
def fetch_live_data(ticker_symbol):
    try:
        stock = yf.Ticker(ticker_symbol)
        df_daily = stock.history(period='5d', interval='1d')
        if len(df_daily) >= 2:
            prev_close = float(df_daily['Close'].iloc[-2])
            try: 
                fast_ltp = float(stock.fast_info.last_price)
                ltp = fast_ltp if fast_ltp > 0 else float(df_daily['Close'].iloc[-1])
            except: ltp = float(df_daily['Close'].iloc[-1])
            
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
    tf_map_period = {"1m": "5d", "3m": "5d", "5m": "5d", "15m": "1mo", "30m": "1mo", "1h": "1mo", "1d": "1y"}
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
            ema9_val = df['EMA9'].iloc[-1]
            ema21_val = df['EMA21'].iloc[-1]
            
            trend = "BULL" if ema9_val > ema21_val else "BEAR"
            
            lows = df['Low'].values
            highs = df['High'].values
            rsis = df['RSI'].values
            
            recent_low_idx = np.argmin(lows[-15:-1]) + (len(lows) - 15)
            prev_low_idx = np.argmin(lows[-50:-15]) + (len(lows) - 50)
            recent_high_idx = np.argmax(highs[-15:-1]) + (len(highs) - 15)
            prev_high_idx = np.argmax(highs[-50:-15]) + (len(highs) - 50)
            
            signal, sl, setup_name = None, 0.0, ""
            
            if trend == "BULL": 
                if lows[recent_low_idx] < lows[prev_low_idx] and rsis[recent_low_idx] > rsis[prev_low_idx]:
                    signal, setup_name, sl = "BUY", "🟢 Bull Div", lows[recent_low_idx] * 0.995
                elif lows[recent_low_idx] > lows[prev_low_idx] and rsis[recent_low_idx] < rsis[prev_low_idx]:
                    signal, setup_name, sl = "BUY", "🟩 Hid Bull", lows[recent_low_idx] * 0.995
                    
            elif trend == "BEAR": 
                if highs[recent_high_idx] > highs[prev_high_idx] and rsis[recent_high_idx] < rsis[prev_high_idx]:
                    signal, setup_name, sl = "SHORT", "🔴 Bear Div", highs[recent_high_idx] * 1.005
                elif highs[recent_high_idx] < highs[prev_high_idx] and rsis[recent_high_idx] > rsis[prev_high_idx]:
                    signal, setup_name, sl = "SHORT", "🟥 Hid Bear", highs[recent_high_idx] * 1.005

            if sentiment == "BULLISH" and signal == "SHORT": return None
            if sentiment == "BEARISH" and signal == "BUY": return None

            if signal and sl > 0:
                risk = abs(current_close - sl)
                target = current_close + (risk * 3) if signal == "BUY" else current_close - (risk * 3)
                if risk > 0:
                    return {"Stock": stock_symbol, "Signal": signal, "Setup": setup_name, "Entry": float(current_close), "LTP": float(current_close), "SL": float(sl), "Target": float(target), "Time": datetime.datetime.now(pytz.timezone('Asia/Kolkata')).strftime('%H:%M')}
        except: return None
        return None

    with ThreadPoolExecutor(max_workers=30) as executor:
        results = list(executor.map(scan_stock, stock_list))
    for res in results:
        if res is not None: signals.append(res)
    return signals

def process_auto_trades(live_signals):
    ist_timezone = pytz.timezone('Asia/Kolkata')
    current_time_str = datetime.datetime.now(ist_timezone).strftime("%Y-%m-%d %H:%M")
    active_stocks = [t['Stock'] for t in st.session_state.active_trades]

    for sig in live_signals:
        if sig['Stock'] not in active_stocks:
            is_triggered = False
            if sig['Signal'] == 'BUY' and sig['LTP'] >= sig['Entry']: is_triggered = True
            elif sig['Signal'] == 'SHORT' and sig['LTP'] <= sig['Entry']: is_triggered = True
            
            if is_triggered:
                new_trade = {"Date": current_time_str, "Stock": sig['Stock'], "Signal": sig['Signal'], "Entry": float(sig['Entry']), "SL": float(sig['SL']), "Target": float(sig['Target']), "Status": "RUNNING"}
                st.session_state.active_trades.append(new_trade)
                save_data(st.session_state.active_trades, ACTIVE_TRADES_FILE)

    trades_to_remove = []
    for trade in st.session_state.active_trades:
        res = fetch_live_data(trade['Stock'])
        ltp = res[0]
        if ltp == 0.0: continue
        close_reason = None
        exit_price = 0.0

        if trade['Signal'] == 'BUY':
            if ltp <= float(trade['SL']): close_reason, exit_price = "🛑 SL HIT", trade['SL']
            elif ltp >= float(trade['Target']): close_reason, exit_price = "🎯 TARGET HIT", trade['Target']
        elif trade['Signal'] == 'SHORT':
            if ltp >= float(trade['SL']): close_reason, exit_price = "🛑 SL HIT", trade['SL']
            elif ltp <= float(trade['Target']): close_reason, exit_price = "🎯 TARGET HIT", trade['Target']

        if close_reason:
            pnl_pct = ((exit_price - trade['Entry']) / trade['Entry']) * 100 if trade['Signal'] == 'BUY' else ((trade['Entry'] - exit_price) / trade['Entry']) * 100
            completed_trade = {"Date": current_time_str, "Stock": trade['Stock'], "Signal": trade['Signal'], "Entry": trade['Entry'], "Exit": exit_price, "Status": close_reason, "P&L %": round(pnl_pct, 2)}
            st.session_state.trade_history.append(completed_trade)
            trades_to_remove.append(trade)

    if trades_to_remove:
        st.session_state.active_trades = [t for t in st.session_state.active_trades if t not in trades_to_remove]
        save_data(st.session_state.active_trades, ACTIVE_TRADES_FILE)
        save_data(st.session_state.trade_history, HISTORY_TRADES_FILE)

@st.cache_data(ttl=120, show_spinner=False)
def calc_dynamic_movers(item_list):
    gainers, losers, trends = [], [], []
    def fetch_data(ticker):
        try:
            res = fetch_live_data(ticker)
            ltp, chg, pct_chg = res[0], res[1], res[2]
            if ltp == 0.0: return None
            
            status, color = None, None
            df = yf.Ticker(ticker).history(period="10d", interval="1d")
            if len(df) >= 3:
                c1 = ltp 
                c2, c3 = float(df['Close'].iloc[-2]), float(df['Close'].iloc[-3])
                o1, o2, o3 = float(df['Open'].iloc[-1]), float(df['Open'].iloc[-2]), float(df['Open'].iloc[-3])
                if c1 > o1 and c2 > o2 and c3 > o3: status, color = "৩ দিন উত্থান", "green"
                elif c1 < o1 and c2 < o2 and c3 < o3: status, color = "৩ দিন পতন", "red"
                
            obj = {"Stock": ticker, "LTP": ltp, "Pct": round(pct_chg, 2)}
            return (obj, status, color)
        except: return None

    with ThreadPoolExecutor(max_workers=50) as executor: results = list(executor.map(fetch_data, item_list))
    for res in results:
        if res:
            obj, status, color = res
            if obj['Pct'] > 0: gainers.append(obj)
            elif obj['Pct'] < 0: losers.append(obj)
            if status: trends.append({"Stock": obj['Stock'], "Status": status, "Color": color})
    return sorted(gainers, key=lambda x: x['Pct'], reverse=True)[:5], sorted(losers, key=lambda x: x['Pct'])[:5], trends

@st.cache_data(ttl=60, show_spinner=False)
def calc_market_breadth(item_list):
    adv, dec = 0, 0
    def fetch_chg(ticker): 
        try: return fetch_live_data(ticker)[2]
        except: return 0.0
    with ThreadPoolExecutor(max_workers=40) as executor: results = list(executor.map(fetch_chg, item_list))
    for pct in results:
        if pct > 0: adv += 1
        elif pct < 0: dec += 1
    return adv, dec

@st.cache_data(ttl=60, show_spinner=False)
def calc_sector_perf(sector_dict, ignore_keys=[]):
    results = []
    for sector, items in sector_dict.items():
        if sector in ignore_keys: continue
        total_pct, valid = 0, 0
        stock_details = []
        for ticker in items:
            try:
                ltp, _, pct = fetch_live_data(ticker)
                if ltp > 0: 
                    total_pct += pct
                    valid += 1
                    stock_details.append({"Stock": ticker, "Pct": pct})
            except: continue
        if valid > 0:
            avg_pct = round(total_pct / valid, 2)
            stock_details = sorted(stock_details, key=lambda x: x['Pct'], reverse=True)
            results.append({"Sector": sector, "Pct": avg_pct, "Width": max(min(abs(avg_pct) * 20, 100), 5), "Stocks": stock_details})
    return sorted(results, key=lambda x: x['Pct'], reverse=True)

@st.cache_data(ttl=60, show_spinner=False)
def scan_pre_market(stock_list):
    movers = []
    def fetch_gap(ticker):
        try:
            df = yf.Ticker(ticker).history(period="5d", interval="1d")
            if len(df) >= 2:
                prev_close = float(df['Close'].iloc[-2])
                today_open = float(df['Open'].iloc[-1])
                if prev_close > 0 and today_open > 0:
                    gap_pct = ((today_open - prev_close) / prev_close) * 100
                    if abs(gap_pct) >= 1.0: return {"Stock": ticker, "Gap %": gap_pct, "Open": today_open}
        except: return None
    with ThreadPoolExecutor(max_workers=50) as executor: results = list(executor.map(fetch_gap, stock_list))
    return sorted([r for r in results if r], key=lambda x: abs(x['Gap %']), reverse=True)


# 🔥 [PLAN B] ULTIMATE NSE OPTION CHAIN SCRAPER (NO API REQUIRED) 🔥
@st.cache_data(ttl=60, show_spinner=False)
def fetch_nse_option_chain(symbol):
    url_oc = f"https://www.nseindia.com/api/option-chain-indices?symbol={symbol}"
    
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.3.1 Safari/605.1.15",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0"
    ]
    
    headers = {
        "User-Agent": random.choice(user_agents),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1"
    }
    
    try:
        session = requests.Session()
        session.get("https://www.nseindia.com/", headers=headers, timeout=5)
        time.sleep(1.5) 
        
        response = session.get(url_oc, headers=headers, timeout=8)
        if response.status_code == 200:
            return response.json()
            
    except Exception as e:
        return None
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
        elif 'PE' in item and item['PE']['underlyingValue'] > 0:
            underlying_val = item['PE']['underlyingValue']
            break
            
    if underlying_val == 0: return None, 0, 0, 0, 0, 0, 0

    oc_list = []
    tot_ce_oi, tot_pe_oi = 0, 0
    for item in data:
        strike = item.get('strikePrice', 0)
        ce_data = item.get('CE', {})
        pe_data = item.get('PE', {})
        
        ce_oi = ce_data.get('openInterest', 0)
        ce_ltp = ce_data.get('lastPrice', 0)
        pe_oi = pe_data.get('openInterest', 0)
        pe_ltp = pe_data.get('lastPrice', 0)
        
        tot_ce_oi += ce_oi
        tot_pe_oi += pe_oi
        
        oc_list.append({
            "CE_OI": ce_oi, "CE_LTP": ce_ltp,
            "Strike": strike,
            "PE_LTP": pe_ltp, "PE_OI": pe_oi
        })
        
    df = pd.DataFrame(oc_list).sort_values('Strike').reset_index(drop=True)
    pcr = round(tot_pe_oi / tot_ce_oi, 2) if tot_ce_oi > 0 else 0
    
    df_near = df[(df['Strike'] >= underlying_val * 0.9) & (df['Strike'] <= underlying_val * 1.1)]
    if not df_near.empty:
        resistance_strike = df_near.loc[df_near['CE_OI'].idxmax()]['Strike']
        support_strike = df_near.loc[df_near['PE_OI'].idxmax()]['Strike']
    else:
        resistance_strike, support_strike = 0, 0
        
    return df, underlying_val, pcr, support_strike, resistance_strike, tot_ce_oi, tot_pe_oi


# --- Sidebar ---
with st.sidebar:
    st.markdown("### 🇮🇳 NSE DASHBOARD")
    menu_options = ["📈 MAIN TERMINAL", "⛓️ Option Chain (Live)", "🌅 9:10 AM: Pre-Market Gap", "📊 Backtest Engine", "⚙️ Scanner Settings"]
    page_selection = st.radio("Select Menu:", menu_options)
    st.divider()
    
    st.markdown("### 📋 CUSTOM WATCHLIST")
    new_asset = st.text_input("Add NSE Stock (e.g. ITC.NS):").upper().strip()
    if st.button("➕ Add Asset") and new_asset:
        if new_asset not in st.session_state.custom_watch_in: st.session_state.custom_watch_in.append(new_asset)
        st.success(f"Added {new_asset}!")
        time.sleep(1)
        st.rerun()

    working_sectors = dict(FNO_SECTORS)
    if st.session_state.custom_watch_in:
        working_sectors["⭐ MY WATCHLIST"] = st.session_state.custom_watch_in
        if st.button("🗑️ Clear My Watchlist"):
            st.session_state.custom_watch_in = []
            st.rerun()

    st.divider()
    st.markdown("### ⚙️ STRATEGY SETTINGS")
    user_sentiment = st.radio("Market Sentiment:", ["BOTH", "BULLISH", "BEARISH"])
    selected_sector = st.selectbox("Select Watchlist to Scan:", list(working_sectors.keys()), index=0)
    current_watchlist = working_sectors[selected_sector]
    
    st.divider()
    st.markdown("### ⏱️ AUTO REFRESH")
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

col_ref1, col_ref2 = st.columns([8, 2])
with col_ref2:
    if st.button("🔄 REFRESH LIVE DATA", type="primary", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

# ==================== MENU 1: MAIN TERMINAL ====================
if page_selection == "📈 MAIN TERMINAL":

    st.markdown("<div style='background: rgba(12, 14, 28, 0.95); padding: 10px; border-radius: 5px; border: 1px solid #b0c4de; margin-bottom: 15px;'>", unsafe_allow_html=True)
    sig_tf_options = {"1m": "1m", "5m": "5m", "15m": "15m", "30m": "30m", "1H": "1h", "1D": "1d"}
    selected_sig_tf = st.radio("⏳ **SELECT SIGNAL TIMEFRAME:**", list(sig_tf_options.keys()), horizontal=True, index=2, key="sig_tf_main_radio_nse")
    sig_interval = sig_tf_options[selected_sig_tf]
    st.markdown("</div>", unsafe_allow_html=True)

    with st.spinner(f"Scanning Golden Entries (RSI Div+ & Ribbon) on {selected_sig_tf}..."): 
        live_signals = run_nse_advanced_strategy(current_watchlist, user_sentiment, sig_interval)
    process_auto_trades(live_signals)

    with st.spinner("Fetching Market Movers..."):
        adv, dec = calc_market_breadth(ALL_STOCKS)
        gainers, losers, trends = calc_dynamic_movers(ALL_STOCKS)

    col1, col2, col3 = st.columns([1.25, 2.5, 1.25])

    with col1:
        st.markdown("<div class='section-title'>📊 SECTOR PERFORMANCE</div>", unsafe_allow_html=True)
        with st.spinner("Fetching Sectors..."): real_sectors = calc_sector_perf(working_sectors)
        if real_sectors:
            sec_html = "<div>"
            for s in real_sectors:
                c = "green" if s['Pct'] >= 0 else "red"
                bc = "bar-fg-green" if s['Pct'] >= 0 else "bar-fg-red"
                sign = "+" if s['Pct'] >= 0 else ""
                sec_html += f"""
                <details class='sector-details'>
                    <summary class='sector-summary'>
                        <div style='width: 45%; color:#003366; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;'>📂 {s['Sector']}</div>
                        <div style='width: 25%; color:{c}; text-align: center;'>{sign}{s['Pct']:.2f}%</div>
                        <div style='width: 30%;'><div class='bar-bg'><div class='{bc}' style='width:{s['Width']}%;'></div></div></div>
                    </summary>
                    <div class='sector-content'>
                """
                for st_data in s['Stocks']:
                    st_color = "green" if st_data['Pct'] >= 0 else "red"
                    st_sign = "+" if st_data['Pct'] >= 0 else ""
                    sec_html += f"<span class='stock-chip' style='color:{st_color};'>{st_data['Stock']} ({st_sign}{st_data['Pct']:.2f}%)</span>"
                sec_html += "</div></details>"
            sec_html += "</div>"
            st.markdown(sec_html, unsafe_allow_html=True)

    with col2:
        st.markdown("<div class='section-title'>📉 MARKET INDICES (LIVE)</div>", unsafe_allow_html=True)
        p1_ltp, p1_chg, p1_pct = fetch_live_data("^BSESN")
        p2_ltp, p2_chg, p2_pct = fetch_live_data("^NSEI")
        p3_ltp, p3_chg, p3_pct = fetch_live_data("INR=X")
        p4_ltp, p4_chg, p4_pct = fetch_live_data("^NSEBANK")
        indices = [("Sensex", "^BSESN", p1_ltp, p1_chg, p1_pct), ("Nifty", "^NSEI", p2_ltp, p2_chg, p2_pct), ("USDINR", "INR=X", p3_ltp, p3_chg, p3_pct), ("Nifty Bank", "^NSEBANK", p4_ltp, p4_chg, p4_pct)]
        
        indices_html = "<div class='idx-container'>"
        for name, ticker, val, chg, pct in indices:
            clr = "green" if chg >= 0 else "red"
            sign = "+" if chg >= 0 else ""
            prefix = "₹" if name != "USDINR" else "₹"
            if name == "USDINR": val_str, chg_str = f"{val:.4f}", f"{chg:.4f}"
            else: val_str, chg_str = fmt_price(val), fmt_price(chg)
            indices_html += f"<div class='idx-box'><span style='font-size:11px; color:#1a73e8; font-weight:bold;'>{name}</span><br><span style='font-size:15px; color:black; font-weight:bold;'>{prefix}{val_str}</span><br><span style='color:{clr}; font-size:11px; font-weight:bold;'>{sign}{chg_str} ({sign}{pct:.2f}%)</span></div>"
        indices_html += "</div>"
        st.markdown(indices_html, unsafe_allow_html=True)

        total_adv_dec = adv + dec
        adv_pct = (adv / total_adv_dec) * 100 if total_adv_dec > 0 else 50
        st.markdown(f"<div class='section-title'>📊 ADVANCE/ DECLINE (NSE)</div>", unsafe_allow_html=True)
        adv_dec_html = f"<div class='adv-dec-container'><div class='adv-dec-bar'><div class='bar-green' style='width: {adv_pct}%;'></div><div class='bar-red' style='width: {100-adv_pct}%;'></div></div><div style='display:flex; justify-content:space-between; font-size:12px; font-weight:bold;'><span style='color:green;'>Advances: {adv}</span><span style='color:red;'>Declines: {dec}</span></div></div>"
        st.markdown(adv_dec_html, unsafe_allow_html=True)

        st.markdown(f"<div class='section-title'>🎯 LIVE SIGNALS: {selected_sector} ({selected_sig_tf} RSI DIV+ RIBBON)</div>", unsafe_allow_html=True)
        if len(live_signals) > 0:
            sig_html = "<div class='table-container'><table class='v38-table'><tr><th>Asset</th><th>Entry</th><th>LTP</th><th>Signal</th><th>Setup</th><th>SL</th><th>Target (1:3)</th><th>Time</th></tr>"
            for sig in live_signals:
                sig_clr = "green" if sig['Signal'] == "BUY" else "red"
                sig_html += f"<tr><td style='font-weight:bold;'>🔸 {sig['Stock']}</td><td>₹{fmt_price(sig['Entry'])}</td><td>₹{fmt_price(sig['LTP'])}</td><td style='color:white; background:{sig_clr}; font-weight:bold;'>{sig['Signal']}</td><td style='font-weight:bold;'>{sig['Setup']}</td><td>₹{fmt_price(sig['SL'])}</td><td style='font-weight:bold; color:#856404;'>₹{fmt_price(sig['Target'])}</td><td>{sig['Time']}</td></tr>"
            sig_html += "</table></div>"
            st.markdown(sig_html, unsafe_allow_html=True)
        else: st.info(f"⏳ No RSI Divergence/Ribbon entries matching on {selected_sig_tf} chart right now.")

    with col3:
        st.markdown("<div class='section-title'>🚀 LIVE TOP GAINERS</div>", unsafe_allow_html=True)
        if gainers:
            g_html = "<div class='table-container'><table class='v38-table'><tr><th>Asset</th><th>LTP</th><th>%</th></tr>"
            for g in gainers: 
                g_html += f"<tr><td style='text-align:left; font-weight:bold;'>🔸 {g['Stock']}</td><td>₹{fmt_price(g['LTP'])}</td><td style='color:green; font-weight:bold;'>+{g['Pct']:.2f}%</td></tr>"
            g_html += "</table></div>"
            st.markdown(g_html, unsafe_allow_html=True)

        st.markdown("<div class='section-title'>🔻 LIVE TOP LOSERS</div>", unsafe_allow_html=True)
        if losers:
            l_html = "<div class='table-container'><table class='v38-table'><tr><th>Asset</th><th>LTP</th><th>%</th></tr>"
            for l in losers: 
                l_html += f"<tr><td style='text-align:left; font-weight:bold;'>🔸 {l['Stock']}</td><td>₹{fmt_price(l['LTP'])}</td><td style='color:red; font-weight:bold;'>{l['Pct']:.2f}%</td></tr>"
            l_html += "</table></div>"
            st.markdown(l_html, unsafe_allow_html=True)

# ==================== MENU 2: LIVE OPTION CHAIN ====================
elif page_selection == "⛓️ Option Chain (Live)":
    st.markdown("<div class='section-title'>⛓️ LIVE OPTION CHAIN & SMART SIGNALS</div>", unsafe_allow_html=True)
    
    idx_col1, idx_col2 = st.columns(2)
    with idx_col1:
        selected_idx = st.selectbox("Select Index:", ["NIFTY", "BANKNIFTY", "FINNIFTY", "MIDCPNIFTY"])
    with idx_col2:
        strike_range = st.slider("Number of Strikes (Above & Below ATM):", 5, 30, 10)
        
    with st.spinner(f"Using Anti-Bot Scraper to fetch Option Chain for {selected_idx}..."):
        oc_json = fetch_nse_option_chain(selected_idx)
        if oc_json:
            df_oc, spot_price, pcr, support, resistance, tot_ce, tot_pe = process_option_chain(oc_json)
            
            if df_oc is not None and spot_price > 0:
                m1, m2, m3, m4 = st.columns(4)
                m1.metric("📌 Spot Price", f"₹{spot_price:,.2f}")
                pcr_status = "🟢 Bullish (Supportive)" if pcr >= 1.0 else "🔴 Bearish (Resistance)"
                m2.metric("📊 PCR (Put-Call Ratio)", f"{pcr}", pcr_status)
                m3.metric("🟢 Strong Support (PE)", f"₹{support:,.0f}")
                m4.metric("🔴 Strong Resistance (CE)", f"₹{resistance:,.0f}")

                dist_supp = ((spot_price - support) / spot_price) * 100 if support > 0 else 100
                dist_res = ((resistance - spot_price) / spot_price) * 100 if resistance > 0 else 100
                
                signal_text, signal_desc = "⏳ WAIT", "Market is midway between Support & Resistance. No clear entry."
                entry_p, sl_p, tp_p = spot_price, 0.0, 0.0
                bg_color, text_color = "#e2e3e5", "#383d41"
                sl_buffer = spot_price * 0.0015 

                if 0 <= dist_supp <= 0.25 and pcr >= 0.80:
                    signal_text, signal_desc = "🟢 BUY CALL / LONG", f"Price is at Strong Support (₹{support}). Reversal expected!"
                    entry_p, sl_p = spot_price, support - sl_buffer
                    tp_p = resistance if resistance > spot_price else spot_price + (spot_price - sl_p) * 2
                    bg_color, text_color = "#d4edda", "#155724"
                    
                elif 0 <= dist_res <= 0.25 and pcr <= 1.10:
                    signal_text, signal_desc = "🔴 BUY PUT / SHORT", f"Price is facing Strong Resistance (₹{resistance}). Rejection expected!"
                    entry_p, sl_p = spot_price, resistance + sl_buffer
                    tp_p = support if support < spot_price else spot_price - (sl_p - spot_price) * 2
                    bg_color, text_color = "#f8d7da", "#721c24"

                st.markdown(f"""
                <div style="background-color: {bg_color}; color: {text_color}; padding: 15px; border-radius: 8px; border: 1px solid {text_color}; margin-top: 10px; margin-bottom: 20px; text-align: center; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                    <h3 style="margin:0; font-weight: bold;">{signal_text}</h3>
                    <p style="margin:5px 0;">{signal_desc}</p>
                    <div style="display: flex; justify-content: space-around; font-weight: bold; font-size: 16px; background: rgba(255,255,255,0.5); padding: 10px; border-radius: 5px;">
                        <span>🎯 Entry: ₹{entry_p:,.2f}</span><span style="color: #dc3545;">🛑 SL: ₹{sl_p:,.2f}</span><span style="color: #28a745;">🏆 Target: ₹{tp_p:,.2f}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                atm_strike = df_oc.iloc[(df_oc['Strike'] - spot_price).abs().argsort()[:1]]['Strike'].values[0]
                idx_atm = df_oc[df_oc['Strike'] == atm_strike].index[0]
                start_idx, end_idx = max(0, idx_atm - strike_range), min(len(df_oc), idx_atm + strike_range + 1)
                df_filtered = df_oc.iloc[start_idx:end_idx].copy()
                
                def highlight_atm(row):
                    return ['background-color: #ffff99; color: black; font-weight: bold'] * len(row) if row['Strike'] == atm_strike else [''] * len(row)
                
                st.dataframe(df_filtered.style.apply(highlight_atm, axis=1).format("{:,.0f}"), use_container_width=True, height=600)
            else:
                st.error("Market Data is empty. NSE might be closed.")
        else:
            st.error("⚠️ Failed to fetch data. Don't worry, just click the REFRESH button once or twice to bypass the NSE Bot-Checker.")

# ==================== PRE-MARKET & OPENING MOVERS ====================
elif page_selection == "🌅 9:10 AM: Pre-Market Gap":
    st.markdown(f"<div class='section-title'>{page_selection}</div>", unsafe_allow_html=True)
    with st.spinner("Scanning Entire Market..."):
        movers = scan_pre_market(ALL_STOCKS)
    if movers:
        m_html = f"<div class='table-container'><table class='v38-table'><tr><th>Stock</th><th>Open Price</th><th>Gap % (vs Yesterday Close)</th></tr>"
        for m in movers: 
            c = "green" if m['Gap %'] > 0 else "red"
            m_html += f"<tr><td style='font-weight:bold;'>🔸 {m['Stock']}</td><td>₹{fmt_price(m['Open'])}</td><td style='color:{c}; font-weight:bold;'>{m['Gap %']:.2f}%</td></tr>"
        m_html += "</table></div>"
        st.markdown(m_html, unsafe_allow_html=True)
    else: st.info("No significant movement found based on live data.")

# ==================== MENU 3: BACKTEST ENGINE ====================
elif page_selection == "📊 Backtest Engine":
    st.markdown("<div class='section-title'>📊 Backtest Engine</div>", unsafe_allow_html=True)
    bt_col1, bt_col2 = st.columns(2)
    with bt_col1: bt_stock = st.selectbox("Select Asset to Backtest:", sorted(ALL_STOCKS), index=0)
    with bt_col2: bt_period = st.selectbox("Select Time Period:", ["1mo", "3mo", "6mo", "1y", "2y"])
    if st.button("🚀 Run Backtest", use_container_width=True):
        with st.spinner(f"Fetching {bt_period} historical data for {bt_stock}..."):
            try:
                bt_data = yf.Ticker(bt_stock).history(period=bt_period)
                if len(bt_data) > 3:
                    trades = []
                    for i in range(3, len(bt_data)):
                        c1, o1 = bt_data['Close'].iloc[i-1], bt_data['Open'].iloc[i-1]
                        c2, o2 = bt_data['Close'].iloc[i-2], bt_data['Open'].iloc[i-2]
                        c3, o3 = bt_data['Close'].iloc[i-3], bt_data['Open'].iloc[i-3]
                        if c1 > o1 and c2 > o2 and c3 > o3:
                            entry_price, exit_price = bt_data['Open'].iloc[i], bt_data['Close'].iloc[i]
                            if entry_price > 0:
                                pnl = ((entry_price - exit_price) / entry_price) * 100
                                trades.append({"Date": bt_data.index[i].strftime('%Y-%m-%d'), "Setup": "3 Days GREEN", "Signal": "SHORT", "Entry": fmt_price(entry_price), "Exit": fmt_price(exit_price), "P&L %": round(pnl, 2)})
                        elif c1 < o1 and c2 < o2 and c3 < o3:
                            entry_price, exit_price = bt_data['Open'].iloc[i], bt_data['Close'].iloc[i]
                            if entry_price > 0:
                                pnl = ((exit_price - entry_price) / entry_price) * 100
                                trades.append({"Date": bt_data.index[i].strftime('%Y-%m-%d'), "Setup": "3 Days RED", "Signal": "BUY", "Entry": fmt_price(entry_price), "Exit": fmt_price(exit_price), "P&L %": round(pnl, 2)})
                    bt_df = pd.DataFrame(trades)
                    if not bt_df.empty:
                        total_pnl = bt_df['P&L %'].sum()
                        win_rate = (len(bt_df[bt_df['P&L %'] > 0]) / len(bt_df)) * 100
                        m_col1, m_col2, m_col3 = st.columns(3)
                        m_col1.metric("Total Trades", len(bt_df))
                        m_col2.metric("Win Rate", f"{win_rate:.2f}%")
                        m_col3.metric("Total Strategy P&L %", f"{total_pnl:.2f}%", delta=f"{total_pnl:.2f}%")
                        st.dataframe(bt_df, use_container_width=True)
                    else: st.info(f"No valid setups found for {bt_stock} in the last {bt_period}.")
            except Exception as e: st.error(f"Error fetching data: {e}")

# ==================== MENU 4: SETTINGS ====================
elif page_selection == "⚙️ Scanner Settings":
    st.markdown("<div class='section-title'>⚙️ System Status</div>", unsafe_allow_html=True)
    st.success("✅ Exclusive Indian Market (NSE) App \n\n ✅ PERFECT Zero-Latency Clock Active \n\n ✅ ANTI-BOT Option Chain (NO API Needed) ⛓️ \n\n ✅ Smart OI Entry & SL Signals Active 🚀 \n\n ✅ RSI Divergence + Ribbon Logic Integrated 🔥 \n\n ✅ Sleep Bug Fixed (Frontend Refresh Active) 🐛🔨")

# 🔥 BUG FIX: Removed backend time.sleep() and added Frontend Auto-Refresh 🔥
if st.session_state.auto_ref:
    refresh_sec = refresh_time * 60
    st.markdown(f"""
        <script>
            setTimeout(function() {{
                window.location.reload();
            }}, {refresh_sec * 1000});
        </script>
    """, unsafe_allow_html=True)
