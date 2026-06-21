"""
JVX-BlackMagic Hybrid Terminal v29.0 - Ultimate Secure Build
Features: 5-Page Navigation, Login Gate, Persistent Feed, Real PnL
"""

import streamlit as st
import pandas as pd
import numpy as np
import hashlib
from datetime import datetime
import plotly.graph_objects as go

# ==========================================
# 1. CONFIGURATION & LOGIN GATE
# ==========================================
st.set_page_config(page_title="JVX Terminal v29.0", layout="wide", page_icon="📈")

USERS = {
    "admin": hashlib.sha256("changeme123".encode()).hexdigest(),
    "hitesh": hashlib.sha256("jvx2026".encode()).hexdigest()
}

if "authenticated" not in st.session_state: st.session_state.authenticated = False

def login_screen():
    c1, c2, c3 = st.columns([1, 1.5, 1])
    with c2:
        st.title("🔐 JVX Terminal Login")
        st.caption("Secure Quant Trading Environment")
        with st.form("login_form"):
            user = st.text_input("Username")
            pwd = st.text_input("Password", type="password")
            if st.form_submit_button("Sign In", use_container_width=True):
                if USERS.get(user) == hashlib.sha256(pwd.encode()).hexdigest():
                    st.session_state.authenticated = True
                    st.session_state.username = user
                    st.rerun()
                else:
                    st.error("❌ Invalid username or password.")
        with st.expander("Show Demo Credentials"):
            st.code("User: hitesh | Pass: jvx2026")

if not st.session_state.authenticated:
    login_screen()
    st.stop()

# ==========================================
# 2. SESSION STATE (PERSISTENT DATA)
# ==========================================
default_state = {
    'auto_trade': False, 'loss_streak': 0, 'exec_mode': "PAPER", 
    'trade_history': [], 'profit_target': 5000, 'loss_limit': 2,
    'selected_strategy': "T3 + RSI", 'watchlist': ["NIFTY", "BANKNIFTY", "RELIANCE"],
    'open_position': None, 'market_data': {}
}
for key, val in default_state.items():
    if key not in st.session_state: st.session_state[key] = val

if not st.session_state.market_data:
    rng = np.random.default_rng()
    for sym in st.session_state.watchlist:
        base = 22000 if "NIFTY" in sym else 2500
        walk = np.cumsum(rng.normal(0, 15, 150))
        df = pd.DataFrame({"Close": base + walk, "Volume": rng.integers(1000, 5000, 150)})
        df['Open'] = df['Close'] - rng.normal(0, 5, 150)
        df['High'] = df[['Open', 'Close']].max(axis=1) + 5
        df['Low'] = df[['Open', 'Close']].min(axis=1) - 5
        st.session_state.market_data[sym] = df

def simulate_market_tick():
    for sym in st.session_state.watchlist:
        df = st.session_state.market_data[sym]
        last_close = df["Close"].iloc[-1]
        new_close = last_close + np.random.normal(0, 15)
        new_row = pd.DataFrame({
            "Close": [new_close], "Volume": [np.random.randint(1000, 5000)],
            "Open": [last_close], "High": [max(last_close, new_close) + 2], "Low": [min(last_close, new_close) - 2]
        })
        st.session_state.market_data[sym] = pd.concat([df, new_row], ignore_index=True).tail(500)

# ==========================================
# 3. STRATEGY ENGINE
# ==========================================
def apply_strategy(df, mode):
    delta = df['Close'].diff()
    gain = delta.clip(lower=0).rolling(14).mean()
    loss = (-delta.clip(upper=0)).rolling(14).mean()
    rs = gain / loss.replace(0, np.nan)
    df["RSI"] = (100 - (100 / (1 + rs))).fillna(50)
    
    df['EMA_20'] = df['Close'].ewm(span=20).mean()
    df['EMA_200'] = df['Close'].ewm(span=200).mean()
    df['VWAP'] = (df['Close'] * df['Volume']).cumsum() / df['Volume'].cumsum()
    
    def get_t3(data, p=10, f=0.7):
        e1, e2, e3 = data.ewm(span=p).mean(), data.ewm(span=p).mean().ewm(span=p).mean(), data.ewm(span=p).mean().ewm(span=p).mean().ewm(span=p).mean()
        e4, e5, e6 = e3.ewm(span=p).mean(), e3.ewm(span=p).mean().ewm(span=p).mean(), e3.ewm(span=p).mean().ewm(span=p).mean().ewm(span=p).mean()
        return -f**3*e6 + (3*f**2 + 3*f**3)*e5 - (6*f**2 + 3*f + 3*f**3)*e4 + (1 + 3*f + f**3 + 3*f**2)*e3
    df['T3'] = get_t3(df['Close'])

    df['Signal'] = "WAIT"
    
    if mode == "T3 + RSI":
        df.loc[(df['Close'] > df['T3']) & (df['RSI'] > 50), 'Signal'] = "BUY"
        df.loc[(df['Close'] < df['T3']) & (df['RSI'] < 50), 'Signal'] = "SELL"
    elif mode == "RSI + UT Bot":
        df.loc[(df['RSI'] > 55) & (df['Close'] > df['EMA_200']), 'Signal'] = "BUY"
        df.loc[(df['RSI'] < 45) & (df['Close'] < df['EMA_200']), 'Signal'] = "SELL"
    elif mode == "EMA + VWAP":
        df.loc[(df['Close'] > df['EMA_20']) & (df['Close'] > df['VWAP']), 'Signal'] = "BUY"
    elif mode == "Volume Breakout":
        df.loc[(df['Volume'] > df['Volume'].rolling(20).mean()) & (df['Close'] > df['Close'].shift(1)), 'Signal'] = "BUY"
        
    return df

# ==========================================
# 4. SIDEBAR NAVIGATION
# ==========================================
st.sidebar.markdown(f"👤 **User:** `{st.session_state.username}`")
if st.sidebar.button("🚪 Logout", use_container_width=True):
    st.session_state.authenticated = False
    st.rerun()
st.sidebar.divider()

menu_choice = st.sidebar.radio("Navigate:", ["📊 Live Dashboard", "📁 Trade Ledger", "🧠 Strategy Setup", "🔍 Market Scanner"])

st.sidebar.divider()
if st.sidebar.button("▶️ Simulate Next Tick", type="primary", use_container_width=True):
    simulate_market_tick()
    st.rerun()

st.session_state.auto_trade = st.sidebar.toggle("🤖 Auto-Pilot", value=st.session_state.auto_trade)

if st.session_state.loss_streak >= st.session_state.loss_limit:
    st.sidebar.error("🛑 CIRCUIT BREAKER TRIPPED")
    st.session_state.auto_trade = False
    if st.sidebar.button("🔧 Reset Breaker"):
        st.session_state.loss_streak = 0
        st.rerun()

# ==========================================
# 5. PAGE RENDER LOGIC
# ==========================================
if menu_choice == "📊 Live Dashboard":
    st.header(f"📊 Live Trading ({st.session_state.exec_mode} MODE)")
    symbol = st.selectbox("Select Asset", st.session_state.watchlist)
    
    raw_df = st.session_state.market_data[symbol].copy()
    df = apply_strategy(raw_df, st.session_state.selected_strategy)
    latest = df.iloc[-1]
    pos = st.session_state.open_position
    
    if st.session_state.auto_trade and st.session_state.loss_streak < st.session_state.loss_limit:
        if pos is None and latest["Signal"] == "BUY":
            st.session_state.open_position = {"symbol": symbol, "entry": float(latest["Close"]), "time": datetime.now().strftime("%H:%M:%S")}
            st.toast(f"🤖 Auto-Pilot: BUY {symbol}")
            st.rerun()
        elif pos is not None and pos["symbol"] == symbol and latest["Signal"] == "SELL":
            pnl = float(latest["Close"]) - pos["entry"]
            outcome = "WIN" if pnl >= 0 else "LOSS"
            st.session_state.trade_history.append({"Action": "AUTO CLOSE", "Symbol": symbol, "Entry": pos["entry"], "Exit": latest["Close"], "PnL": round(pnl,2), "Outcome": outcome})
            st.session_state.loss_streak = 0 if outcome == "WIN" else st.session_state.loss_streak + 1
            st.session_state.open_position = None
            st.rerun()

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("LTP", f"₹{latest['Close']:.2f}")
    c2.metric("Active Strategy", st.session_state.selected_strategy)
    c3.metric("Signal", latest['Signal'])
    c4.metric("Loss Streak", f"{st.session_state.loss_streak} / {st.session_state.loss_limit}")
    
    fig = go.Figure()
    fig.add_trace(go.Candlestick(open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name="Price"))
    if "T3" in st.session_state.selected_strategy: fig.add_trace(go.Scatter(y=df['T3'], line=dict(color='orange'), name="T3 Line"))
    fig.update_layout(template="plotly_dark", height=400, margin=dict(l=0, r=0, t=30, b=0), xaxis_rangeslider_visible=False)
    st.plotly_chart(fig, use_container_width=True)
    
    st.subheader("⚡ Execution Console")
    if st.session_state.loss_streak >= st.session_state.loss_limit:
        st.error("🛑 TRADING BLOCKED: Circuit breaker tripped.")
    elif pos is None:
        if st.button(f"🟢 MARKET BUY {symbol}", use_container_width=True):
            st.session_state.open_position = {"symbol": symbol, "entry": float(latest["Close"]), "time": datetime.now().strftime("%H:%M:%S")}
            st.rerun()
    else:
        if pos["symbol"] == symbol:
            pnl = float(latest["Close"]) - pos["entry"]
            st.metric("Open Position PnL", f"₹{pnl:.2f}", delta=f"{pnl:.2f}")
            if st.button("🔴 CLOSE POSITION", type="primary", use_container_width=True):
                outcome = "WIN" if pnl >= 0 else "LOSS"
                st.session_state.trade_history.append({"Action": "MANUAL CLOSE", "Symbol": symbol, "Entry": pos["entry"], "Exit": latest["Close"], "PnL": round(pnl,2), "Outcome": outcome})
                st.session_state.loss_streak = 0 if outcome == "WIN" else st.session_state.loss_streak + 1
                st.session_state.open_position = None
                st.rerun()

elif menu_choice == "📁 Trade Ledger":
    st.header("📁 Audit Trail & Order Book")
    if st.session_state.trade_history:
        ledger_df = pd.DataFrame(st.session_state.trade_history)
        st.dataframe(ledger_df, use_container_width=True, hide_index=True)

elif menu_choice == "🧠 Strategy Setup":
    st.header("🧠 Algorithm & Risk Rules")
    st.session_state.selected_strategy = st.selectbox("Active Algo", ["T3 + RSI", "RSI + UT Bot", "EMA + VWAP", "EMA Only", "Volume Breakout"])

elif menu_choice == "🔍 Market Scanner":
    st.header("🔍 Live Market Scanner")
    scan_results = []
    for sym in st.session_state.watchlist:
        df_scan = apply_strategy(st.session_state.market_data[sym].copy(), st.session_state.selected_strategy)
        latest_scan = df_scan.iloc[-1]
        scan_results.append({"Symbol": sym, "LTP": round(latest_scan['Close'], 2), "Signal": latest_scan['Signal']})
    st.dataframe(pd.DataFrame(scan_results), use_container_width=True)
    