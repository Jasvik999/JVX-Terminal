"""
JVX-BlackMagic Hybrid Terminal v34.0 - LIVE YFINANCE EDITION
Features: Real Market Data + Live News + SQLite DB + True Net-PnL + Pro UI
"""

import streamlit as st
import pandas as pd
import numpy as np
import hashlib
import sqlite3
import math
from datetime import datetime, timedelta
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import yfinance as yf

st.set_page_config(page_title="JVX Ultimate v34.0", layout="wide", page_icon="📈")

# ==========================================
# 0. DATABASE & TAX ENGINE INITIALIZATION
# ==========================================
conn = sqlite3.connect('jvx_trading.db', check_same_thread=False)
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS trades (id INTEGER PRIMARY KEY AUTOINCREMENT, symbol TEXT, side TEXT, entry REAL, exit REAL, qty INTEGER, gross_pnl REAL, taxes REAL, net_pnl REAL, time TEXT)''')
conn.commit()

def calculate_taxes(entry, exit_price, qty):
    turnover = (entry + exit_price) * qty
    brokerage = 40.0 # ₹20 Buy, ₹20 Sell
    stt = turnover * 0.00125 if turnover > 0 else 0
    exchange_txn = turnover * 0.0000325
    gst = (brokerage + exchange_txn) * 0.18
    sebi_charges = turnover * 0.000001
    stamp_duty = (entry * qty) * 0.00015
    total_tax = round(brokerage + stt + exchange_txn + gst + sebi_charges + stamp_duty, 2)
    gross_pnl = (exit_price - entry) * qty
    net_pnl = round(gross_pnl - total_tax, 2)
    return total_tax, net_pnl

def save_trade(sym, side, entry, exit_price, qty):
    gross = (exit_price - entry) * qty
    if side == "SELL": gross = -gross
    tax, net = calculate_taxes(entry, exit_price, qty)
    t = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute("INSERT INTO trades (symbol, side, entry, exit, qty, gross_pnl, taxes, net_pnl, time) VALUES (?,?,?,?,?,?,?,?,?)", 
              (sym, side, entry, exit_price, qty, round(gross,2), tax, net, t))
    conn.commit()

# ==========================================
# 1. CSS & THEME
# ==========================================
DARK_CSS = """
<style>
    @keyframes gradientBG { 0% { background-position: 0% 50%; } 50% { background-position: 100% 50%; } 100% { background-position: 0% 50%; } }
    @keyframes pulse-green { 0% { box-shadow: 0 0 0 0 rgba(0,200,83,0.7); } 70% { box-shadow: 0 0 0 10px rgba(0,200,83,0); } 100% { box-shadow: 0 0 0 0 rgba(0,200,83,0); } }
    @keyframes pulse-red { 0% { box-shadow: 0 0 0 0 rgba(255,23,68,0.7); } 70% { box-shadow: 0 0 0 10px rgba(255,23,68,0); } 100% { box-shadow: 0 0 0 0 rgba(255,23,68,0); } }
    @keyframes blink { 0%,100% { opacity: 1; } 50% { opacity: 0.3; } }
    .main .block-container { background: linear-gradient(-45deg, #0e1117, #1a1f2e, #0e1117, #151b2b); background-size: 400% 400%; animation: gradientBG 15s ease infinite; }
    .live-dot { display: inline-block; width: 10px; height: 10px; background-color: #00c853; border-radius: 50%; animation: blink 1.5s infinite; margin-right: 8px; }
    .signal-buy { animation: pulse-green 2s infinite; border-radius: 8px; padding: 4px 12px; font-weight: bold; color: #00c853 !important; }
    .signal-sell { animation: pulse-red 2s infinite; border-radius: 8px; padding: 4px 12px; font-weight: bold; color: #ff1744 !important; }
    .fade-in { animation: fadeIn 0.6s ease-out; }
    .news-card { background: rgba(255,255,255,0.03); border-left: 3px solid #00d4aa; border-radius: 0 8px 8px 0; padding: 12px 16px; margin-bottom: 10px; transition: all 0.3s ease; }
    .metric-card { background: rgba(255,255,255,0.05); border-radius: 10px; padding: 15px; border: 1px solid rgba(255,255,255,0.1); text-align: center; }
</style>
"""
st.markdown(DARK_CSS, unsafe_allow_html=True)

# ==========================================
# 2. LOGIN GATE
# ==========================================
USERS = {"admin": hashlib.sha256("changeme123".encode()).hexdigest(), "hitesh": hashlib.sha256("jvx2026".encode()).hexdigest()}
if "authenticated" not in st.session_state: st.session_state.authenticated = False

if not st.session_state.authenticated:
    c1, c2, c3 = st.columns([1, 1.5, 1])
    with c2:
        st.markdown("<div style='text-align: center;'><h1 style='color: #00d4aa;'>📈 JVX BlackMagic Hybrid</h1><p style='color: #888;'>TERMINAL v34.0 // LIVE YFINANCE EDITION</p></div>", unsafe_allow_html=True)
        with st.form("login_form"):
            user = st.text_input("Username")
            pwd = st.text_input("Password", type="password")
            if st.form_submit_button("🔐 Secure Login", use_container_width=True):
                if USERS.get(user) == hashlib.sha256(pwd.encode()).hexdigest():
                    st.session_state.authenticated = True
                    st.session_state.username = user
                    st.rerun()
                else: st.error("❌ Invalid credentials!")
    st.stop()

# ==========================================
# 3. YFINANCE LIVE DATA ENGINE
# ==========================================
YF_TICKERS = {
    "NIFTY 50": "^NSEI", "BANKNIFTY": "^NSEBANK", "RELIANCE": "RELIANCE.NS", 
    "HDFCBANK": "HDFCBANK.NS", "INFY": "INFY.NS", "TCS": "TCS.NS", 
    "SBIN": "SBIN.NS", "
