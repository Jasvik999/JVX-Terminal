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
    "SBIN": "SBIN.NS", "ICICIBANK": "ICICIBANK.NS"
}

default_state = {
    'exec_mode': "PAPER", 'selected_strategy': "T3 + RSI", 
    'watchlist': list(YF_TICKERS.keys()), 'quantity': 50,
    'portfolio': [], 'balance': 1500000, 'used_margin': 0
}
for key, val in default_state.items():
    if key not in st.session_state: st.session_state[key] = val

if 'market_data' not in st.session_state:
    st.session_state.market_data = {}
    for sym in st.session_state.watchlist:
        try:
            df = yf.Ticker(YF_TICKERS[sym]).history(period="5d", interval="5m")
            if not df.empty: st.session_state.market_data[sym] = df[['Open', 'High', 'Low', 'Close', 'Volume']].copy()
        except: pass

def simulate_market_tick():
    for sym in st.session_state.watchlist:
        try:
            df = yf.Ticker(YF_TICKERS[sym]).history(period="5d", interval="5m")
            if not df.empty: st.session_state.market_data[sym] = df[['Open', 'High', 'Low', 'Close', 'Volume']].copy()
        except: pass

def apply_strategy(df, mode):
    if len(df) < 20: return df
    df['EMA_20'] = df['Close'].ewm(span=20, adjust=False).mean()
    df['VWAP'] = (df['Close'] * df['Volume']).cumsum() / df['Volume'].cumsum()
    delta = df['Close'].diff()
    gain = delta.clip(lower=0).rolling(14).mean()
    loss = (-delta.clip(upper=0)).rolling(14).mean()
    rs = gain / loss.replace(0, np.nan)
    df["RSI"] = (100 - (100 / (1 + rs))).fillna(50).clip(0, 100)
    df['Signal'] = "WAIT"
    df.loc[(df['Close'] > df['EMA_20']) & (df['RSI'] > 55), 'Signal'] = "BUY"
    df.loc[(df['Close'] < df['EMA_20']) & (df['RSI'] < 45), 'Signal'] = "SELL"
    return df

# ==========================================
# 4. SIDEBAR
# ==========================================
st.sidebar.markdown(f"<span style='color: #00d4aa; font-weight: bold;'>👤 {st.session_state.username.upper()}</span>", unsafe_allow_html=True)
st.sidebar.divider()

menu_choice = st.sidebar.radio("Navigate:", [
    "📊 Live Dashboard", "📰 Market News", "📁 Trade Ledger & Audit", 
    "📈 Options Builder (Payoff)", "📂 Portfolio"
])

st.sidebar.divider()
st.sidebar.markdown("""<div style="display: flex; align-items: center;"><span class="live-dot"></span><span style="color: #00c853; font-weight: bold;">LIVE YFINANCE DATA</span></div>""", unsafe_allow_html=True)

if st.sidebar.button("🔄 Refresh Live Data", type="primary", use_container_width=True):
    simulate_market_tick()
    st.rerun()

# ==========================================
# 5. PAGES
# ==========================================

# --- LIVE DASHBOARD ---
if menu_choice == "📊 Live Dashboard":
    st.markdown("<h2>📊 Advanced Trading Dashboard</h2>", unsafe_allow_html=True)
    symbol = st.selectbox("Select Asset", st.session_state.watchlist)
    
    if symbol in st.session_state.market_data and not st.session_state.market_data[symbol].empty:
        df = apply_strategy(st.session_state.market_data[symbol].copy(), st.session_state.selected_strategy)
        latest = df.iloc[-1]
        
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("LTP", f"₹{latest['Close']:.2f}")
        m2.metric("RSI", f"{latest.get('RSI', 50):.1f}")
        m3.metric("VWAP", f"₹{latest.get('VWAP', latest['Close']):.2f}")
        sig_class = "signal-buy" if latest.get('Signal') == "BUY" else "signal-sell" if latest.get('Signal') == "SELL" else ""
        m4.markdown(f"**Signal:** <span class='{sig_class}'>{latest.get('Signal', 'WAIT')}</span>", unsafe_allow_html=True)

        fig = make_subplots(rows=2, cols=1, shared_xaxes=True, row_width=[0.2, 0.8])
        fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name="Price"), row=1, col=1)
        if 'EMA_20' in df: fig.add_trace(go.Scatter(x=df.index, y=df['EMA_20'], line=dict(color='#00d4aa'), name="EMA 20"), row=1, col=1)
        if 'RSI' in df: fig.add_trace(go.Scatter(x=df.index, y=df['RSI'], line=dict(color='#ab47bc'), name="RSI"), row=2, col=1)
        fig.update_layout(template="plotly_dark", height=600, xaxis_rangeslider_visible=False)
        st.plotly_chart(fig, use_container_width=True)

        st.subheader("⚡ Execution Console")
        o1, o2, o3 = st.columns(3)
        qty = o1.number_input("Qty", min_value=1, value=st.session_state.quantity, step=1)
        
        if o2.button(f"🟢 BUY {symbol}", use_container_width=True):
            st.session_state.portfolio.append({"symbol": symbol, "entry": float(latest['Close']), "qty": qty, "side": "BUY"})
            st.success(f"Position Opened: {symbol} at ₹{latest['Close']:.2f}")
            st.rerun()
                
        if o3.button(f"🔴 SELL {symbol}", use_container_width=True):
            st.session_state.portfolio.append({"symbol": symbol, "entry": float(latest['Close']), "qty": qty, "side": "SELL"})
            st.success(f"Short Position Opened: {symbol} at ₹{latest['Close']:.2f}")
            st.rerun()
            
        active_positions = [p for p in st.session_state.portfolio if p['symbol'] == symbol]
        if active_positions:
            for idx, pos in enumerate(st.session_state.portfolio):
                if pos['symbol'] == symbol:
                    multiplier = 1 if pos['side'] == 'BUY' else -1
                    pnl = (float(latest['Close']) - pos['entry']) * pos['qty'] * multiplier
                    pnl_color = "#00c853" if pnl >= 0 else "#ff1744"
                    c1, c2 = st.columns([3, 1])
                    c1.markdown(f"<div class='metric-card'><b>{pos['side']} {pos['qty']} Qty</b> @ ₹{pos['entry']:.2f} | <span style='color:{pnl_color}; font-weight:bold;'>Open PnL: ₹{pnl:.2f}</span></div>", unsafe_allow_html=True)
                    if c2.button("🔒 CLOSE & AUDIT", key=f"close_{idx}", type="primary", use_container_width=True):
                        save_trade(symbol, pos['side'], pos['entry'], float(latest['Close']), pos['qty'])
                        st.session_state.portfolio.pop(idx)
                        st.success("✅ Trade Closed & Audited in SQLite!")
                        st.rerun()
    else:
        st.warning("Loading Market Data from Yahoo Finance... Please click 'Refresh Live Data' on the sidebar.")

# --- LIVE MARKET NEWS ---
elif menu_choice == "📰 Market News":
    st.markdown("<h2>📰 Live Market News (Yahoo Finance)</h2>", unsafe_allow_html=True)
    sym = st.selectbox("Select Symbol for News", st.session_state.watchlist)
    st.info(f"Fetching latest real-time news for {sym}...")
    
    try:
        ticker = yf.Ticker(YF_TICKERS.get(sym, sym))
        news_data = ticker.news
        if news_data:
            for item in news_data[:10]:
                title = item.get('title', 'No Title')
                publisher = item.get('publisher', 'Unknown Publisher')
                link = item.get('link', '#')
                pub_time = item.get('providerPublishTime', 0)
                dt = datetime.fromtimestamp(pub_time).strftime("%Y-%m-%d %H:%M:%S") if pub_time else "Just Now"
                
                st.markdown(f"""
                    <div class="news-card">
                        <div style="display: flex; justify-content: space-between;">
                            <div><span style="color: #00d4aa; font-weight: bold; font-size: 0.85em;">{publisher}</span>
                            <span style="color: #666; font-size: 0
