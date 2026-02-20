import yfinance as yf
import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
from datetime import datetime
import threading

# Sector mapping based on your haridas_v2.py
SECTOR_MAP = {
    "BANK 🏦": ["HDFCBANK.NS", "ICICIBANK.NS", "SBIN.NS", "KOTAKBANK.NS", "AXISBANK.NS"],
    "IT 💻": ["TCS.NS", "INFY.NS", "HCLTECH.NS", "WIPRO.NS", "TECHM.NS"],
    "AUTO 🚗": ["TATAMOTORS.NS", "MARUTI.NS", "M&M.NS", "BAJAJ-AUTO.NS", "EICHERMOT.NS"],
    "METAL ⚙️": ["TATASTEEL.NS", "JSWSTEEL.NS", "HINDALCO.NS", "VEDL.NS"],
    "ENERGY ⚡": ["RELIANCE.NS", "NTPC.NS", "POWERGRID.NS", "ONGC.NS"],
    "PHARMA 💊": ["SUNPHARMA.NS", "CIPLA.NS", "DRREDDY.NS", "DIVISLAB.NS"],
    "FMCG 🛒": ["ITC.NS", "HINDUNILVR.NS", "NESTLEIND.NS", "BRITANNIA.NS"]
}

class HaridasMobileV2:
    def __init__(self, root):
        self.root = root
        self.root.title("Haridas Mobile v2")
        self.root.geometry("400x850")
        self.root.configure(bg="#0a192f")
        
        self.scan_results = []
        self.setup_ui()
        self.update_clock()

    def setup_ui(self):
        # Header
        header = tk.Frame(self.root, bg="#0a192f", pady=10)
        header.pack(fill="x")
        tk.Label(header, text="HARIDAS V2 MOBILE", font=("Arial", 14, "bold"), bg="#0a192f", fg="#00ffcc").pack()
        self.clock_label = tk.Label(header, text="", font=("Consolas", 10), bg="#0a192f", fg="#ffcc00")
        self.clock_label.pack()

        # Action Buttons
        btn_frame = tk.Frame(self.root, bg="#0a192f")
        btn_frame.pack(fill="x", padx=10, pady=5)
        self.scan_btn = tk.Button(btn_frame, text="SCAN MARKET", command=self.start_scan, bg="#007bff", fg="white", font=("Arial", 10, "bold"), height=2)
        self.scan_btn.pack(fill="x", pady=5)

        # Scrollable Body
        self.main_container = ttk.Frame(self.root)
        self.main_container.pack(fill="both", expand=True)
        
        canvas = tk.Canvas(self.main_container, bg="#eaedf2")
        scrollbar = ttk.Scrollbar(self.main_container, orient="vertical", command=canvas.yview)
        self.scrollable_frame = tk.Frame(canvas, bg="#eaedf2")

        self.scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Sections
        self.create_signals_section()
        self.create_sector_section()
        self.create_drastic_section()

    def create_signals_section(self):
        f = tk.LabelFrame(self.scrollable_frame, text=" 💹 TRADING SIGNALS ", bg="white", font=("Arial", 10, "bold"))
        f.pack(fill="x", padx=10, pady=10)
        self.sig_tree = ttk.Treeview(f, columns=("S", "L", "Sig"), show="headings", height=6)
        self.sig_tree.heading("S", text="Stock"); self.sig_tree.column("S", width=120)
        self.sig_tree.heading("L", text="LTP"); self.sig_tree.column("L", width=80)
        self.sig_tree.heading("Sig", text="Signal"); self.sig_tree.column("Sig", width=80)
        self.sig_tree.pack(fill="x", padx=5, pady=5)

    def create_sector_section(self):
        f = tk.LabelFrame(self.scrollable_frame, text=" 🏢 SECTOR TRENDS ", bg="white", font=("Arial", 10, "bold"))
        f.pack(fill="x", padx=10, pady=10)
        self.sec_tree = ttk.Treeview(f, columns=("S", "C", "B"), show="headings", height=6)
        self.sec_tree.heading("S", text="Sector"); self.sec_tree.column("S", width=100)
        self.sec_tree.heading("C", text="%"); self.sec_tree.column("C", width=60)
        self.sec_tree.heading("B", text="Visual"); self.sec_tree.column("B", width=100)
        self.sec_tree.pack(fill="x", padx=5, pady=5)

    def create_drastic_section(self):
        f = tk.LabelFrame(self.scrollable_frame, text=" ⚠️ DRASTIC WATCH (3-Day) ", bg="white", font=("Arial", 10, "bold"))
        f.pack(fill="x", padx=10, pady=10)
        self.drastic_tree = ttk.Treeview(f, columns=("S", "Status"), show="headings", height=5)
        self.drastic_tree.heading("S", text="Stock"); self.drastic_tree.column("S", width=140)
        self.drastic_tree.heading("Status", text="Trend"); self.drastic_tree.column("Status", width=140)
        self.drastic_tree.pack(fill="x", padx=5, pady=5)

    def update_clock(self):
        self.clock_label.config(text=datetime.now().strftime("%H:%M:%S"))
        self.root.after(1000, self.update_clock)

    def start_scan(self):
        self.scan_btn.config(text="SCANNING...", state="disabled")
        threading.Thread(target=self.fetch_data).start()

    def fetch_data(self):
        # Clear old data
        for t in [self.sig_tree, self.sec_tree, self.drastic_tree]:
            t.delete(*t.get_children())
        
        for sector, stocks in SECTOR_MAP.items():
            sector_chgs = []
            for s in stocks:
                try:
                    df = yf.Ticker(s).history(period="5d")
                    if len(df) < 4: continue
                    prices = df['Close'].values
                    ltp = round(prices[-1], 2)
                    chg = round(((ltp - prices[-2])/prices[-2])*100, 2)
                    sector_chgs.append(chg)
                    
                    # 3-Day Trend Logic (From v2)
                    is_falling_3d = (prices[-2] < prices[-3] < prices[-4])
                    is_rising_3d = (prices[-2] > prices[-3] > prices[-4])
                    
                    if is_falling_3d: self.drastic_tree.insert("", "end", values=(s, "৩ দিন পতন 📉"))
                    elif is_rising_3d: self.drastic_tree.insert("", "end", values=(s, "৩ দিন উত্থান 📈"))

                    # Signal Logic
                    sig = "-"
                    if chg >= 2.0 and not is_falling_3d: sig = "BUY"
                    elif chg <= -2.0 and not is_rising_3d: sig = "SELL"
                    
                    if sig != "-":
                        self.sig_tree.insert("", "end", values=(s, ltp, sig))
                except: continue
            
            if sector_chgs:
                avg = round(sum(sector_chgs)/len(sector_chgs), 2)
                bar = "█" * int(abs(avg) * 5) if abs(avg) > 0 else ""
                self.sec_tree.insert("", "end", values=(sector, f"{avg}%", bar))

        self.scan_btn.config(text="SCAN MARKET", state="normal")

if __name__ == "__main__":
    root = tk.Tk()
    app = HaridasMobileV2(root)
    root.mainloop()
