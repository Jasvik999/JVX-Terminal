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
c.execute('''CREATE TABLE IF NOT EXISTS trades (
    id INTEGER PRIMARY KEY AUTOINCREMENT, 
    symbol TEXT, 
    side TEXT, 
    entry REAL, 
    exit REAL, 
    qty INTEGER, 
    gross_pnl REAL, 
    taxes REAL, 
    net_pnl REAL, 
    time TEXT
)''')
conn.commit()

def calculate_taxes(entry, exit_price, qty, side="BUY"):
    turnover = (entry + exit_price) * qty
    brokerage = 40.0  # ₹20 Buy, ₹20 Sell
    stt = turnover * 0.00125 if turnover > 0 else 0
    exchange_txn = turnover * 0.0000325
    gst = (brokerage + exchange_txn) * 0.18
    sebi_charges = turnover * 0.000001
    # Stamp duty on buy side only
    if side == "BUY":
        stamp_duty = (entry * qty) * 0.00015
    else:
        stamp_duty = (exit_price * qty) * 0.00015
    total_tax = round(brokerage + stt + exchange_txn + gst + sebi_charges + stamp_duty, 2)
    return total_tax

def save_trade(sym, side, entry, exit_price, qty):
    if side == "BUY":
        gross = (exit_price - entry) * qty
    else:  # SELL
        gross = (entry - exit_price) * qty
    
    tax = calculate_taxes(entry, exit_price, qty, side)
    net = round(gross - tax, 2)
    t = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute("INSERT INTO trades (symbol, side, entry, exit, qty, gross_pnl, taxes, net_pnl, time) VALUES (?,?,?,?,?,?,?,?,?)", 
              (sym, side, entry, exit_price, qty, round(gross, 2), tax, net, t))
    conn.commit()

# ==========================================
# 1. CSS & THEME
# ==========================================
DARK_CSS = """
<style>
    @keyframes gradientBG { 
        0% { background-position: 0% 50%; } 
        50% { background-position: 100% 50%; } 
        100% { background-position: 0% 50%; } 
    }
    @keyframes pulse-green { 
        0% { box-shadow: 0 0 0 0 rgba(0,200,83,0.7); } 
        70% { box-shadow: 0 0 0 10px rgba(0,200,83,0); } 
        100% { box-shadow: 0 0 0 0 rgba(0,200,83,0); } 
    }
    @keyframes pulse-red { 
        0% { box-shadow: 0 0 0 0 rgba(255,23,68,0.7); } 
        70% { box-shadow: 0 0 0 10px rgba(255,23,68,0); } 
        100% { box-shadow: 0 0 0 0 rgba(255,23,68,0); } 
    }
    @keyframes blink { 
        0%,100% { opacity: 1; } 
        50% { opacity: 0.3; } 
    }
    @keyframes fadeIn { 
        from { opacity: 0; transform: translateY(10px); } 
        to { opacity: 1; transform: translateY(0); } 
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
    .fade-in { 
        animation: fadeIn 0.6s ease-out; 
    }
    .news-card { 
        background: rgba(255,255,255,0.03); 
        border-left: 3px solid #00d4aa; 
        border-radius: 0 8px 8px 0; 
        padding: 12px 16px; 
        margin-bottom: 10px; 
        transition: all 0.3s ease; 
    }
    .news-card:hover {
        background: rgba(255,255,255,0.06);
        transform: translateX(5px);
    }
    .metric-card { 
        background: rgba(255,255,255,0.05); 
        border-radius: 10px; 
        padding: 15px; 
        border: 1px solid rgba(255,255,255,0.1); 
        text-align: center; 
    }
</style>
"""
st.markdown(DARK_CSS, unsafe_allow_html=True)

# ==========================================
# 2. LOGIN GATE
# ==========================================
USERS = {
    "admin": hashlib.sha256("changeme123".encode()).hexdigest(), 
    "hitesh": hashlib.sha256("jvx2026".encode()).hexdigest()
}

if "authenticated" not in st.session_state: 
    st.session_state.authenticated = False

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
                else: 
                    st.error("❌ Invalid credentials!")
    st.stop()

# ==========================================
# 3. YFINANCE LIVE DATA ENGINE
# ==========================================
YF_TICKERS = {
    "NIFTY 50": "^NSEI", 
    "BANKNIFTY": "^NSEBANK", 
    "RELIANCE": "RELIANCE.NS", 
    "HDFCBANK": "HDFCBANK.NS", 
    "INFY": "INFY.NS", 
    "TCS": "TCS.NS", 
    "SBIN": "SBIN.NS",
    "ICICIBANK": "ICICIBANK.NS",
    "KOTAKBANK": "KOTAKBANK.NS",
    "AXISBANK": "AXISBANK.NS",
    "ITC": "ITC.NS",
    "HINDUNILVR": "HINDUNILVR.NS",
    "LT": "LT.NS",
    "BAJFINANCE": "BAJFINANCE.NS",
    "ASIANPAINT": "ASIANPAINT.NS"
}

@st.cache_data(ttl=60)
def get_stock_data(ticker, period="5d", interval="15m"):
    try:
        stock = yf.Ticker(ticker)
        data = stock.history(period=period, interval=interval)
        if data.empty:
            return pd.DataFrame()
        return data
    except Exception as e:
        return pd.DataFrame()

def get_current_price(ticker):
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        price = info.get('regularMarketPrice') or info.get('currentPrice') or 0
        prev_close = info.get('regularMarketPreviousClose') or info.get('previousClose') or 0
        change = price - prev_close if price and prev_close else 0
        pct_change = (change / prev_close * 100) if prev_close else 0
        return price, change, pct_change
    except Exception:
        return 0, 0, 0

def get_stock_news(ticker, limit=5):
    try:
        stock = yf.Ticker(ticker)
        news = stock.news
        if news:
            return news[:limit]
        return []
    except Exception:
        return []

# ==========================================
# 4. SIDEBAR & NAVIGATION
# ==========================================
st.sidebar.markdown(f"### 👤 Welcome, `{st.session_state.username}`")
st.sidebar.markdown("---")
page = st.sidebar.radio("Navigation", ["📊 Dashboard", "📝 Trade Entry", "📜 History", "📰 News"])
st.sidebar.markdown("---")

if st.sidebar.button("🚪 Logout", use_container_width=True):
    st.session_state.authenticated = False
    st.rerun()

# ==========================================
# 5. DASHBOARD PAGE
# ==========================================
if page == "📊 Dashboard":
    st.markdown("<h1 style='text-align: center; color: #00d4aa;'><span class='live-dot'></span>Live Market Dashboard</h1>", unsafe_allow_html=True)
    
    c1, c2 = st.columns([4, 1])
    with c1:
        selected_symbol = st.selectbox("📌 Select Symbol", list(YF_TICKERS.keys()), index=0)
    with c2:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🔄 Refresh", use_container_width=True):
            st.rerun()
    
    ticker = YF_TICKERS[selected_symbol]
    
    # Price metrics
    price, change, pct = get_current_price(ticker)
    
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.markdown(f"""
        <div class="metric-card fade-in">
            <h3 style="color: #00d4aa; margin: 0;">₹{price:,.2f}</h3>
            <p style="color: #888; margin: 5px 0 0 0;">Current Price</p>
        </div>
        """, unsafe_allow_html=True)
    with m2:
        color = "#00c853" if change >= 0 else "#ff1744"
        sign = "+" if change >= 0 else ""
        st.markdown(f"""
        <div class="metric-card fade-in">
            <h3 style="color: {color}; margin: 0;">{sign}{change:,.2f}</h3>
            <p style="color: #888; margin: 5px 0 0 0;">Change</p>
        </div>
        """, unsafe_allow_html=True)
    with m3:
        color = "#00c853" if pct >= 0 else "#ff1744"
        sign = "+" if pct >= 0 else ""
        st.markdown(f"""
        <div class="metric-card fade-in">
            <h3 style="color: {color}; margin: 0;">{sign}{pct:.2f}%</h3>
            <p style="color: #888; margin: 5px 0 0 0;">% Change</p>
        </div>
        """, unsafe_allow_html=True)
    with m4:
        st.markdown(f"""
        <div class="metric-card fade-in">
            <h3 style="color: #00d4aa; margin: 0;">{datetime.now().strftime("%H:%M:%S")}</h3>
            <p style="color: #888; margin: 5px 0 0 0;">Last Updated</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Chart
    data = get_stock_data(ticker, period="5d", interval="15m")
    if not data.empty:
        fig = go.Figure(data=[go.Candlestick(
            x=data.index,
            open=data['Open'],
            high=data['High'],
            low=data['Low'],
            close=data['Close'],
            increasing_line_color='#00c853',
            decreasing_line_color='#ff1744'
        )])
        fig.update_layout(
            template="plotly_dark",
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=20, r=20, t=40, b=20),
            title=f"{selected_symbol} Candlestick Chart (15m)",
            xaxis_rangeslider_visible=False,
            height=500
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Quick stats
        st.subheader("📊 Session Statistics")
        s1, s2, s3, s4 = st.columns(4)
        s1.metric("Open", f"₹{data['Open'].iloc[0]:,.2f}")
        s2.metric("High", f"₹{data['High'].max():,.2f}")
        s3.metric("Low", f"₹{data['Low'].min():,.2f}")
        s4.metric("Close", f"₹{data['Close'].iloc[-1]:,.2f}")
    else:
        st.warning("⚠️ No data available. Market might be closed or ticker invalid.")

# ==========================================
# 6. TRADE ENTRY PAGE
# ==========================================
elif page == "📝 Trade Entry":
    st.markdown("<h1 style='text-align: center; color: #00d4aa;'>📝 New Trade Entry</h1>", unsafe_allow_html=True)
    
    with st.form("trade_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            sym = st.selectbox("Symbol", list(YF_TICKERS.keys()))
            side = st.selectbox("Side", ["BUY", "SELL"])
        with c2:
            entry = st.number_input("Entry Price (₹)", min_value=0.0, step=0.05, format="%.2f")
            exit_price = st.number_input("Exit Price (₹)", min_value=0.0, step=0.05, format="%.2f")
            qty = st.number_input("Quantity", min_value=1, step=1, value=1)
        
        # Live preview of taxes
        if entry > 0 and exit_price > 0 and qty > 0:
            preview_tax = calculate_taxes(entry, exit_price, qty, side)
            if side == "BUY":
                preview_gross = (exit_price - entry) * qty
            else:
                preview_gross = (entry - exit_price) * qty
            preview_net = preview_gross - preview_tax
            
            st.info(f"💡 Preview: Gross P&L = ₹{preview_gross:,.2f} | Taxes = ₹{preview_tax:,.2f} | Net P&L = ₹{preview_net:,.2f}")
        
        submitted = st.form_submit_button("💾 Save Trade", use_container_width=True)
        if submitted:
            if entry <= 0 or exit_price <= 0 or qty <= 0:
                st.error("❌ All values must be positive!")
            else:
                save_trade(sym, side, entry, exit_price, qty)
                st.success(f"✅ Trade saved successfully! {side} {qty} shares of {sym}")
                st.balloons()

# ==========================================
# 7. HISTORY PAGE
# ==========================================
elif page == "📜 History":
    st.markdown("<h1 style='text-align: center; color: #00d4aa;'>📜 Trade History</h1>", unsafe_allow_html=True)
    
    c.execute("SELECT * FROM trades ORDER BY time DESC")
    rows = c.fetchall()
    
    if rows:
        df = pd.DataFrame(rows, columns=["ID", "Symbol", "Side", "Entry", "Exit", "Qty", "Gross PnL", "Taxes", "Net PnL", "Time"])
        
        # Summary metrics
        total_gross = df["Gross PnL"].sum()
        total_tax = df["Taxes"].sum()
        total_net = df["Net PnL"].sum()
        
        m1, m2, m3 = st.columns(3)
        color_gross = "#00c853" if total_gross >= 0 else "#ff1744"
        color_net = "#00c853" if total_net >= 0 else "#ff1744"
        
        m1.markdown(f"""
        <div class="metric-card">
            <h2 style="color: {color_gross}; margin: 0;">₹{total_gross:,.2f}</h2>
            <p style="color: #888; margin: 5px 0 0 0;">Total Gross P&L</p>
        </div>
        """, unsafe_allow_html=True)
        m2.markdown(f"""
        <div class="metric-card">
            <h2 style="color: #ff9800; margin: 0;">₹{total_tax:,.2f}</h2>
            <p style="color: #888; margin: 5px 0 0 0;">Total Taxes</p>
        </div>
        """, unsafe_allow_html=True)
        m3.markdown(f"""
        <div class="metric-card">
            <h2 style="color: {color_net}; margin: 0;">₹{total_net:,.2f}</h2>
            <p style="color: #888; margin: 5px 0 0 0;">Total Net P&L</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Data table
        st.subheader("🗂️ All Trades")
        st.dataframe(df, use_container_width=True, hide_index=True)
        
        # Delete option
        st.markdown("---")
        st.subheader("🗑️ Delete Trade")
        trade_ids = df["ID"].tolist()
        if trade_ids:
            col1, col2 = st.columns([3, 1])
            with col1:
                del_id = st.selectbox("Select Trade ID to delete", trade_ids)
            with col2:
                if st.button("🗑️ Delete", use_container_width=True):
                    c.execute("DELETE FROM trades WHERE id = ?", (del_id,))
                    conn.commit()
                    st.success(f"Trade #{del_id} deleted!")
                    st.rerun()
    else:
        st.info("📭 No trades found. Start trading from the Trade Entry page!")

# ==========================================
# 8. NEWS PAGE
# ==========================================
elif page == "📰 News":
    st.markdown("<h1 style='text-align: center; color: #00d4aa;'>📰 Market News</h1>", unsafe_allow_html=True)
    
    selected_symbol = st.selectbox("📌 Select Symbol for News", list(YF_TICKERS.keys()), index=0)
    ticker = YF_TICKERS[selected_symbol]
    
    news_items = get_stock_news(ticker)
    
    if news_items:
        for item in news_items:
            title = item.get('title', 'No Title')
            publisher = item.get('publisher', 'Unknown')
            published_time = item.get('published', '')
            link = item.get('link', '#')
            
            # Format time
            try:
                dt = datetime.fromtimestamp(published_time)
                time_str = dt.strftime("%Y-%m-%d %H:%M")
            except:
                time_str = str(published_time)
            
            st.markdown(f"""
            <div class="news-card fade-in">
                <h4 style="color: #fff; margin-bottom: 8px;">{title}</h4>
                <p style="color: #888; font-size: 0.9em; margin: 0;">{publisher} • {time_str}</p>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("📭 No news available for this symbol.")
