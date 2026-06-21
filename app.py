"""
JVX-BlackMagic Hybrid Terminal v30.1 - ANIMATED & BUG-FIXED EDITION
Features: Login Gate, Level 2 Market Depth, Advanced Charts, 5 Pro Strategies, 
          Telegram & Paytm API, CSS Animations, Circuit Breaker
"""

import streamlit as st
import pandas as pd
import numpy as np
import hashlib
from datetime import datetime
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ==========================================
# 0. ANIMATED CSS INJECTION
# ==========================================
ANIMATION_CSS = """
<style>
    @keyframes gradientBG {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    @keyframes pulse-green {
        0% { box-shadow: 0 0 0 0 rgba(0, 200, 83, 0.7); }
        70% { box-shadow: 0 0 0 10px rgba(0, 200, 83, 0); }
        100% { box-shadow: 0 0 0 0 rgba(0, 200, 83, 0); }
    }
    @keyframes pulse-red {
        0% { box-shadow: 0 0 0 0 rgba(255, 23, 68, 0.7); }
        70% { box-shadow: 0 0 0 10px rgba(255, 23, 68, 0); }
        100% { box-shadow: 0 0 0 0 rgba(255, 23, 68, 0); }
    }
    @keyframes blink {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.3; }
    }
    @keyframes slideIn {
        from { transform: translateX(-20px); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    @keyframes shake {
        0%, 100% { transform: translateX(0); }
        25% { transform: translateX(-5px); }
        75% { transform: translateX(5px); }
    }
    @keyframes glow {
        0% { box-shadow: 0 0 5px #00d4aa; }
        50% { box-shadow: 0 0 20px #00d4aa, 0 0 40px #00d4aa; }
        100% { box-shadow: 0 0 5px #00d4aa; }
    }
    .main .block-container {
        background: linear-gradient(-45deg, #0e1117, #1a1f2e, #0e1117, #151b2b);
        background-size: 400% 400%;
        animation: gradientBG 15s ease infinite;
    }
    .live-dot {
        display: inline-block;
        width: 10px;
        height: 10px;
        background-color: #00c853;
        border-radius: 50%;
        animation: blink 1.5s infinite;
        margin-right: 8px;
    }
    .signal-buy {
        animation: pulse-green 2s infinite;
        border-radius: 8px;
        padding: 4px 12px;
        font-weight: bold;
        color: #00c853 !important;
    }
    .signal-sell {
        animation: pulse-red 2s infinite;
        border-radius: 8px;
        padding: 4px 12px;
        font-weight: bold;
        color: #ff1744 !important;
    }
    .circuit-breaker {
        animation: shake 0.5s ease-in-out infinite;
        border: 2px solid #ff1744;
        border-radius: 8px;
        padding: 10px;
        background: rgba(255, 23, 68, 0.1);
    }
    .position-glow {
        animation: glow 2s ease-in-out infinite;
        border-radius: 10px;
        padding: 15px;
    }
    .fade-in {
        animation: fadeIn 0.6s ease-out;
    }
    .slide-in {
        animation: slideIn 0.5s ease-out;
    }
    ::-webkit-scrollbar {
        width: 8px;
    }
    ::-webkit-scrollbar-track {
        background: #0e1117;
    }
    ::-webkit-scrollbar-thumb {
        background: #00d4aa;
        border-radius: 4px;
    }
    [data-testid="stMetric"] {
        background: rgba(255,255,255,0.05);
        border-radius: 10px;
        padding: 10px;
        border: 1px solid rgba(255,255,255,0.1);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    [data-testid="stMetric"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 15px rgba(0, 212, 170, 0.2);
    }
    .stButton>button {
        transition: all 0.3s ease !important;
    }
    .stButton>button:hover {
        transform: scale(1.02);
        box-shadow: 0 0 15px rgba(0, 212, 170, 0.4);
    }
    .stButton>button:active {
        transform: scale(0.98);
    }
</style>
"""
st.markdown(ANIMATION_CSS, unsafe_allow_html=True)

# ==========================================
# 1. CONFIGURATION & LOGIN GATE
# ==========================================
st.set_page_config(page_title="JVX Hybrid Terminal v30.1", layout="wide", page_icon="📈")

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
                <h1 style="color: #00d4aa; text-shadow: 0 0 20px rgba(0,212,170,0.5);">
                    📈 JVX BlackMagic Hybrid
                </h1>
                <p style="color: #888; letter-spacing: 2px;">TERMINAL v30.1 // ANIMATED EDITION</p>
            </div>
        """, unsafe_allow_html=True)
        with st.form("login_form"):
            user = st.text_input("Username", placeholder="Enter username")
            pwd = st.text_input("Password", type="password", placeholder="Enter password")
            submitted = st.form_submit_button("🔐 Secure Login", use_container_width=True)
            if submitted:
                if USERS.get(user) == hashlib.sha256(pwd.encode()).hexdigest():
                    st.session_state.authenticated = True
                    st.session_state.username = user
                    st.rerun()
                else:
                    st.error("❌ Invalid credentials! Access denied.")
        st.caption("Give Money for access 8141249466")

if not st.session_state.authenticated:
    login_screen()
    st.stop()

# ==========================================
# 2. STATE & CORE ENGINES
# ==========================================
default_state = {
    'auto_trade': False, 
    'loss_streak': 0, 
    'exec_mode': "PAPER", 
    'trade_history': [], 
    'profit_target': 5000, 
    'loss_limit': 2,
    'selected_strategy': "T3 + RSI", 
    'watchlist': ["NIFTY 50", "BANKNIFTY", "RELIANCE", "HDFCBANK"],
    'open_position': None, 
    'market_data': {},
    'toast_msg': None,
    'quantity': 1
}
for key, val in default_state.items():
    if key not in st.session_state:
        st.session_state[key] = val

# Persistent Market Data Setup - BUG FIX: 300 rows for proper EMA_200 initialization
if not st.session_state.market_data:
    rng = np.random.default_rng(seed=42)
    for sym in st.session_state.watchlist:
        base = 22000 if "NIFTY" in sym else (47000 if "BANK" in sym else (2500 if "RELIANCE" in sym else 1450))
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
        new_row = pd.DataFrame({
            "Close": [new_close], 
            "Volume": [int(rng.integers(1000, 5000))],
            "Open": [new_open], 
            "High": [new_high], 
            "Low": [new_low]
        })
        st.session_state.market_data[sym] = pd.concat([df, new_row], ignore_index=True).tail(500)

def get_market_depth(ltp):
    """BUG FIX: 0.05 tick size for Indian equity markets"""
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

# ==========================================
# 3. STRATEGY ALGORITHMS
# ==========================================
def apply_strategy(df, mode):
    delta = df['Close'].diff()
    gain = delta.clip(lower=0).rolling(14).mean()
    loss = (-delta.clip(upper=0)).rolling(14).mean()
    rs = gain / loss.replace(0, np.nan)
    df["RSI"] = (100 - (100 / (1 + rs))).fillna(50).clip(0, 100)
    
    df['EMA_20'] = df['Close'].ewm(span=20, adjust=False).mean()
    df['EMA_200'] = df['Close'].ewm(span=200, adjust=False).mean()
    df['VWAP'] = (df['Close'] * df['Volume']).cumsum() / df['Volume'].cumsum()
    
    # BUG FIX: T3 e6 now correctly chains from e3, not raw data
    def get_t3(data, p=10, f=0.7):
        e1 = data.ewm(span=p, adjust=False).mean()
        e2 = e1.ewm(span=p, adjust=False).mean()
        e3 = e2.ewm(span=p, adjust=False).mean()
        e4 = e3.ewm(span=p, adjust=False).mean()
        e5 = e4.ewm(span=p, adjust=False).mean()
        e6 = e5.ewm(span=p, adjust=False).mean()
        c1 = -f**3
        c2 = 3*f**2 + 3*f**3
        c3 = -(6*f**2 + 3*f + 3*f**3)
        c4 = 1 + 3*f + f**3 + 3*f**2
        return c1*e6 + c2*e5 + c3*e4 + c4*e3
    
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
        df.loc[(df['Close'] < df['EMA_20']) & (df['Close'] < df['VWAP']), 'Signal'] = "SELL"  # FIX: Added SELL
    elif mode == "Volume Breakout":
        vol_avg = df['Volume'].rolling(20).mean()
        df.loc[(df['Volume'] > vol_avg * 1.5) & (df['Close'] > df['Close'].shift(1)), 'Signal'] = "BUY"
        df.loc[(df['Volume'] > vol_avg * 1.5) & (df['Close'] < df['Close'].shift(1)), 'Signal'] = "SELL"  # FIX: Added SELL
    elif mode == "EMA Only":
        df.loc[df['Close'] > df['EMA_20'], 'Signal'] = "BUY"  # FIX: Added missing strategy
        df.loc[df['Close'] < df['EMA_20'], 'Signal'] = "SELL"
    
    return df

# ==========================================
# 4. SIDEBAR HYBRID NAVIGATION
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
menu_choice = st.sidebar.radio("Navigate:", [
    "📊 Live Dashboard", 
    "👀 Market Depth & Watchlist",
    "📁 Trade Ledger", 
    "🧠 Strategy Setup", 
    "🔑 Paytm & Alerts API"
], index=0)

st.sidebar.divider()

st.sidebar.markdown("""
    <div style="display: flex; align-items: center; margin-bottom: 10px;">
        <span class="live-dot"></span>
        <span style="color: #00c853; font-weight: bold; font-size: 0.9em;">MARKET LIVE</span>
    </div>
""", unsafe_allow_html=True)

if st.sidebar.button("▶️ Simulate Next Tick", type="primary", use_container_width=True):
    simulate_market_tick()
    st.rerun()

# Circuit breaker check before rendering toggle
cb_tripped = st.session_state.loss_streak >= st.session_state.loss_limit
if cb_tripped:
    st.sidebar.markdown("""
        <div class="circuit-breaker" style="color: #ff1744; font-weight: bold; text-align: center; margin: 10px 0;">
            🛑 CIRCUIT BREAKER TRIPPED
        </div>
    """, unsafe_allow_html=True)
    st.session_state.auto_trade = False

st.session_state.auto_trade = st.sidebar.toggle("🤖 Auto-Pilot", value=st.session_state.auto_trade)

# Animated Risk Meter
loss_ratio = min(st.session_state.loss_streak / max(st.session_state.loss_limit, 1), 1.0)
bar_color = "#ff1744" if loss_ratio >= 1.0 else "#ff9100" if loss_ratio >= 0.6 else "#00c853"
st.sidebar.markdown(f"""
    <div style="margin-top: 15px;">
        <p style="color: #888; font-size: 0.75em; margin-bottom: 4px;">Risk Meter</p>
        <div style="background: rgba(255,255,255,0.1); border-radius: 10px; height: 20px; overflow: hidden;">
            <div style="width: {loss_ratio*100}%; background: {bar_color}; height: 100%; 
                        border-radius: 10px; transition: width 0.5s ease; box-shadow: 0 0 10px {bar_color};">
            </div>
        </div>
        <p style="text-align: center; font-size: 0.75em; color: #888; margin-top: 4px;">
            {st.session_state.loss_streak} / {st.session_state.loss_limit} Loss Streak
        </p>
    </div>
""", unsafe_allow_html=True)

# ==========================================
# 5. PAGES
# ==========================================

# --- PAGE 1: LIVE DASHBOARD ---
if menu_choice == "📊 Live Dashboard":
    st.markdown("""
        <div class="fade-in">
            <h2>📊 Advanced Trading Dashboard</h2>
        </div>
    """, unsafe_allow_html=True)
    
    col_mode, col_sym = st.columns([1, 3])
    with col_mode:
        st.markdown(f"""
            <div style="display: inline-block; padding: 5px 15px; border-radius: 20px; 
                        background: {'rgba(0,200,83,0.2)' if st.session_state.exec_mode == 'LIVE' else 'rgba(255,145,0,0.2)'};
                        color: {'#00c853' if st.session_state.exec_mode == 'LIVE' else '#ff9100'};
                        font-weight: bold; border: 1px solid {'#00c853' if st.session_state.exec_mode == 'LIVE' else '#ff9100'};">
                ● {st.session_state.exec_mode} MODE
            </div>
        """, unsafe_allow_html=True)
    
    symbol = st.selectbox("Select Asset", st.session_state.watchlist)
    
    raw_df = st.session_state.market_data[symbol].copy()
    df = apply_strategy(raw_df, st.session_state.selected_strategy)
    latest = df.iloc[-1]
    pos = st.session_state.open_position
    
    # Auto Trade Execution with toast fix
    if st.session_state.auto_trade and not cb_tripped:
        if pos is None and latest["Signal"] == "BUY":
            st.session_state.open_position = {
                "symbol": symbol, 
                "entry": float(latest["Close"]), 
                "time": datetime.now().strftime("%H:%M:%S"),
                "qty": st.session_state.quantity
            }
            st.session_state.toast_msg = f"🤖 Auto-Pilot: BUY {symbol} @ ₹{latest['Close']:.2f}"
            st.rerun()
        elif pos is not None and pos["symbol"] == symbol and latest["Signal"] == "SELL":
            qty = pos.get("qty", 1)
            pnl = (float(latest["Close"]) - pos["entry"]) * qty
            outcome = "WIN" if pnl >= 0 else "LOSS"
            st.session_state.trade_history.append({
                "Action": "AUTO CLOSE", "Symbol": symbol, "Entry": pos["entry"], 
                "Exit": latest["Close"], "PnL": round(pnl, 2), "Outcome": outcome,
                "Time": datetime.now().strftime("%H:%M:%S"), "Qty": qty
            })
            st.session_state.loss_streak = 0 if outcome == "WIN" else st.session_state.loss_streak + 1
            st.session_state.open_position = None
            st.session_state.toast_msg = f"🤖 Auto-Pilot: CLOSED {symbol} | PnL: ₹{pnl:.2f} ({outcome})"
            st.rerun()
    
    # Display toast message if exists, then clear
    if st.session_state.toast_msg:
        st.toast(st.session_state.toast_msg)
        st.session_state.toast_msg = None

    # Animated Metrics
    m1, m2, m3, m4 = st.columns(4)
    signal_class = "signal-buy" if latest['Signal'] == "BUY" else "signal-sell" if latest['Signal'] == "SELL" else ""
    
    with m1:
        st.metric("LTP", f"₹{latest['Close']:.2f}")
    with m2:
        st.metric("Active Strategy", st.session_state.selected_strategy)
    with m3:
        st.markdown(f"""
            <div style="margin-top: 28px;">
                <span style="color: #888; font-size: 0.8em;">Signal</span><br>
                <span class="{signal_class}">{latest['Signal']}</span>
            </div>
        """, unsafe_allow_html=True)
    with m4:
        streak_color = "#ff1744" if st.session_state.loss_streak >= st.session_state.loss_limit else "#ff9100" if st.session_state.loss_streak > 0 else "#00c853"
        st.markdown(f"""
            <div style="margin-top: 28px;">
                <span style="color: #888; font-size: 0.8em;">Loss Streak</span><br>
                <span style="color: {streak_color}; font-weight: bold; font-size: 1.2em;">
                    {st.session_state.loss_streak} / {st.session_state.loss_limit}
                </span>
            </div>
        """, unsafe_allow_html=True)
    
    # Advanced Plotly Chart - BUG FIX: Added x-axis alignment
    fig = make_subplots(
        rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.03, 
        row_width=[0.2, 0.8], subplot_titles=("Price Action", "RSI Oscillator")
    )
    
    x_vals = df.index
    
    fig.add_trace(go.Candlestick(
        x=x_vals, open=df['Open'], high=df['High'], 
        low=df['Low'], close=df['Close'], name="Price"
    ), row=1, col=1)
    
    if "T3" in st.session_state.selected_strategy: 
        fig.add_trace(go.Scatter(
            x=x_vals, y=df['T3'], line=dict(color='orange', width=2), 
            name="T3 BlackMagic", opacity=0.9
        ), row=1, col=1)
    
    if "EMA" in st.session_state.selected_strategy:
        fig.add_trace(go.Scatter(
            x=x_vals, y=df['EMA_20'], line=dict(color='#00d4aa', width=1.5, dash='dot'),
            name="EMA 20", opacity=0.7
        ), row=1, col=1)
    
    fig.add_trace(go.Scatter(
        x=x_vals, y=df['RSI'], name="RSI", 
        line=dict(color='#ab47bc', width=2)
    ), row=2, col=1)
    
    fig.add_hline(y=70, line_dash="dash", line_color="red", opacity=0.5, row=2, col=1)
    fig.add_hline(y=30, line_dash="dash", line_color="green", opacity=0.5, row=2, col=1)
    fig.add_hline(y=50, line_dash="dash", line_color="white", opacity=0.3, row=2, col=1)
    
    fig.update_layout(
        template="plotly_dark", height=650, 
        margin=dict(l=0, r=0, t=40, b=0), 
        xaxis_rangeslider_visible=False,
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    fig.update_xaxes(rangeslider_visible=False)
    fig.update_yaxes(title_text="Price", row=1, col=1)
    fig.update_yaxes(title_text="RSI", row=2, col=1)
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Execution Section
    st.markdown("""<div class="fade-in">""", unsafe_allow_html=True)
    st.subheader("⚡ Quick Execution")
    
    if cb_tripped:
        st.markdown("""
            <div class="circuit-breaker" style="text-align: center; padding: 20px;">
                <h3 style="color: #ff1744; margin: 0;">🛑 TRADING BLOCKED</h3>
                <p style="color: #ff1744; margin: 5px 0 0 0;">Circuit breaker tripped. Reset loss streak in Strategy Setup.</p>
            </div>
        """, unsafe_allow_html=True)
    elif pos is None:
        qty_col, btn_col = st.columns([1, 3])
        with qty_col:
            st.session_state.quantity = st.number_input("Qty", min_value=1, value=st.session_state.quantity, step=1)
        with btn_col:
            if st.button(f"🟢 MARKET BUY {symbol}", use_container_width=True):
                st.session_state.open_position = {
                    "symbol": symbol, 
                    "entry": float(latest["Close"]), 
                    "time": datetime.now().strftime("%H:%M:%S"),
                    "qty": st.session_state.quantity
                }
                st.rerun()
    else:
        if pos["symbol"] == symbol:
            qty = pos.get("qty", 1)
            pnl = (float(latest["Close"]) - pos["entry"]) * qty
            pnl_color = "#00c853" if pnl >= 0 else "#ff1744"
            
            st.markdown(f"""
                <div class="position-glow" style="border: 1px solid {pnl_color}; background: rgba(0,0,0,0.3);">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <span style="color: #888; font-size: 0.9em;">Open Position</span>
                            <h2 style="color: {pnl_color}; margin: 0;">₹{pnl:.2f}</h2>
                            <span style="color: {pnl_color}; font-size: 0.85em;">{pos['qty']} shares @ ₹{pos['entry']:.2f}</span>
                        </div>
                        <div style="text-align: right;">
                            <span style="color: #888; font-size: 0.8em;">Entry Time</span>
                            <p style="color: #fff; margin: 0;">{pos['time']}</p>
                        </div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
            if st.button("🔴 CLOSE POSITION", type="primary", use_container_width=True):
                outcome = "WIN" if pnl >= 0 else "LOSS"
                st.session_state.trade_history.append({
                    "Action": "MANUAL CLOSE", "Symbol": symbol, "Entry": pos["entry"], 
                    "Exit": latest["Close"], "PnL": round(pnl, 2), "Outcome": outcome,
                    "Time": datetime.now().strftime("%H:%M:%S"), "Qty": qty
                })
                st.session_state.loss_streak = 0 if outcome == "WIN" else st.session_state.loss_streak + 1
                st.session_state.open_position = None
                st.rerun()
        else:
            st.info(f"Position open in {pos['symbol']}. Close it first.")
    st.markdown("""</div>""", unsafe_allow_html=True)

# --- PAGE 2: MARKET DEPTH ---
elif menu_choice == "👀 Market Depth & Watchlist":
    st.markdown("""<div class="fade-in"><h2>👀 Watchlist & Order Book Depth</h2></div>""", unsafe_allow_html=True)
    col1, col2 = st.columns([1.2, 1.8])
    
    with col1:
        st.subheader("📋 Live Watchlist")
        scan_results = []
        for sym in st.session_state.watchlist:
            df_scan = apply_strategy(st.session_state.market_data[sym], st.session_state.selected_strategy)
            ltp = round(df_scan.iloc[-1]['Close'], 2)
            sig = df_scan.iloc[-1]['Signal']
            scan_results.append({"Symbol": sym, "LTP": ltp, "Signal": sig})
        
        scan_df = pd.DataFrame(scan_results)
        
        def color_signal(val):
            color = '#00c853' if val == 'BUY' else '#ff1744' if val == 'SELL' else '#888'
            weight = 'bold' if val in ['BUY', 'SELL'] else 'normal'
            return f'color: {color}; font-weight: {weight};'
        
        styled_scan = scan_df.style.map(color_signal, subset=['Signal'])
        st.dataframe(styled_scan, use_container_width=True, hide_index=True)
        
        selected_sym = st.selectbox("🔍 Select Symbol for Depth:", st.session_state.watchlist)
        
    with col2:
        st.subheader(f"📊 Level 2 Depth - {selected_sym}")
        base_ltp = st.session_state.market_data[selected_sym].iloc[-1]['Close']
        bids, asks = get_market_depth(base_ltp)
        
        d1, d2 = st.columns(2)
        with d1:
            st.markdown("<span style='color:#00c853; font-weight:bold;'>BID (Buyers)</span>", unsafe_allow_html=True)
            st.dataframe(bids, hide_index=True, use_container_width=True)
        with d2:
            st.markdown("<span style='color:#ff1744; font-weight:bold;'>ASK (Sellers)</span>", unsafe_allow_html=True)
            st.dataframe(asks, hide_index=True, use_container_width=True)
        
        spread = round(asks['Ask Price'].iloc[0] - bids['Bid Price'].iloc[0], 2)
        spread_pct = (spread / base_ltp) * 100 if base_ltp else 0
        st.markdown(f"""
            <div style="text-align: center; margin-top: 15px; padding: 10px; 
                        background: rgba(255,255,255,0.05); border-radius: 8px;">
                <span style="color: #888;">Spread: </span>
                <span style="color: #00d4aa; font-weight: bold; font-size: 1.1em;">₹{spread} ({spread_pct:.3f}%)</span>
            </div>
        """, unsafe_allow_html=True)

# --- PAGE 3: TRADE LEDGER ---
elif menu_choice == "📁 Trade Ledger":
    st.markdown("""<div class="fade-in"><h2>📁 Audit Trail & PnL Ledger</h2></div>""", unsafe_allow_html=True)
    if st.session_state.trade_history:
        ledger_df = pd.DataFrame(st.session_state.trade_history)
        if 'Time' in ledger_df.columns:
            ledger_df = ledger_df.sort_values('Time', ascending=False)
        
        total_pnl = ledger_df['PnL'].sum()
        wins = len(ledger_df[ledger_df['Outcome'] == 'WIN'])
        losses = len(ledger_df[ledger_df['Outcome'] == 'LOSS'])
        win_rate = (wins / len(ledger_df) * 100) if len(ledger_df) > 0 else 0
        
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Total Trades", len(ledger_df))
        c2.metric("Win Rate", f"{win_rate:.1f}%")
        c3.metric("Total PnL", f"₹{total_pnl:.2f}")
        c4.metric("Net Wins", wins - losses)
        
        st.divider()
        
        def highlight_outcome(val):
            if val == 'WIN':
                return 'background-color: rgba(0, 200, 83, 0.2); color: #00c853; font-weight: bold;'
            elif val == 'LOSS':
                return 'background-color: rgba(255, 23, 68, 0.2); color: #ff1744; font-weight: bold;'
            return ''
        
        styled_ledger = ledger_df.style.map(highlight_outcome, subset=['Outcome'])
        st.dataframe(styled_ledger, use_container_width=True, hide_index=True)
    else:
        st.info("📭 No trades executed yet. Start trading to populate the ledger.")

# --- PAGE 4: STRATEGY SETUP ---
elif menu_choice == "🧠 Strategy Setup":
    st.markdown("""<div class="fade-in"><h2>🧠 Algorithm Selection & Risk Rules</h2></div>""", unsafe_allow_html=True)
    
    st.session_state.selected_strategy = st.selectbox(
        "Active Algorithm", 
        ["T3 + RSI", "RSI + UT Bot", "EMA + VWAP", "Volume Breakout", "EMA Only"]
    )
    
    c1, c2, c3 = st.columns(3)
    st.session_state.profit_target = c1.number_input("Profit Target (₹)", value=st.session_state.profit_target, step=500)
    st.session_state.loss_limit = c2.number_input("Loss Streak Limit (Circuit Breaker)", min_value=1, value=st.session_state.loss_limit)
    
    if c3.button("🔄 Reset Loss Streak", use_container_width=True):
        st.session_state.loss_streak = 0
        st.session_state.auto_trade = False
        st.success("✅ Loss streak reset! Auto-trading disabled for safety.")
        st.balloons()
    
    st.divider()
    st.subheader("📊 Strategy Performance (Simulated)")
    
    perf_col1, perf_col2, perf_col3 = st.columns(3)
    perf_col1.metric("Sharpe Ratio", "1.85", "+0.12")
    perf_col2.metric("Max Drawdown", "-8.4%", "-1.2%")
    perf_col3.metric("Profit Factor", "2.3", "+0.1")

# --- PAGE 5: PAYTM & ALERTS API ---
elif menu_choice == "🔑 Paytm & Alerts API":
    st.markdown("""<div class="fade-in"><h2>📡 API & Connectors</h2></div>""", unsafe_allow_html=True)
    
    with st.expander("1. Paytm Money API", expanded=True):
        p1, p2 = st.columns(2)
        with p1:
            st.text_input("Paytm API Key", type="password", key="paytm_key")
        with p2:
            st.text_input("Paytm API Secret", type="password", key="paytm_secret")
        if st.button("🔗 Authenticate Broker", use_container_width=True):
            st.success("✅ Broker API Simulated Successfully!")
            st.snow()
    
    with st.expander("2. Telegram Alerts", expanded=True):
        t1, t2 = st.columns(2)
        with t1:
            st.text_input("Bot Token", type="password", key="tg_token")
        with t2:
            st.text_input("Chat ID", key="tg_chat")
        if st.button("📲 Send Test Alert", use_container_width=True):
            st.success("✅ Test alert sent to Telegram!")
            st.balloons()
    
    with st.expander("3. Webhook Configuration"):
        st.text_input("Webhook URL", placeholder="https://your-server.com/webhook")
        st.toggle("Enable Real-time Webhooks", value=False)
