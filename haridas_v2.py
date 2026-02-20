import yfinance as yf
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import pandas as pd
from datetime import datetime
import threading

# Sector Map (Updated from pic)
SECTOR_MAP = {
    "NIFTY BANK 🏦": ["HDFCBANK.NS", "ICICIBANK.NS", "SBIN.NS", "KOTAKBANK.NS", "AXISBANK.NS"],
    "NIFTY IT 💻": ["TCS.NS", "INFY.NS", "HCLTECH.NS", "WIPRO.NS", "TECHM.NS"],
    "NIFTY AUTO 🚗": ["TATAMOTORS.NS", "MARUTI.NS", "M&M.NS", "BAJAJ-AUTO.NS", "EICHERMOT.NS"],
    "NIFTY METAL ⚙️": ["TATASTEEL.NS", "JSWSTEEL.NS", "HINDALCO.NS", "VEDL.NS"],
    "NIFTY ENERGY ⚡": ["RELIANCE.NS", "NTPC.NS", "POWERGRID.NS", "ONGC.NS"],
    "NIFTY PHARMA 💊": ["SUNPHARMA.NS", "CIPLA.NS", "DRREDDY.NS", "DIVISLAB.NS"],
    "NIFTY FMCG 🛒": ["ITC.NS", "HINDUNILVR.NS", "NESTLEIND.NS", "BRITANNIA.NS"],
    "NIFTY INFRA 🏗️": ["LT.NS", "ADANIPORTS.NS", "GRASIM.NS", "AMBUJACEM.NS"],
    "NIFTY REALTY 🏢": ["DLF.NS", "GODREJPROP.NS", "OBEROIRLTY.NS", "PRESTIGE.NS"],
    "NIFTY FIN SRV 💹": ["BAJFINANCE.NS", "BAJAJFINSV.NS", "CHOLAFIN.NS"]
}

scan_results = []

def update_clock():
    now = datetime.now().strftime("%H:%M:%S")
    clock_label.config(text=f"LIVE: {now}")
    app.after(1000, update_clock)

def fetch_market_data():
    global scan_results
    scan_results = []
    advances, declines = 0, 0
    
    # Clear previous data
    for t in [signal_tree, gainer_tree, loser_tree, sector_tree, drastic_tree]:
        for item in t.get_children(): t.delete(item)
    
    # 📊 মার্কেট ইনডেক্স ফেচিং (ফিক্সড)
    broad_indices = {
        "SENSEX": "^BSESN", 
        "NIFTY 50": "^NSEI", 
        "NIFTY BANK": "^NSEBANK", 
        "NIFTY IT": "^CNXIT",     
        "NIFTY FIN": "NIFTY_FIN_SERVICE.NS" 
    }
    
    for name, symbol in broad_indices.items():
        try:
            df = yf.Ticker(symbol).history(period="2d")
            if not df.empty:
                ltp = round(df['Close'].iloc[-1], 2)
                prev = df['Close'].iloc[-2]
                pt_chg = round(ltp - prev, 2)
                pct_chg = round((pt_chg / prev) * 100, 2)
                
                color = "#28a745" if pt_chg > 0 else "#dc3545" 
                sign = "+" if pt_chg > 0 else ""
                
                idx_labels[name]['price'].config(text=f"{ltp:,.2f}", fg="#1a1a1a")
                idx_labels[name]['change'].config(text=f"{sign}{pt_chg} ({sign}{pct_chg}%)", fg=color)
        except: pass

    all_stocks_data = []
    sector_perf = []
    
    for sector, stocks in SECTOR_MAP.items():
        sec_chgs = []
        for stock in stocks:
            try:
                df = yf.Ticker(stock).history(period="7d")
                if not df.empty and len(df) >= 4:
                    prices = df['Close'].values
                    ltp = round(prices[-1], 2)
                    chg = round(((ltp - prices[-2]) / prices[-2]) * 100, 2)
                    
                    all_stocks_data.append((stock, ltp, chg, prices))
                    sec_chgs.append(chg)
                    if chg > 0: advances += 1
                    else: declines += 1
            except: continue 
        if sec_chgs:
            sector_perf.append((sector, round(sum(sec_chgs)/len(sec_chgs), 2)))

    # Sector View
    for sec, chg in sorted(sector_perf, key=lambda x: x[1], reverse=True):
        tag = 'sec_up' if chg > 0 else 'sec_down'
        bar = "█" * int(abs(chg) * 10) if abs(chg) > 0 else ""
        sector_tree.insert("", "end", values=(sec, f"{chg:+}%", bar), tags=(tag,))

    adv_label.config(text=f"ADVANCES: {advances}")
    dec_label.config(text=f"DECLINES: {declines}")

    # Gainers/Losers
    sorted_stocks = sorted(all_stocks_data, key=lambda x: x[2], reverse=True)
    for s in sorted_stocks[:5]: gainer_tree.insert("", "end", values=(s[0], f"+{s[2]}%"), tags=('gainer',))
    for s in sorted_stocks[-5:]: loser_tree.insert("", "end", values=(s[0], f"{s[2]}%"), tags=('loser',))

    # 💹 Trading Signals & Drastic Watch (Filtered)
    for stock, ltp, change, prices in sorted_stocks:
        # Drastic Watch Logic
        is_falling_3d = (prices[-2] < prices[-3] < prices[-4])
        is_rising_3d = (prices[-2] > prices[-3] > prices[-4])
        
        if is_falling_3d: drastic_tree.insert("", "end", values=(stock, "৩ দিন পতন"), tags=('fall',))
        elif is_rising_3d: drastic_tree.insert("", "end", values=(stock, "৩ দিন উত্থান"), tags=('rise',))

        # 🎯 Signal logic (Only Buy/Sell)
        signal = "-"
        if change >= 2.0 and not is_falling_3d: signal = "BUY"
        elif change <= -2.0 and not is_rising_3d: signal = "SELL"

        # শুধু সিগন্যাল থাকলে তবেই লিস্টে আসবে
        if signal != "-":
            tag = 'buy_row' if signal == "BUY" else 'sell_row'
            sl = round(ltp * 0.985, 2) if signal == "BUY" else round(ltp * 1.015, 2)
            t1, t2, t3 = round(ltp*1.01, 2), round(ltp*1.02, 2), round(ltp*1.03, 2)
            if signal == "SELL":
                t1, t2, t3 = round(ltp*0.99, 2), round(ltp*0.98, 2), round(ltp*0.97, 2)
            
            row = (stock, ltp, f"{change}%", signal, sl, t1, t2, t3, datetime.now().strftime('%H:%M:%S'))
            signal_tree.insert("", "end", values=row, tags=(tag,))
            scan_results.append(row)
            
    scan_btn.config(text="SCAN MARKET", state="normal")

def start_scan():
    scan_btn.config(text="SCANNING...", state="disabled")
    threading.Thread(target=fetch_market_data).start()

# --- GUI Setup (Identical to your screenshot) ---
app = tk.Tk()
app.title("Haridas Pro Master Terminal v38.0")
app.state('zoomed')
app.configure(bg="#eaedf2")

# Styles
style = ttk.Style()
style.theme_use("clam")
style.configure("Treeview.Heading", background="#4e73df", foreground="white", font=("Arial", 10, "bold"))
style.configure("Treeview", rowheight=28)

# Top Bar
top = tk.Frame(app, bg="#0a192f", height=60); top.pack(side="top", fill="x")
tk.Label(top, text="HARIDAS NSE TERMINAL", font=("Arial", 16, "bold"), bg="#0a192f", fg="#00ffcc").pack(side="left", padx=20)
clock_label = tk.Label(top, text="", font=("Consolas", 14), bg="#0a192f", fg="#ffcc00"); clock_label.pack(side="left", padx=20)
adv_label = tk.Label(top, text="ADVANCES: 0", font=("Arial", 12, "bold"), bg="#0a192f", fg="#00ffcc"); adv_label.pack(side="left", padx=15)
dec_label = tk.Label(top, text="DECLINES: 0", font=("Arial", 12, "bold"), bg="#0a192f", fg="#ff4444"); dec_label.pack(side="left", padx=15)

scan_btn = tk.Button(top, text="SCAN MARKET", command=start_scan, bg="#007bff", fg="white", font=("Arial", 10, "bold"), padx=15)
scan_btn.pack(side="right", padx=10, pady=10)

# Body Layout
body = tk.Frame(app, bg="#eaedf2"); body.pack(fill="both", expand=True, padx=10, pady=10)

def create_box(parent, title):
    f = tk.LabelFrame(parent, text=title, bg="white", fg="#4e73df", font=("Arial", 11, "bold"), bd=2)
    return f

# Left: Sector
left_frame = create_box(body, " SECTOR PERFORMANCE ")
left_frame.pack(side="left", fill="both", expand=True, padx=5)
sector_tree = ttk.Treeview(left_frame, columns=("S", "C", "B"), show="headings")
sector_tree.heading("S", text="Sector"); sector_tree.column("S", width=120)
sector_tree.heading("C", text="%"); sector_tree.column("C", width=70)
sector_tree.heading("B", text="Trend"); sector_tree.column("B", width=100)
sector_tree.tag_configure('sec_up', foreground="green"); sector_tree.tag_configure('sec_down', foreground="red")
sector_tree.pack(fill="both", expand=True)

# Mid: Indices & Signals
mid_frame = tk.Frame(body, bg="#eaedf2")
mid_frame.pack(side="left", fill="both", expand=True, padx=5)

idx_box = create_box(mid_frame, " MARKET INDICES ")
idx_box.pack(side="top", fill="x", pady=(0, 10))
idx_labels = {}
for name in ["SENSEX", "NIFTY 50", "NIFTY BANK", "NIFTY IT", "NIFTY FIN"]:
    f = tk.Frame(idx_box, bg="#f8f9fc", bd=1, relief="ridge")
    f.pack(side="left", expand=True, fill="both",
