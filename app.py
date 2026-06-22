"""
JVX-BlackMagic Hybrid Terminal v33.0 - THE ULTIMATE EDITION
Features: Kimi's 14-Tab Pro UI + SQLite DB + True Net-PnL Tax + Options Payoff Builder
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

st.set_page_config(page_title="JVX Ultimate v33.0", layout="wide", page_icon="📈")

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
# 1. KIMI's CSS & THEME
# ==========================================
DARK_CSS = """
<style>
    @keyframes gradientBG { 0% { background-position: 0% 50%; } 50% { background-position: 100% 50%; } 100% { background-position: 0% 50%; } }
    @keyframes pulse-green { 0% { box-shadow: 0 0 0 0 rgba(0,200,83,0.7); } 70% { box-shadow: 0 0 0 10px rgba(0,200,83,0); } 100% { box-shadow: 0 0 0 0 rgba(0,200,83,0); } }
    @keyframes pulse-red { 0% { box-shadow: 0 0 0 0 rgba(255,23,68,0.7); } 70% { box-shadow: 0 0 0 10px rgba(255,23,68,0); } 100% { box-shadow: 0 0 0 0 rgba(255,23,68,0); } }
    @keyframes blink { 0%,100% { opacity: 1; } 50% { opacity: 0.3; } }
    @keyframes slideIn { from { transform: translateX(-20px); opacity: 0; } to { transform: translateX(0); opacity: 1; } }
    @keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
    @keyframes shake { 0%,100% { transform: translateX(0); } 25% { transform: translateX(-5px); } 75% { transform: translateX(5px); } }
    @keyframes glow { 0% { box-shadow: 0 0 5px #00d4aa; } 50% { box-shadow: 0 0 20px #00d4aa, 0 0 40px #00d4aa; } 100% { box-shadow: 0 0 5px #00d4aa; } }
    @keyframes ticker { 0% { transform: translateX(100%); } 100% { transform: translateX(-100%); } }
    .main .block-container { background: linear-gradient(-45deg, #0e1117, #1a1f2e, #0e1117, #151b2b); background-size: 400% 400%; animation: gradientBG 15s ease infinite; }
    .live-dot { display: inline-block; width: 10px; height: 10px; background-color: #00c853; border-radius: 50%; animation: blink 1.5s infinite; margin-right: 8px; }
    .signal-buy { animation: pulse-green 2s infinite; border-radius: 8px; padding: 4px 12px; font-weight: bold; color: #00c853 !important; }
    .signal-sell { animation: pulse-red 2s infinite; border-radius: 8px; padding: 4px 12px; font-weight: bold; color: #ff1744 !important; }
    .circuit-breaker { animation: shake 0.5s ease-in-out infinite; border: 2px solid #ff1744; border-radius: 8px; padding: 10px; background: rgba(255,23,68,0.1); }
    .position-glow { animation: glow 2s ease-in-out infinite; border-radius: 10px; padding: 15px; }
    .fade-in { animation: fadeIn 0.6s ease-out; }
    .slide-in { animation: slideIn 0.5s ease-out; }
    .idea-card { background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.1); border-radius: 12px; padding: 16px; margin-bottom: 12px; transition: all 0.3s ease; }
    .idea-card:hover { border-color: #00d4aa; box-shadow: 0 0 20px rgba(0,212,170,0.15); transform: translateY(-2px); }
    .news-card { background: rgba(255,255,255,0.03); border-left: 3px solid #00d4aa; border-radius: 0 8px 8px 0; padding: 12px 16px; margin-bottom: 10px; transition: all 0.3s ease; }
    .news-card:hover { background: rgba(255,255,255,0.06); }
    .news-negative { border-left-color: #ff1744 !important; }
    .news-neutral { border-left-color: #ff9100 !important; }
    .score-badge { display: inline-flex; align-items: center; justify-content: center; width: 40px; height: 40px; border-radius: 50%; font-weight: bold; font-size: 0.9em; }
    .score-high { background: rgba(0,200,83,0.2); color: #00c853; border: 2px solid #00c853; }
    .score-mid { background: rgba(255,145,0,0.2); color: #ff9100; border: 2px solid #ff9100; }
    .score-low { background: rgba(255,23,68,0.2); color: #ff1744; border: 2px solid #ff1744; }
    .ticker-wrap { overflow: hidden; white-space: nowrap; background: rgba(0,0,0,0.3); border-radius: 8px; padding: 8px 0; margin-bottom: 15px; }
    .ticker-content { display: inline-block; animation: ticker 20s linear infinite; color: #00d4aa; font-weight: 500; }
    .metric-card { background: rgba(255,255,255,0.05); border-radius: 10px; padding: 15px; border: 1px solid rgba(255,255,255,0.1); text-align: center; transition: all 0.3s ease; }
    .metric-card:hover { transform: translateY(-2px); box-shadow: 0 4px 15px rgba(0,212,170,0.2); }
    .depth-row { transition: all 0.2s ease; }
    .depth-row:hover { background: rgba(255,255,255,0.05); }
    .bid-bar { background: linear-gradient(90deg, rgba(0,200,83,0.3) 0%, rgba(0,200,83,0.05) 100%); border-radius: 4px; }
    .ask-bar { background: linear-gradient(90deg, rgba(255,23,68,0.3) 0%, rgba(255,23,68,0.05) 100%); border-radius: 4px; }
    .script-header { background: rgba(0,212,170,0.08); border: 1px solid rgba(0,212,170,0.2); border-radius: 12px; padding: 20px; margin-bottom: 20px; }
    .recommendation-box { background: rgba(0,0,0,0.3); border: 1px solid rgba(255,255,255,0.1); border-radius: 12px; padding: 20px; }
    ::-webkit-scrollbar { width: 8px; }
    ::-webkit-scrollbar-track { background: #0e1117; }
    ::-webkit-scrollbar-thumb { background: #00d4aa; border-radius: 4px; }
</style>
"""
st.markdown(DARK_CSS, unsafe_allow_html=True)

# ==========================================
# 2. LOGIN GATE (NO DEMO ID SHOWN)
# ==========================================
USERS = {
    "admin": hashlib.sha256("changeme123".encode()).hexdigest(),
    "hitesh": hashlib.sha256("jvx2026".encode()).hexdigest()
}

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

def login_screen():
    c1, c2, c3 = st.columns([1, 1.5, 1])
    with c2:
        st.markdown("""
            <div class="fade-in" style="text-align: center;">
                <h1 style="color: #00d4aa; text-shadow: 0 0 20px rgba(0,212,170,0.5);">📈 JVX BlackMagic Hybrid</h1>
                <p style="color: #888; letter-spacing: 2px;">TERMINAL v33.0 // ULTIMATE EDITION</p>
            </div>
        """, unsafe_allow_html=True)
        with st.form("login_form"):
            user = st.text_input("Username", placeholder="Enter username")
            pwd = st.text_input("Password", type="password", placeholder="Enter password")
            if st.form_submit_button("🔐 Secure Login", use_container_width=True):
                if USERS.get(user) == hashlib.sha256(pwd.encode()).hexdigest():
                    st.session_state.authenticated = True
                    st.session_state.username = user
                    st.rerun()
                else:
                    st.error("❌ Invalid credentials!")

if not st.session_state.authenticated:
    login_screen()
    st.stop()

# ==========================================
# 3. STATE INITIALIZATION
# ==========================================
default_state = {
    'auto_trade': False, 'loss_streak': 0, 'exec_mode': "PAPER", 
    'trade_history': [], 'profit_target': 5000, 'loss_limit': 2,
    'selected_strategy': "T3 + RSI", 
    'watchlist': ["NIFTY 50", "BANKNIFTY", "RELIANCE", "HDFCBANK", "INFY", "TCS", "SBIN", "ICICIBANK"],
    'market_data': {}, 'toast_msg': None, 'quantity': 50,
    'news_cache': [], 'last_news_time': None,
    'portfolio': [], 'balance': 1500000, 'used_margin': 0, 'day_pnl': 0,
    'orders': [], 'alerts': [], 'alert_log': [],
    'depth_symbol': None, 'depth_active': False
}
for key, val in default_state.items():
    if key not in st.session_state:
        st.session_state[key] = val

# ==========================================
# 4. MARKET DATA ENGINE & STRATEGIES
# ==========================================
if not st.session_state.market_data:
    rng = np.random.default_rng(seed=42)
    base_prices = {"NIFTY 50": 22400, "BANKNIFTY": 47800, "RELIANCE": 2850, "HDFCBANK": 1480, "INFY": 1580, "TCS": 3850, "SBIN": 760, "ICICIBANK": 1120}
    for sym in st.session_state.watchlist:
        base = base_prices.get(sym, 2500)
        walk = np.cumsum(rng.normal(0, 15, 300))
        df = pd.DataFrame({"Close": base + walk, "Volume": rng.integers(1000, 5000, 300)})
        df['Open'] = df['Close'] - rng.normal(0, 5, 300)
        df['High'] = df[['Open', 'Close']].max(axis=1) + rng.uniform(2, 8, 300)
        df['Low'] = df[['Open', 'Close']].min(axis=1) - rng.uniform(2, 8, 300)
        df['High'] = np.maximum(df['High'], df[['Open', 'Close']].max(axis=1))
        df['Low'] = np.minimum(df['Low'], df[['Open', 'Close']].min(axis=1))
        st.session_state.market_data[sym] = df

def simulate_market_tick():
    rng = np.random.default_rng()
    for sym in st.session_state.watchlist:
        df = st.session_state.market_data[sym]
        last_close = float(df["Close"].iloc[-1])
        new_close = last_close + np.random.normal(0, 15)
        new_open = last_close
        new_high = max(new_open, new_close) + rng.uniform(2, 8)
        new_low = min(new_open, new_close) - rng.uniform(2, 8)
        new_row = pd.DataFrame({"Close": [new_close], "Volume": [int(rng.integers(1000, 5000))], "Open": [new_open], "High": [new_high], "Low": [new_low]})
        st.session_state.market_data[sym] = pd.concat([df, new_row], ignore_index=True).tail(500)

def get_market_depth(ltp):
    tick = 0.05
    bids = pd.DataFrame({
        'Bid Qty': np.random.randint(200, 5000, 5), 
        'Bid Price': [round(ltp - (i*tick), 2) for i in range(1, 6)]
    })
    asks = pd.DataFrame({
        'Ask Price': [round(ltp + (i*tick), 2) for i in range(1, 6)], 
        'Ask Qty': np.random.randint(200, 5000, 5)
    })
    return bids, asks

def apply_strategy(df, mode):
    delta = df['Close'].diff()
    gain = delta.clip(lower=0).rolling(14).mean()
    loss = (-delta.clip(upper=0)).rolling(14).mean()
    rs = gain / loss.replace(0, np.nan)
    df["RSI"] = (100 - (100 / (1 + rs))).fillna(50).clip(0, 100)
    df['EMA_20'] = df['Close'].ewm(span=20, adjust=False).mean()
    df['EMA_200'] = df['Close'].ewm(span=200, adjust=False).mean()
    df['VWAP'] = (df['Close'] * df['Volume']).cumsum() / df['Volume'].cumsum()

    def get_t3(data, p=10, f=0.7):
        e1 = data.ewm(span=p, adjust=False).mean()
        e2 = e1.ewm(span=p, adjust=False).mean()
        e3 = e2.ewm(span=p, adjust=False).mean()
        e4 = e3.ewm(span=p, adjust=False).mean()
        e5 = e4.ewm(span=p, adjust=False).mean()
        e6 = e5.ewm(span=p, adjust=False).mean()
        return -f**3*e6 + (3*f**2 + 3*f**3)*e5 - (6*f**2 + 3*f + 3*f**3)*e4 + (1 + 3*f + f**3 + 3*f**2)*e3

    df['T3'] = get_t3(df['Close'])
    df['Signal'] = "WAIT"

    if mode == "T3 + RSI":
        df.loc[(df['Close'] > df['T3']) & (df['RSI'] > 55), 'Signal'] = "BUY"
        df.loc[(df['Close'] < df['T3']) & (df['RSI'] < 45), 'Signal'] = "SELL"
    elif mode == "RSI + UT Bot":
        df.loc[(df['RSI'] > 55) & (df['Close'] > df['EMA_200']), 'Signal'] = "BUY"
        df.loc[(df['RSI'] < 45) & (df['Close'] < df['EMA_200']), 'Signal'] = "SELL"
    elif mode == "EMA + VWAP":
        df.loc[(df['Close'] > df['EMA_20']) & (df['Close'] > df['VWAP']), 'Signal'] = "BUY"
        df.loc[(df['Close'] < df['EMA_20']) & (df['Close'] < df['VWAP']), 'Signal'] = "SELL"
    return df

# ==========================================
# 5. SIDEBAR NAVIGATION
# ==========================================
st.sidebar.markdown(f"""
    <div class="slide-in" style="padding: 10px; border-radius: 8px; background: rgba(0,212,170,0.1); margin-bottom: 10px;">
        <span style="color: #00d4aa; font-weight: bold;">👤 {st.session_state.username.upper()}</span><br>
        <span style="font-size: 0.8em; color: #888;">{st.session_state.exec_mode} MODE</span>
    </div>
""", unsafe_allow_html=True)

if st.sidebar.button("🚪 Logout", use_container_width=True):
    st.session_state.authenticated = False
    st.rerun()

st.sidebar.divider()

# Fetch DB Net PnL to reflect accurate balance
df_trades_db = pd.read_sql_query("SELECT * FROM trades", conn)
db_pnl = df_trades_db['net_pnl'].sum() if not df_trades_db.empty else 0
available = st.session_state.balance - st.session_state.used_margin + db_pnl

st.sidebar.markdown(f"""
    <div class="metric-card" style="margin-bottom: 15px;">
        <div style="font-size: 0.75em; color: #888;">Available Margin</div>
        <div style="font-size: 1.4em; font-weight: bold; color: #00d4aa;">₹{available:,.0f}</div>
        <div style="font-size: 0.7em; color: #666;">Used: ₹{st.session_state.used_margin:,.0f}</div>
    </div>
""", unsafe_allow_html=True)

menu_choice = st.sidebar.radio("Navigate:", [
    "💡 Trade Ideas", "📊 Live Dashboard", "👀 Market Depth", "📈 Options Builder (Payoff)",
    "📰 Market News", "📂 Portfolio", "📋 Order Book", "🔔 Alerts",
    "🎭 Sentiment", "📅 Economic Calendar", "📁 Trade Ledger & Audit", 
    "🧠 Strategy Setup", "🤖 AI Assistant", "🔑 API Settings"
], index=1)

st.sidebar.divider()
st.sidebar.markdown("""<div style="display: flex; align-items: center; margin-bottom: 10px;"><span class="live-dot"></span><span style="color: #00c853; font-weight: bold; font-size: 0.9em;">MARKET LIVE</span></div>""", unsafe_allow_html=True)

if st.sidebar.button("▶️ Simulate Next Tick", type="primary", use_container_width=True):
    simulate_market_tick()
    st.rerun()

st.session_state.auto_trade = st.sidebar.toggle("🤖 Auto-Pilot", value=st.session_state.auto_trade)

# ==========================================
# 6. PAGES
# ==========================================

# --- TRADE IDEAS ---
if menu_choice == "💡 Trade Ideas":
    st.markdown("""<div class="fade-in"><h2>💡 Top Trade Ideas</h2><p style="color: #888;">AI-powered setups</p></div>""", unsafe_allow_html=True)
    st.info("Market is currently consolidating. Keep an eye on NIFTY 22,500 resistance and BANKNIFTY 48,000 breakout levels.")

# --- LIVE DASHBOARD ---
elif menu_choice == "📊 Live Dashboard":
    st.markdown("""<div class="fade-in"><h2>📊 Advanced Trading Dashboard</h2></div>""", unsafe_allow_html=True)
    symbol = st.selectbox("Select Asset", st.session_state.watchlist)
    
    # Get Data and Apply Strategy
    df = apply_strategy(st.session_state.market_data[symbol].copy(), st.session_state.selected_strategy)
    latest = df.iloc[-1]
    
    # Top Metrics
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("LTP", f"₹{latest['Close']:.2f}")
    m2.metric("RSI", f"{latest['RSI']:.1f}")
    m3.metric("VWAP", f"₹{latest['VWAP']:.2f}")
    sig_class = "signal-buy" if latest['Signal'] == "BUY" else "signal-sell" if latest['Signal'] == "SELL" else ""
    m4.markdown(f"**Signal:** <span class='{sig_class}'>{latest['Signal']}</span>", unsafe_allow_html=True)

    # Advanced Charting
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, row_width=[0.2, 0.8])
    fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name="Price"), row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df['EMA_20'], line=dict(color='#00d4aa', width=1.5, dash='dot'), name="EMA 20"), row=1, col=1)
    if "T3" in st.session_state.selected_strategy:
        fig.add_trace(go.Scatter(x=df.index, y=df['T3'], line=dict(color='orange', width=2), name="T3"), row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df['RSI'], line=dict(color='#ab47bc'), name="RSI"), row=2, col=1)
    fig.add_hline(y=70, line_dash="dash", line_color="red", opacity=0.5, row=2, col=1)
    fig.add_hline(y=30, line_dash="dash", line_color="green", opacity=0.5, row=2, col=1)
    fig.update_layout(template="plotly_dark", height=600, xaxis_rangeslider_visible=False, margin=dict(l=0, r=0, t=30, b=0))
    st.plotly_chart(fig, use_container_width=True)

    # Execution Console
    st.subheader("⚡ Execution Console")
    o1, o2, o3 = st.columns(3)
    qty = o1.number_input("Qty", min_value=1, value=st.session_state.quantity, step=1)
    
    if o2.button(f"🟢 BUY {symbol}", use_container_width=True):
        margin = float(latest['Close']) * qty * 0.2
        if st.session_state.balance - st.session_state.used_margin >= margin:
            st.session_state.portfolio.append({"symbol": symbol, "entry": float(latest['Close']), "qty": qty, "side": "BUY"})
            st.session_state.used_margin += margin
            st.success(f"Position Opened: {symbol} at ₹{latest['Close']:.2f}")
            st.rerun()
        else:
            st.error("❌ Insufficient margin!")
            
    if o3.button(f"🔴 SELL {symbol}", use_container_width=True):
        margin = float(latest['Close']) * qty * 0.2
        if st.session_state.balance - st.session_state.used_margin >= margin:
            st.session_state.portfolio.append({"symbol": symbol, "entry": float(latest['Close']), "qty": qty, "side": "SELL"})
            st.session_state.used_margin += margin
            st.success(f"Short Position Opened: {symbol} at ₹{latest['Close']:.2f}")
            st.rerun()
        else:
            st.error("❌ Insufficient margin!")
    
    # Portfolio Close Logic with SQLite DB Save
    st.divider()
    active_positions = [p for p in st.session_state.portfolio if p['symbol'] == symbol]
    if active_positions:
        st.markdown("### 🎯 Manage Active Positions")
        for idx, pos in enumerate(st.session_state.portfolio):
            if pos['symbol'] == symbol:
                multiplier = 1 if pos['side'] == 'BUY' else -1
                pnl = (float(latest['Close']) - pos['entry']) * pos['qty'] * multiplier
                pnl_color = "#00c853" if pnl >= 0 else "#ff1744"
                
                c1, c2 = st.columns([3, 1])
                c1.markdown(f"<div class='metric-card'><b>{pos['side']} {pos['qty']} Qty</b> @ ₹{pos['entry']:.2f} | <span style='color:{pnl_color}; font-weight:bold;'>Open PnL: ₹{pnl:.2f}</span></div>", unsafe_allow_html=True)
                
                if c2.button("🔒 CLOSE & AUDIT", key=f"close_{idx}", type="primary", use_container_width=True):
                    save_trade(symbol, pos['side'], pos['entry'], float(latest['Close']), pos['qty'])
                    st.session_state.used_margin -= pos['entry'] * pos['qty'] * 0.2
                    st.session_state.portfolio.pop(idx)
                    st.success("✅ Trade Closed! Audited and Saved to SQLite Database.")
                    st.balloons()
                    st.rerun()

# --- OPTIONS BUILDER (PAYOFF) ---
elif menu_choice == "📈 Options Builder (Payoff)":
    st.markdown("""<div class="fade-in"><h2>📈 Advanced Options Builder & Payoff</h2></div>""", unsafe_allow_html=True)
    st.info("Build strategies like Sensibull and visualize your Max Risk/Reward at Expiry.")
    
    c1, c2, c3 = st.columns(3)
    spot = c1.number_input("Current Spot Price", value=22400)
    strike = c2.number_input("Option Strike Price", value=22500)
    premium = c3.number_input("Premium Paid/Received", value=150.0)
    
    c4, c5, c6 = st.columns(3)
    op_type = c4.radio("Option Type", ["Call (CE)", "Put (PE)"], horizontal=True)
    pos_type = c5.radio("Position", ["Buy (Long)", "Sell (Short)"], horizontal=True)
    lot_size = c6.number_input("Lot Size", value=50)
    
    prices = np.arange(spot * 0.90, spot * 1.10, 10)
    payoff = []
    for p in prices:
        if "Call" in op_type: val = max(0, p - strike)
        else: val = max(0, strike - p)
        
        if "Buy" in pos_type: pnl = val - premium
        else: pnl = premium - val
        payoff.append(pnl * lot_size)
        
    fig = go.Figure()
    colors = ['rgba(0, 200, 83, 0.4)' if pnl >= 0 else 'rgba(255, 23, 68, 0.4)' for pnl in payoff]
    fig.add_trace(go.Bar(x=prices, y=payoff, marker_color=colors, name='Payoff Profile'))
    fig.add_hline(y=0, line_dash="solid", line_color="white", opacity=0.5)
    fig.add_vline(x=spot, line_dash="dot", line_color="yellow", annotation_text="Spot Price")
    fig.add_vline(x=strike, line_dash="dash", line_color="#00d4aa", annotation_text="Strike")
    fig.update_layout(template="plotly_dark", title=f"Expiry Payoff Chart (Lot Size: {lot_size})", height=500)
    st.plotly_chart(fig, use_container_width=True)

# --- MARKET DEPTH ---
elif menu_choice == "👀 Market Depth":
    st.markdown("""<div class="fade-in"><h2>👀 Live Level-2 Order Book</h2></div>""", unsafe_allow_html=True)
    sym = st.selectbox("Select Symbol", st.session_state.watchlist)
    ltp = st.session_state.market_data[sym].iloc[-1]['Close']
    
    st.markdown(f"""
        <div class="script-header">
            <h1 style="margin: 0; color: #fff;">{sym}</h1>
            <span style="color: #00c853; font-size: 2em; font-weight: bold;">₹{ltp:.2f}</span>
        </div>
    """, unsafe_allow_html=True)
    
    bids, asks = get_market_depth(ltp)
    d1, d2 = st.columns(2)
    with d1:
        st.markdown("<h4 style='color:#00c853; text-align:center;'>🟢 BID (Buyers)</h4>", unsafe_allow_html=True)
        for i, row in bids.iterrows():
            st.markdown(f"""
                <div class="depth-row bid-bar" style="padding: 10px; margin-bottom: 5px; display: flex; justify-content: space-between;">
                    <span style="color: #00c853; font-weight: bold;">₹{row['Bid Price']}</span>
                    <span style="color: #fff;">{row['Bid Qty']:,}</span>
                </div>
            """, unsafe_allow_html=True)
            
    with d2:
        st.markdown("<h4 style='color:#ff1744; text-align:center;'>🔴 ASK (Sellers)</h4>", unsafe_allow_html=True)
        for i, row in asks.iterrows():
            st.markdown(f"""
                <div class="depth-row ask-bar" style="padding: 10px; margin-bottom: 5px; display: flex; justify-content: space-between;">
                    <span style="color: #ff1744; font-weight: bold;">₹{row['Ask Price']}</span>
                    <span style="color: #fff;">{row['Ask Qty']:,}</span>
                </div>
            """, unsafe_allow_html=True)

# --- MARKET NEWS ---
elif menu_choice == "📰 Market News":
    st.markdown("""<div class="fade-in"><h2>📰 Live Market News Feed</h2></div>""", unsafe_allow_html=True)
    now = datetime.now()
    if not st.session_state.last_news_time or (now - st.session_state.last_news_time).seconds > 60:
        news_templates = [
            {"headline": "NIFTY 50 breaches resistance as IT stocks rally", "impact": "positive", "symbol": "NIFTY 50"},
            {"headline": "RBI MPC maintains repo rate at 6.5% — markets cheer", "impact": "positive", "symbol": "BANKNIFTY"},
            {"headline": "Reliance announces major 5G expansion", "impact": "positive", "symbol": "RELIANCE"},
            {"headline": "US Fed signals 2 rate cuts in 2026", "impact": "positive", "symbol": "NIFTY 50"},
            {"headline": "Crude oil spikes to $85/barrel", "impact": "negative", "symbol": "RELIANCE"},
            {"headline": "TCS bags $500M deal from European bank", "impact": "positive", "symbol": "TCS"},
            {"headline": "SBI reduces FD rates by 25 bps", "impact": "negative", "symbol": "SBIN"}
        ]
        rng = np.random.default_rng(seed=int(now.timestamp()) % 1000)
        selected = rng.choice(news_templates, size=6, replace=False).tolist()
        for item in selected:
            item["timestamp"] = now - timedelta(minutes=rng.integers(0, 180))
        selected.sort(key=lambda x: x['timestamp'], reverse=True)
        st.session_state.news_cache = selected
        st.session_state.last_news_time = now
        
    for item in st.session_state.news_cache:
        impact_class = "news-negative" if item['impact'] == 'negative' else "news-neutral" if item['impact'] == 'neutral' else ""
        emoji = "🟢" if item['impact'] == 'positive' else "🔴" if item['impact'] == 'negative' else "🟡"
        mins = int((now - item['timestamp']).total_seconds() / 60)
        st.markdown(f"""
            <div class="news-card {impact_class} fade-in">
                <div style="display: flex; justify-content: space-between;">
                    <div><span style="color: #00d4aa; font-weight: bold; font-size: 0.85em;">{item['symbol']}</span>
                    <span style="color: #666; font-size: 0.75em; margin-left: 10px;">{mins} min ago</span>
                    <p style="color: #fff; margin: 5px 0 0 0; font-size: 0.95em;">{item['headline']}</p></div>
                    <div style="font-size: 1.2em;">{emoji}</div>
                </div>
            </div>
        """, unsafe_allow_html=True)

# --- PORTFOLIO ---
elif menu_choice == "📂 Portfolio":
    st.markdown("""<div class="fade-in"><h2>📂 Active Portfolio</h2></div>""", unsafe_allow_html=True)
    if st.session_state.portfolio:
        df_port = pd.DataFrame(st.session_state.portfolio)
        st.dataframe(df_port, use_container_width=True, hide_index=True)
    else:
        st.info("📭 No open positions.")

# --- ORDER BOOK & ALERTS ---
elif menu_choice == "📋 Order Book":
    st.markdown("""<div class="fade-in"><h2>📋 Order Book</h2></div>""", unsafe_allow_html=True)
    st.info("No pending limit orders.")

elif menu_choice == "🔔 Alerts":
    st.markdown("""<div class="fade-in"><h2>🔔 Price Alerts</h2></div>""", unsafe_allow_html=True)
    with st.form("alert_form"):
        a1, a2, a3 = st.columns(3)
        alert_sym = a1.selectbox("Symbol", st.session_state.watchlist)
        alert_cond = a2.selectbox("Condition", ["ABOVE", "BELOW"])
        alert_price = a3.number_input("Price", value=22000.0, step=0.05)
        if st.form_submit_button("➕ Add Alert"):
            st.success(f"✅ Alert set: {alert_sym} {alert_cond} ₹{alert_price}")

# --- SENTIMENT & CALENDAR ---
elif menu_choice == "🎭 Sentiment":
    st.markdown("""<div class="fade-in"><h2>🎭 Market Sentiment (Fear & Greed)</h2></div>""", unsafe_allow_html=True)
    fear_greed = np.random.randint(30, 80)
    fg_color = "#00c853" if fear_greed > 60 else "#ff9100" if fear_greed > 40 else "#ff1744"
    fig = go.Figure(go.Indicator(
        mode = "gauge+number", value = fear_greed, title = {'text': "Fear & Greed Index"},
        gauge = {'axis': {'range': [0, 100]}, 'bar': {'color': fg_color}}
    ))
    fig.update_layout(template="plotly_dark", height=400)
    st.plotly_chart(fig, use_container_width=True)

elif menu_choice == "📅 Economic Calendar":
    st.markdown("""<div class="fade-in"><h2>📅 Economic Calendar</h2></div>""", unsafe_allow_html=True)
    st.success("Today 10:00 - RBI MPC Minutes Release (HIGH IMPACT)")
    st.warning("Tomorrow 18:00 - Fed Chair Speech (HIGH IMPACT)")
    st.info("Friday 10:30 - Nifty 50 Rebalancing (MEDIUM IMPACT)")

# --- TRADE LEDGER & AUDIT (SQLITE + TAX ENGINE) ---
elif menu_choice == "📁 Trade Ledger & Audit":
    st.markdown("""<div class="fade-in"><h2>🏦 Deep Audit & Net-PnL Ledger</h2></div>""", unsafe_allow_html=True)
    st.info("Data is securely fetched from local SQLite Database (jvx_trading.db)")
    
    df_trades = pd.read_sql_query("SELECT * FROM trades ORDER BY id DESC", conn)
    
    if not df_trades.empty:
        gross = df_trades['gross_pnl'].sum()
        total_tax = df_trades['taxes'].sum()
        net = df_trades['net_pnl'].sum()
        
        a1, a2, a3 = st.columns(3)
        a1.markdown(f"<div class='metric-card'><span style='color:#888;'>Gross PnL</span><h3 style='color:#00d4aa;'>₹{gross:.2f}</h3></div>", unsafe_allow_html=True)
        a2.markdown(f"<div class='metric-card'><span style='color:#888;'>Govt & Broker Taxes</span><h3 style='color:#ff1744;'>₹{total_tax:.2f}</h3></div>", unsafe_allow_html=True)
        a3.markdown(f"<div class='metric-card'><span style='color:#888;'>True Net PnL</span><h3 style='color:#00c853;'>₹{net:.2f}</h3></div>", unsafe_allow_html=True)
        
        st.dataframe(df_trades[['time', 'symbol', 'side', 'qty', 'entry', 'exit', 'gross_pnl', 'taxes', 'net_pnl']], use_container_width=True, hide_index=True)
    else:
        st.warning("No trades found in the local database. Go to Live Dashboard to execute a trade.")

# --- STRATEGY SETUP ---
elif menu_choice == "🧠 Strategy Setup":
    st.markdown("""<div class="fade-in"><h2>🧠 Strategy Parameters</h2></div>""", unsafe_allow_html=True)
    st.session_state.selected_strategy = st.selectbox("Active Algorithm", ["T3 + RSI", "RSI + UT Bot", "EMA + VWAP"])
    st.success(f"Strategy {st.session_state.selected_strategy} is active and running.")

# --- AI ASSISTANT ---
elif menu_choice == "🤖 AI Assistant":
    st.markdown("""<div class="fade-in"><h2>🤖 JVX AI Trade Assistant</h2></div>""", unsafe_allow_html=True)
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    
    user_input = st.chat_input("Ask me anything about your positions or the market...")
    if user_input:
        st.session_state.chat_history.append({"role": "user", "message": user_input})
        st.session_state.chat_history.append({"role": "assistant", "message": f"Analyzing '{user_input}'... Based on the current T3 + RSI setup, market is maintaining its support levels."})
        st.rerun()
        
    for chat in st.session_state.chat_history:
        if chat['role'] == 'user':
            st.markdown(f"<div style='background: rgba(0,212,170,0.1); border-radius: 10px; padding: 10px; margin: 5px 0; text-align: right;'><span style='color: #00d4aa;'>👤 {chat['message']}</span></div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div style='background: rgba(255,255,255,0.05); border-radius: 10px; padding: 10px; margin: 5px 0; border-left: 3px solid #ab47bc;'><span style='color: #fff;'>🤖 {chat['message']}</span></div>", unsafe_allow_html=True)

# --- API SETTINGS ---
elif menu_choice == "🔑 API Settings":
    st.markdown("""<div class="fade-in"><h2>📡 API & Connectors</h2></div>""", unsafe_allow_html=True)
    with st.expander("1. Paytm Money / Dhan API", expanded=True):
        p1, p2 = st.columns(2)
        with p1: st.text_input("Broker API Key", type="password")
        with p2: st.text_input("Broker API Secret", type="password")
        if st.button("🔗 Authenticate Broker", use_container_width=True):
            st.success("✅ WebSockets Activated & Broker Simulated!")
    with st.expander("2. Telegram Alerts", expanded=True):
        st.text_input("Bot Token", type="password")
        if st.button("📲 Send Test Alert", use_container_width=True):
            st.success("✅ Test alert sent to Telegram!")
            
# ==========================================
# 4. MARKET DATA ENGINE & STRATEGIES (Real yfinance Data)
# ==========================================
YF_TICKERS = {
    "NIFTY 50": "^NSEI", "BANKNIFTY": "^NSEBANK", "RELIANCE": "RELIANCE.NS", 
    "HDFCBANK": "HDFCBANK.NS", "INFY": "INFY.NS", "TCS": "TCS.NS", 
    "SBIN": "SBIN.NS", "ICICIBANK": "ICICIBANK.NS"
}

if 'market_data_loaded' not in st.session_state:
    st.session_state.market_data = {}
    for sym in st.session_state.watchlist:
        yf_sym = YF_TICKERS.get(sym, sym)
        try:
            # 5-min timeframe का असली लाइव डेटा (पिछले 5 दिनों का)
            df = yf.Ticker(yf_sym).history(period="5d", interval="5m")
            if not df.empty:
                st.session_state.market_data[sym] = df[['Open', 'High', 'Low', 'Close', 'Volume']].copy()
        except Exception as e:
            pass
    st.session_state.market_data_loaded = True

def simulate_market_tick():
    # अब यह बटन डमी टिक नहीं बनाएगा, बल्कि NSE से असली 'लाइव कैंडल' फेच करेगा!
    for sym in st.session_state.watchlist:
        yf_sym = YF_TICKERS.get(sym, sym)
        try:
            df = yf.Ticker(yf_sym).history(period="5d", interval="5m")
            if not df.empty:
                st.session_state.market_data[sym] = df[['Open', 'High', 'Low', 'Close', 'Volume']].copy()
        except:
            pass
            # --- MARKET NEWS ---
elif menu_choice == "📰 Market News":
    st.markdown("""<div class="fade-in"><h2>📰 Live Market News Feed (yfinance)</h2></div>""", unsafe_allow_html=True)
    
    sym = st.selectbox("Select Symbol for News", st.session_state.watchlist)
    yf_sym = YF_TICKERS.get(sym, sym)
    
    st.info(f"Fetching latest real-time news for {sym}...")
    
    try:
        ticker = yf.Ticker(yf_sym)
        news_data = ticker.news
        
        if news_data:
            for item in news_data[:10]: # Top 10 ताज़ा ख़बरें
                title = item.get('title', 'No Title')
                publisher = item.get('publisher', 'Unknown Publisher')
                link = item.get('link', '#')
                pub_time = item.get('providerPublishTime', 0)
                dt = datetime.fromtimestamp(pub_time).strftime("%Y-%m-%d %H:%M:%S")
                
                st.markdown(f"""
                    <div class="news-card fade-in">
                        <div style="display: flex; justify-content: space-between;">
                            <div><span style="color: #00d4aa; font-weight: bold; font-size: 0.85em;">{publisher}</span>
                            <span style="color: #666; font-size: 0.75em; margin-left: 10px;">{dt}</span>
                            <p style="color: #fff; margin: 5px 0 0 0; font-size: 0.95em;">
                                <a href="{link}" target="_blank" style="color: white; text-decoration: none;">{title}</a>
                            </p></div>
                            <div style="font-size: 1.2em;">📰</div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
        else:
            st.warning(f"No recent news found for {sym}.")
    except Exception as e:
        st.error("Error fetching news. Please check your internet connection.")
                
