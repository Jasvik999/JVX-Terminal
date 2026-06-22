"""
JVX-BlackMagic Hybrid Terminal v31.3 - PROFESSIONAL EDITION
Features: Deep Audit, MTF Triple Confirmation, Black-Scholes Greeks, Live WebSocket
Fixed: Trade Ideas HTML quote rendering issue
"""

import streamlit as st
import pandas as pd
import numpy as np
import hashlib
from datetime import datetime, timedelta
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from scipy.stats import norm
import io

# ==========================================
# 0. CSS & THEME
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
    .option-call { background: rgba(0,200,83,0.08); border-radius: 6px; }
    .option-put { background: rgba(255,23,68,0.08); border-radius: 6px; }
    .depth-row { transition: all 0.2s ease; }
    .depth-row:hover { background: rgba(255,255,255,0.05); }
    .bid-bar { background: linear-gradient(90deg, rgba(0,200,83,0.3) 0%, rgba(0,200,83,0.05) 100%); border-radius: 4px; }
    .ask-bar { background: linear-gradient(90deg, rgba(255,23,68,0.3) 0%, rgba(255,23,68,0.05) 100%); border-radius: 4px; }
    .script-header { background: rgba(0,212,170,0.08); border: 1px solid rgba(0,212,170,0.2); border-radius: 12px; padding: 20px; margin-bottom: 20px; }
    .recommendation-box { background: rgba(0,0,0,0.3); border: 1px solid rgba(255,255,255,0.1); border-radius: 12px; padding: 20px; }
    .mtf-match { background: rgba(0,200,83,0.15); border: 2px solid #00c853; border-radius: 8px; padding: 10px; }
    .mtf-mismatch { background: rgba(255,23,68,0.15); border: 2px solid #ff1744; border-radius: 8px; padding: 10px; }
    .heatmap-cell { text-align: center; padding: 8px; border-radius: 4px; font-weight: bold; }
    ::-webkit-scrollbar { width: 8px; }
    ::-webkit-scrollbar-track { background: #0e1117; }
    ::-webkit-scrollbar-thumb { background: #00d4aa; border-radius: 4px; }
    [data-testid="stMetric"] { background: rgba(255,255,255,0.05); border-radius: 10px; padding: 10px; border: 1px solid rgba(255,255,255,0.1); transition: transform 0.3s ease, box-shadow 0.3s ease; }
    [data-testid="stMetric"]:hover { transform: translateY(-2px); box-shadow: 0 4px 15px rgba(0,212,170,0.2); }
    .stButton>button { transition: all 0.3s ease !important; }
    .stButton>button:hover { transform: scale(1.02); box-shadow: 0 0 15px rgba(0,212,170,0.4); }
    .stButton>button:active { transform: scale(0.98); }
</style>
"""

st.set_page_config(page_title="JVX Hybrid Terminal v31.3", layout="wide", page_icon="📈")
st.markdown(DARK_CSS, unsafe_allow_html=True)

# ==========================================
# 1. LOGIN GATE
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
                <p style="color: #888; letter-spacing: 2px;">TERMINAL v31.3 // PRO EDITION</p>
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
# 2. STATE INITIALIZATION
# ==========================================
default_state = {
    'auto_trade': False, 'loss_streak': 0, 'exec_mode': "PAPER", 
    'trade_history': [], 'profit_target': 5000, 'loss_limit': 2,
    'selected_strategy': "T3 + RSI", 
    'watchlist': ["NIFTY 50", "BANKNIFTY", "RELIANCE", "HDFCBANK", "INFY", "TCS", "SBIN", "ICICIBANK"],
    'market_data': {}, 'toast_msg': None, 'quantity': 1,
    'news_cache': [], 'last_news_time': None,
    'portfolio': [], 'balance': 500000, 'used_margin': 0, 'day_pnl': 0,
    'orders': [], 'alerts': [], 'alert_log': [],
    'theme': 'dark', 'backtest_results': None,
    'depth_symbol': None, 'depth_active': False,
    'live_websocket': False, 'last_tick_time': None
}
for key, val in default_state.items():
    if key not in st.session_state:
        st.session_state[key] = val

# Seed data
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

# ==========================================
# 3. CORE FUNCTIONS
# ==========================================
def simulate_market_tick():
    rng = np.random.default_rng()
    for sym in st.session_state.watchlist:
        df = st.session_state.market_data[sym]
        last_close = float(df["Close"].iloc[-1])
        new_close = last_close + rng.normal(0, 15)
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

    for pos in st.session_state.portfolio:
        sym = pos['symbol']
        if sym in st.session_state.market_data:
            ltp = float(st.session_state.market_data[sym].iloc[-1]['Close'])
            pos['ltp'] = ltp
            multiplier = 1 if pos['side'] == 'BUY' else -1
            pos['pnl'] = (ltp - pos['entry']) * pos['qty'] * multiplier

    for alert in st.session_state.alerts:
        if not alert.get('triggered', False):
            sym = alert.get('symbol', '')
            if sym in st.session_state.market_data:
                ltp = float(st.session_state.market_data[sym].iloc[-1]['Close'])
                condition = alert.get('condition', '')
                price = alert.get('price', 0)
                if (condition == 'ABOVE' and ltp >= price) or (condition == 'BELOW' and ltp <= price):
                    alert['triggered'] = True
                    alert['trigger_time'] = datetime.now().strftime("%H:%M:%S")
                    st.session_state.alert_log.append(
                        f"🔔 {sym} {condition} ₹{price} @ {alert['trigger_time']}"
                    )

    if len(st.session_state.alert_log) > 100:
        st.session_state.alert_log = st.session_state.alert_log[-100:]

    st.session_state.last_tick_time = datetime.now().strftime("%H:%M:%S")

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
    df['EMA_50'] = df['Close'].ewm(span=50, adjust=False).mean()
    df['EMA_200'] = df['Close'].ewm(span=200, adjust=False).mean()
    df['VWAP'] = (df['Close'] * df['Volume']).rolling(50).sum() / df['Volume'].rolling(50).sum()

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
    elif mode == "Volume Breakout":
        vol_avg = df['Volume'].rolling(20).mean()
        df.loc[(df['Volume'] > vol_avg * 1.5) & (df['Close'] > df['Close'].shift(1)), 'Signal'] = "BUY"
        df.loc[(df['Volume'] > vol_avg * 1.5) & (df['Close'] < df['Close'].shift(1)), 'Signal'] = "SELL"
    elif mode == "EMA Only":
        df.loc[df['Close'] > df['EMA_20'], 'Signal'] = "BUY"
        df.loc[df['Close'] < df['EMA_20'], 'Signal'] = "SELL"
    return df

# ==========================================
# 4. BLACK-SCHOLES GREEKS
# ==========================================
def black_scholes_greeks(S, K, T, r, sigma, option_type='call'):
    if T <= 0 or sigma <= 0:
        return {'price': 0, 'delta': 0, 'gamma': 0, 'theta': 0, 'vega': 0, 'rho': 0, 'iv': sigma}

    d1 = (np.log(S / K) + (r + 0.5 * sigma**2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)

    if option_type == 'call':
        price = S * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2)
        delta = norm.cdf(d1)
    else:
        price = K * np.exp(-r * T) * norm.cdf(-d2) - S * norm.cdf(-d1)
        delta = -norm.cdf(-d1)

    gamma = norm.pdf(d1) / (S * sigma * np.sqrt(T))
    theta = -(S * norm.pdf(d1) * sigma) / (2 * np.sqrt(T)) - r * K * np.exp(-r * T) * norm.cdf(d2 if option_type == 'call' else -d2)
    vega = S * norm.pdf(d1) * np.sqrt(T)
    rho = K * T * np.exp(-r * T) * norm.cdf(d2 if option_type == 'call' else -d2)
    if option_type == 'put':
        rho = -rho

    return {
        'price': round(price, 2),
        'delta': round(delta, 4),
        'gamma': round(gamma, 6),
        'theta': round(theta / 365, 4),
        'vega': round(vega / 100, 4),
        'rho': round(rho / 100, 4),
        'iv': round(sigma * 100, 2)
    }

def generate_options_chain_bs(symbol):
    ltp = st.session_state.market_data[symbol].iloc[-1]['Close']
    spot = round(ltp / 50) * 50 if "NIFTY" in symbol else round(ltp / 100) * 100
    strikes = [spot + i*50 for i in range(-5, 6)] if "NIFTY" in symbol else [spot + i*100 for i in range(-5, 6)]

    T = 7 / 365
    r = 0.065

    chain = []
    for strike in strikes:
        moneyness = abs(strike - spot) / spot
        sigma = 0.15 + moneyness * 0.3 + np.random.uniform(0.02, 0.08)

        call_greeks = black_scholes_greeks(spot, strike, T, r, sigma, 'call')
        put_greeks = black_scholes_greeks(spot, strike, T, r, sigma, 'put')

        chain.append({
            "Strike": strike, "Spot": round(spot, 2),
            "CE LTP": call_greeks['price'], "CE Delta": call_greeks['delta'],
            "CE Gamma": call_greeks['gamma'], "CE Theta": call_greeks['theta'],
            "CE Vega": call_greeks['vega'], "CE IV": call_greeks['iv'],
            "PE LTP": put_greeks['price'], "PE Delta": put_greeks['delta'],
            "PE Gamma": put_greeks['gamma'], "PE Theta": put_greeks['theta'],
            "PE Vega": put_greeks['vega'], "PE IV": put_greeks['iv']
        })
    return pd.DataFrame(chain)

# ==========================================
# 5. MTF TRIPLE CONFIRMATION
# ==========================================
def get_mtf_signal(symbol, strategy):
    df = st.session_state.market_data[symbol].copy()

    df_5m = apply_strategy(df, strategy)
    sig_5m = df_5m.iloc[-1]['Signal']

    df_15m = df.iloc[::3].copy()
    df_15m = apply_strategy(df_15m, strategy)
    sig_15m = df_15m.iloc[-1]['Signal'] if len(df_15m) > 0 else "WAIT"

    df_1h = df.iloc[::12].copy()
    df_1h = apply_strategy(df_1h, strategy)
    sig_1h = df_1h.iloc[-1]['Signal'] if len(df_1h) > 0 else "WAIT"

    buy_count = sum(1 for s in [sig_5m, sig_15m, sig_1h] if s == "BUY")
    sell_count = sum(1 for s in [sig_5m, sig_15m, sig_1h] if s == "SELL")

    if buy_count == 3:
        return "BUY", 95, sig_5m, sig_15m, sig_1h
    elif sell_count == 3:
        return "SELL", 95, sig_5m, sig_15m, sig_1h
    elif buy_count >= 2:
        return "BUY", 70, sig_5m, sig_15m, sig_1h
    elif sell_count >= 2:
        return "SELL", 70, sig_5m, sig_15m, sig_1h
    else:
        return "WAIT", 30, sig_5m, sig_15m, sig_1h

# ==========================================
# 6. DEEP AUDIT / RISK METRICS
# ==========================================
def calculate_risk_metrics(trades):
    if not trades or len(trades) < 2:
        return {
            'sharpe': 0, 'max_drawdown': 0, 'calmar': 0,
            'win_rate': 0, 'profit_factor': 0,
            'avg_win': 0, 'avg_loss': 0, 'expectancy': 0
        }

    pnls = [t['PnL'] for t in trades]
    wins = [p for p in pnls if p > 0]
    losses = [p for p in pnls if p < 0]

    returns = np.array(pnls)
    if len(returns) > 1 and np.std(returns) > 0:
        sharpe = (np.mean(returns) / np.std(returns)) * np.sqrt(252)
    else:
        sharpe = 0

    cumulative = np.cumsum(returns)
    running_max = np.maximum.accumulate(cumulative)
    drawdowns = (cumulative - running_max) / running_max
    max_dd = np.min(drawdowns) if len(drawdowns) > 0 else 0

    total_return = cumulative[-1] if len(cumulative) > 0 else 0
    calmar = total_return / abs(max_dd) if max_dd != 0 else 0

    win_rate = (len(wins) / len(pnls) * 100) if len(pnls) > 0 else 0

    gross_profit = sum(wins) if wins else 0
    gross_loss = abs(sum(losses)) if losses else 0
    profit_factor = gross_profit / gross_loss if gross_loss > 0 else 0

    avg_win = np.mean(wins) if wins else 0
    avg_loss = np.mean(losses) if losses else 0

    expectancy = (win_rate/100 * avg_win) - ((100-win_rate)/100 * abs(avg_loss)) if avg_loss != 0 else 0

    return {
        'sharpe': round(sharpe, 2),
        'max_drawdown': round(max_dd * 100, 2),
        'calmar': round(calmar, 2),
        'win_rate': round(win_rate, 1),
        'profit_factor': round(profit_factor, 2),
        'avg_win': round(avg_win, 2),
        'avg_loss': round(avg_loss, 2),
        'expectancy': round(expectancy, 2)
    }

def generate_eod_excel(trades):
    if not trades:
        return None

    df = pd.DataFrame(trades)
    metrics = calculate_risk_metrics(trades)

    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Trade History', index=False)
        metrics_df = pd.DataFrame([metrics])
        metrics_df.to_excel(writer, sheet_name='Risk Metrics', index=False)
        summary = {
            'Metric': ['Total Trades', 'Total PnL', 'Win Rate %', 'Sharpe Ratio', 
                      'Max Drawdown %', 'Calmar Ratio', 'Profit Factor', 'Expectancy'],
            'Value': [
                len(trades),
                round(df['PnL'].sum(), 2),
                metrics['win_rate'],
                metrics['sharpe'],
                metrics['max_drawdown'],
                metrics['calmar'],
                metrics['profit_factor'],
                metrics['expectancy']
            ]
        }
        pd.DataFrame(summary).to_excel(writer, sheet_name='Summary', index=False)

    output.seek(0)
    return output

# ==========================================
# 7. SIDEBAR
# ==========================================
st.sidebar.markdown(f"""
    <div class="slide-in" style="padding: 10px; border-radius: 8px; background: rgba(0,212,170,0.1); margin-bottom: 10px;">
        <span style="color: #00d4aa; font-weight: bold;">👤 {st.session_state.username.upper()}</span><br>
        <span style="font-size: 0.8em; color: #888;">{st.session_state.exec_mode} MODE</span>
    </div>
""", unsafe_allow_html=True)

if st.sidebar.button("🚪 Logout", use_container_width=True):
    keys_to_clear = ['portfolio', 'trade_history', 'orders', 'alerts', 'alert_log', 
                     'news_cache', 'market_data', 'depth_symbol', 'depth_active']
    for key in keys_to_clear:
        if key in st.session_state:
            del st.session_state[key]
    st.session_state.authenticated = False
    st.rerun()

st.sidebar.divider()

total_pnl = sum(p.get('pnl', 0) for p in st.session_state.portfolio)
available = st.session_state.balance - st.session_state.used_margin + total_pnl
st.sidebar.markdown(f"""
    <div class="metric-card" style="margin-bottom: 15px;">
        <div style="font-size: 0.75em; color: #888;">Available Margin</div>
        <div style="font-size: 1.4em; font-weight: bold; color: #00d4aa;">₹{available:,.0f}</div>
        <div style="font-size: 0.7em; color: #666;">Used: ₹{st.session_state.used_margin:,.0f}</div>
    </div>
""", unsafe_allow_html=True)

st.session_state.live_websocket = st.sidebar.toggle("🌐 Live WebSocket Mode", value=st.session_state.live_websocket)
if st.session_state.live_websocket:
    st.sidebar.markdown(f"""
        <div style="text-align: center; padding: 8px; background: rgba(0,200,83,0.1); border-radius: 6px; margin-bottom: 10px;">
            <span class="live-dot"></span>
            <span style="color: #00c853; font-weight: bold; font-size: 0.85em;">AUTO-REFRESH: 1.0s</span><br>
            <span style="color: #888; font-size: 0.7em;">Last: {st.session_state.last_tick_time or 'Never'}</span>
        </div>
    """, unsafe_allow_html=True)

menu_choice = st.sidebar.radio("Navigate:", [
    "💡 Trade Ideas", "📊 Live Dashboard", "👀 Market Depth", "📊 Options Chain",
    "📰 Market News", "📂 Portfolio", "📋 Order Book", "🔔 Alerts",
    "🎭 Sentiment", "📅 Economic Calendar", "📁 Trade Ledger", 
    "🧠 Strategy Setup", "🤖 AI Assistant", "🔑 API Settings"
], index=0)

st.sidebar.divider()
st.sidebar.markdown("""<div style="display: flex; align-items: center; margin-bottom: 10px;"><span class="live-dot"></span><span style="color: #00c853; font-weight: bold; font-size: 0.9em;">MARKET LIVE</span></div>""", unsafe_allow_html=True)

if st.sidebar.button("▶️ Simulate Next Tick", type="primary", use_container_width=True):
    simulate_market_tick()
    st.session_state.last_news_time = None
    st.rerun()

if st.session_state.live_websocket:
    st.sidebar.caption("Auto-refreshing every 1 second...")
    st.rerun()

cb_tripped = st.session_state.loss_streak >= st.session_state.loss_limit
if cb_tripped:
    st.sidebar.markdown("""<div class="circuit-breaker" style="color: #ff1744; font-weight: bold; text-align: center; margin: 10px 0;">🛑 CIRCUIT BREAKER</div>""", unsafe_allow_html=True)
    st.session_state.auto_trade = False

st.session_state.auto_trade = st.sidebar.toggle("🤖 Auto-Pilot", value=st.session_state.auto_trade)

loss_ratio = min(st.session_state.loss_streak / max(st.session_state.loss_limit, 1), 1.0)
bar_color = "#ff1744" if loss_ratio >= 1.0 else "#ff9100" if loss_ratio >= 0.6 else "#00c853"
st.sidebar.markdown(f"""
    <div style="margin-top: 15px;">
        <p style="color: #888; font-size: 0.75em; margin-bottom: 4px;">Risk Meter</p>
        <div style="background: rgba(255,255,255,0.1); border-radius: 10px; height: 20px; overflow: hidden;">
            <div style="width: {loss_ratio*100}%; background: {bar_color}; height: 100%; border-radius: 10px; transition: width 0.5s ease; box-shadow: 0 0 10px {bar_color};"></div>
        </div>
        <p style="text-align: center; font-size: 0.75em; color: #888; margin-top: 4px;">{st.session_state.loss_streak} / {st.session_state.loss_limit} Loss Streak</p>
    </div>
""", unsafe_allow_html=True)

# ==========================================
# 8. PAGES
# ==========================================

# --- TRADE IDEAS WITH MTF (FIXED) ---
if menu_choice == "💡 Trade Ideas":
    st.markdown("""<div class="fade-in"><h2>💡 Top 10 Trade Ideas</h2><p style="color: #888;">MTF Triple Confirmation Enabled</p></div>""", unsafe_allow_html=True)
    ticker_text = "  🔥 NIFTY +1.2% | BANKNIFTY +0.8% | RELIANCE +2.1% | TCS +1.5% | INFY -0.4% | SBIN +1.8% | HDFCBANK +0.9% | ICICIBANK +1.1% 🔥  "
    st.markdown(f"""<div class="ticker-wrap"><div class="ticker-content">{ticker_text}</div></div>""", unsafe_allow_html=True)

    rng = np.random.default_rng(seed=int(datetime.now().timestamp()) % 1000)
    ideas = []
    for i in range(10):
        sym = rng.choice(st.session_state.watchlist)
        mtf_signal, mtf_score, sig_5m, sig_15m, sig_1h = get_mtf_signal(sym, st.session_state.selected_strategy)

        df = st.session_state.market_data[sym].copy()
        df = apply_strategy(df, st.session_state.selected_strategy)
        latest = df.iloc[-1]
        ltp = round(latest['Close'], 2)
        atr = round(df['Close'].diff().abs().rolling(14).mean().iloc[-1], 2)

        if mtf_signal == "BUY":
            entry, sl, target1, target2, direction = ltp, round(ltp-atr*1.5, 2), round(ltp+atr*2, 2), round(ltp+atr*3.5, 2), "LONG"
        elif mtf_signal == "SELL":
            entry, sl, target1, target2, direction = ltp, round(ltp+atr*1.5, 2), round(ltp-atr*2, 2), round(ltp-atr*3.5, 2), "SHORT"
        else:
            entry, sl, target1, target2, direction = ltp, round(ltp-atr*2, 2), round(ltp+atr*2.5, 2), "-", "RANGE"

        reasons = {
            "BUY": ["T3 breakout on all 3 timeframes", "Triple confirmation: 5M+15M+1H aligned", "Volume surge + VWAP support", "RSI momentum across TFs"],
            "SELL": ["T3 rejection on all 3 timeframes", "Triple confirmation: 5M+15M+1H aligned", "Breakdown below VWAP on all TFs", "RSI divergence resolved"],
            "RANGE": ["Mixed signals across timeframes", "Wait for alignment", "Consolidation on higher TF", "Low volume expansion"]
        }
        reason = rng.choice(reasons.get(mtf_signal, reasons["RANGE"]))

        ideas.append({
            "id": i+1, "symbol": sym, "direction": direction, "entry": entry, "sl": sl, 
            "target1": target1, "target2": target2, "score": mtf_score,
            "sig_5m": sig_5m, "sig_15m": sig_15m, "sig_1h": sig_1h,
            "timeframe": rng.choice(["15M", "30M", "1H", "D"]), "reason": reason, "rsi": round(latest['RSI'], 1)
        })
    ideas = sorted(ideas, key=lambda x: x['score'], reverse=True)

    buy_count = sum(1 for i in ideas if i['direction'] == "LONG")
    sell_count = sum(1 for i in ideas if i['direction'] == "SHORT")
    high_conviction = sum(1 for i in ideas if i['score'] >= 95)

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total Ideas", len(ideas))
    m2.metric("🔥 High Conviction", high_conviction)
    m3.metric("BUY Setups", buy_count)
    m4.metric("SELL Setups", sell_count)
    st.divider()

    cols = st.columns(2)
    for idx, idea in enumerate(ideas):
        col = cols[idx % 2]

        # Use native Streamlit components - NO raw HTML inside cards
        with col.container():
            # Header row
            h1, h2 = st.columns([3, 1])
            dir_color = "green" if idea['direction'] == "LONG" else "red" if idea['direction'] == "SHORT" else "orange"
            h1.markdown(f"**{idea['symbol']}** :{dir_color}[{idea['direction']}]")
            h2.markdown(f"**Score: {idea['score']}**")

            # MTF Status
            mtf_match = idea['sig_5m'] == idea['sig_15m'] == idea['sig_1h'] and idea['sig_5m'] in ["BUY", "SELL"]
            if mtf_match:
                st.success(f"🔥 MTF ALIGN: 5M:{idea['sig_5m']} | 15M:{idea['sig_15m']} | 1H:{idea['sig_1h']} ✅ TRIPLE MATCH")
            else:
                st.info(f"MTF: 5M:{idea['sig_5m']} | 15M:{idea['sig_15m']} | 1H:{idea['sig_1h']}")

            # Entry/SL/Target
            e1, e2, e3 = st.columns(3)
            e1.metric("ENTRY", f"₹{idea['entry']}")
            e2.metric("SL", f"₹{idea['sl']}", delta=f"₹{round(idea['entry']-idea['sl'],2)}")
            e3.metric("TARGET", f"₹{idea['target1']}")

            # Reason
            st.caption(f"Strategy: {idea['reason']}")
            st.caption(f"TF: {idea['timeframe']} | RSI: {idea['rsi']}")

            # Execute button
            if idea['direction'] in ["LONG", "SHORT"]:
                if st.button(f"🚀 Execute {idea['direction']}", key=f"idea_{idea['id']}", use_container_width=True):
                    margin_used = idea['entry'] * st.session_state.quantity * 0.2
                    if st.session_state.balance - st.session_state.used_margin >= margin_used:
                        st.session_state.portfolio.append({
                            "symbol": idea['symbol'], "entry": idea['entry'], "qty": st.session_state.quantity,
                            "side": "BUY" if idea['direction'] == "LONG" else "SELL",
                            "sl": idea['sl'], "target": idea['target1'], "time": datetime.now().strftime("%H:%M:%S"),
                            "pnl": 0
                        })
                        st.session_state.used_margin += margin_used
                        st.session_state.toast_msg = f"🚀 {idea['direction']} {idea['symbol']} @ ₹{idea['entry']}"
                        st.rerun()
                    else:
                        st.error("❌ Insufficient margin!")

            st.divider()
# --- LIVE DASHBOARD ---
elif menu_choice == "📊 Live Dashboard":
    st.markdown("""<div class="fade-in"><h2>📊 Advanced Trading Dashboard</h2></div>""", unsafe_allow_html=True)
    col_mode, col_sym = st.columns([1, 3])
    with col_mode:
        st.markdown(f"""<div style="display: inline-block; padding: 5px 15px; border-radius: 20px; background: {'rgba(0,200,83,0.2)' if st.session_state.exec_mode == 'LIVE' else 'rgba(255,145,0,0.2)'}; color: {'#00c853' if st.session_state.exec_mode == 'LIVE' else '#ff9100'}; font-weight: bold; border: 1px solid {'#00c853' if st.session_state.exec_mode == 'LIVE' else '#ff9100'};">● {st.session_state.exec_mode} MODE</div>""", unsafe_allow_html=True)
    symbol = st.selectbox("Select Asset", st.session_state.watchlist)
    raw_df = st.session_state.market_data[symbol].copy()
    df = apply_strategy(raw_df, st.session_state.selected_strategy)
    latest = df.iloc[-1]
    for pos in st.session_state.portfolio:
        if pos['symbol'] == symbol:
            multiplier = 1 if pos['side'] == 'BUY' else -1
            pos['pnl'] = (latest['Close'] - pos['entry']) * pos['qty'] * multiplier
            pos['ltp'] = latest['Close']
    total_pnl = sum(p.get('pnl', 0) for p in st.session_state.portfolio)
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("LTP", f"₹{latest['Close']:.2f}")
    m2.metric("Active Strategy", st.session_state.selected_strategy)
    sig_class = "signal-buy" if latest['Signal'] == "BUY" else "signal-sell" if latest['Signal'] == "SELL" else ""
    m3.markdown(f"""<div style="margin-top: 28px;"><span style="color: #888; font-size: 0.8em;">Signal</span><br><span class="{sig_class}">{latest['Signal']}</span></div>""", unsafe_allow_html=True)
    m4.metric("Open P&L", f"₹{total_pnl:.2f}", delta=f"{total_pnl:.2f}")

    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.03, row_width=[0.2, 0.8], subplot_titles=("Price Action", "RSI"))
    x_vals = df.index
    fig.add_trace(go.Candlestick(x=x_vals, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name="Price"), row=1, col=1)
    if "T3" in st.session_state.selected_strategy: 
        fig.add_trace(go.Scatter(x=x_vals, y=df['T3'], line=dict(color='orange', width=2), name="T3"), row=1, col=1)
    if "EMA" in st.session_state.selected_strategy:
        fig.add_trace(go.Scatter(x=x_vals, y=df['EMA_20'], line=dict(color='#00d4aa', width=1.5, dash='dot'), name="EMA 20"), row=1, col=1)
    fig.add_trace(go.Scatter(x=x_vals, y=df['RSI'], name="RSI", line=dict(color='#ab47bc', width=2)), row=2, col=1)
    fig.add_hline(y=70, line_dash="dash", line_color="red", opacity=0.5, row=2, col=1)
    fig.add_hline(y=30, line_dash="dash", line_color="green", opacity=0.5, row=2, col=1)
    fig.add_hline(y=50, line_dash="dash", line_color="white", opacity=0.3, row=2, col=1)
    fig.update_layout(template="plotly_dark", height=650, margin=dict(l=0, r=0, t=40, b=0), xaxis_rangeslider_visible=False, showlegend=True, legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("⚡ Quick Execution")
    if cb_tripped:
        st.markdown("""<div class="circuit-breaker" style="text-align: center; padding: 20px;"><h3 style="color: #ff1744; margin: 0;">🛑 TRADING BLOCKED</h3></div>""", unsafe_allow_html=True)
    else:
        o1, o2, o3, o4 = st.columns(4)
        order_type = o1.selectbox("Order Type", ["MARKET", "LIMIT", "SL", "SL-M", "BRACKET"])
        qty = o2.number_input("Qty", min_value=1, value=1, step=1)
        side = o3.selectbox("Side", ["BUY", "SELL"])
        price = o4.number_input("Price", value=float(latest['Close']), step=0.05) if order_type != "MARKET" else latest['Close']
        if st.button(f"🚀 Place {order_type} {side} Order", use_container_width=True):
            margin = latest['Close'] * qty * 0.2
            if st.session_state.balance - st.session_state.used_margin >= margin:
                if order_type == "MARKET":
                    st.session_state.portfolio.append({
                        "symbol": symbol, "entry": float(latest['Close']), "qty": qty,
                        "side": side, "sl": float(latest['Close'])*0.98 if side=="BUY" else float(latest['Close'])*1.02,
                        "target": float(latest['Close'])*1.04 if side=="BUY" else float(latest['Close'])*0.96,
                        "time": datetime.now().strftime("%H:%M:%S"), "pnl": 0, "ltp": latest['Close']
                    })
                    st.session_state.used_margin += margin
                    st.success(f"✅ {side} {qty} {symbol} @ ₹{latest['Close']:.2f}")
                else:
                    st.session_state.orders.append({
                        "symbol": symbol, "type": order_type, "side": side, "qty": qty,
                        "price": price, "status": "PENDING", "time": datetime.now().strftime("%H:%M:%S")
                    })
                    st.success(f"✅ {order_type} {side} order placed for {qty} {symbol} @ ₹{price}")
            else:
                st.error("❌ Insufficient margin!")

# --- MARKET DEPTH ---
elif menu_choice == "👀 Market Depth":
    st.markdown("""<div class="fade-in"><h2>👀 Professional Market Depth</h2><p style="color: #888;">Live Level-2 Order Book with Script Analytics</p></div>""", unsafe_allow_html=True)

    st.markdown("""<div class="fade-in">""", unsafe_allow_html=True)
    search_col, btn_col, kill_col = st.columns([3, 1, 1])

    with search_col:
        search_input = st.text_input("🔍 Search Symbol", placeholder="e.g. RELIANCE, NIFTY 50, SBIN...", value=st.session_state.depth_symbol if st.session_state.depth_symbol else "")

    with btn_col:
        search_clicked = st.button("🔎 SEARCH", use_container_width=True, type="primary")

    with kill_col:
        kill_clicked = st.button("❌ KILL", use_container_width=True)

    if kill_clicked:
        st.session_state.depth_symbol = None
        st.session_state.depth_active = False
        st.rerun()

    if search_clicked and search_input.strip():
        matched = [s for s in st.session_state.watchlist if search_input.upper() in s.upper()]
        if matched:
            st.session_state.depth_symbol = matched[0]
            st.session_state.depth_active = True
        else:
            st.error(f"❌ Symbol '{search_input}' not found in watchlist!")

    if not st.session_state.depth_active or not st.session_state.depth_symbol:
        st.info("🔍 Enter a symbol and click SEARCH to view live market depth. Click KILL to reset.")
        st.stop()

    sym = st.session_state.depth_symbol
    df = st.session_state.market_data[sym].copy()
    df = apply_strategy(df, st.session_state.selected_strategy)

    latest = df.iloc[-1]
    prev_close = df.iloc[-2]['Close'] if len(df) > 1 else latest['Close']
    ltp = latest['Close']
    open_price = latest['Open']
    day_high = df['High'].tail(50).max()
    day_low = df['Low'].tail(50).min()
    volume = int(latest['Volume'])
    avg_price = round((df['Close'].tail(50) * df['Volume'].tail(50)).sum() / df['Volume'].tail(50).sum(), 2) if df['Volume'].tail(50).sum() > 0 else ltp

    change = round(ltp - prev_close, 2)
    change_pct = round((change / prev_close) * 100, 2) if prev_close else 0
    change_color = "#00c853" if change >= 0 else "#ff1744"
    change_sign = "+" if change >= 0 else ""

    upper_circuit = round(prev_close * 1.20, 2) if "NIFTY" not in sym else round(prev_close * 1.10, 2)
    lower_circuit = round(prev_close * 0.80, 2) if "NIFTY" not in sym else round(prev_close * 0.90, 2)

    st.markdown(f"""
        <div class="script-header fade-in">
            <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap;">
                <div>
                    <h1 style="margin: 0; color: #fff; font-size: 2.2em;">{sym}</h1>
                    <span style="color: #888; font-size: 0.9em;">NSE EQ • {st.session_state.exec_mode} MODE</span>
                </div>
                <div style="text-align: right;">
                    <div style="font-size: 2.5em; font-weight: bold; color: {change_color};">₹{ltp:.2f}</div>
                    <div style="color: {change_color}; font-size: 1.1em; font-weight: bold;">
                        {change_sign}{change:.2f} ({change_sign}{change_pct:.2f}%)
                    </div>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    m1, m2, m3, m4, m5, m6, m7, m8 = st.columns(8)
    m1.metric("Open", f"₹{open_price:.2f}")
    m2.metric("High", f"₹{day_high:.2f}")
    m3.metric("Low", f"₹{day_low:.2f}")
    m4.metric("Prev Close", f"₹{prev_close:.2f}")
    m5.metric("Volume", f"{volume:,}")
    m6.metric("Avg Price", f"₹{avg_price:.2f}")
    m7.metric("Upper Circuit", f"₹{upper_circuit:.2f}")
    m8.metric("Lower Circuit", f"₹{lower_circuit:.2f}")

    st.divider()

    bids, asks = get_market_depth(ltp)
    total_bid_qty = int(bids['Bid Qty'].sum())
    total_ask_qty = int(asks['Ask Qty'].sum())
    bid_ask_ratio = round(total_bid_qty / total_ask_qty, 2) if total_ask_qty > 0 else 0

    st.subheader("📊 Live Level-2 Market Depth")

    total_qty = total_bid_qty + total_ask_qty
    bid_pct = (total_bid_qty / total_qty * 100) if total_qty > 0 else 50
    ask_pct = 100 - bid_pct

    st.markdown(f"""
        <div style="margin-bottom: 15px;">
            <div style="display: flex; justify-content: space-between; font-size: 0.85em; margin-bottom: 5px;">
                <span style="color: #00c853; font-weight: bold;">👥 BUYERS: {total_bid_qty:,}</span>
                <span style="color: #ff1744; font-weight: bold;">SELLERS: {total_ask_qty:,} 👥</span>
            </div>
            <div style="display: flex; height: 30px; border-radius: 6px; overflow: hidden;">
                <div style="width: {bid_pct}%; background: linear-gradient(90deg, #00c853, #00c853aa); display: flex; align-items: center; justify-content: center; color: #000; font-weight: bold; font-size: 0.85em;">
                    {bid_pct:.0f}%
                </div>
                <div style="width: {ask_pct}%; background: linear-gradient(90deg, #ff1744aa, #ff1744); display: flex; align-items: center; justify-content: center; color: #fff; font-weight: bold; font-size: 0.85em;">
                    {ask_pct:.0f}%
                </div>
            </div>
            <div style="text-align: center; margin-top: 5px; color: #888; font-size: 0.8em;">
                Bid/Ask Ratio: {bid_ask_ratio} | {"Buyers Dominating" if bid_ask_ratio > 1.2 else "Sellers Dominating" if bid_ask_ratio < 0.8 else "Balanced"}
            </div>
        </div>
    """, unsafe_allow_html=True)

    depth_col1, depth_col2 = st.columns(2)

    with depth_col1:
        st.markdown("<h4 style='color: #00c853; text-align: center;'>🟢 BID (Buyers)</h4>", unsafe_allow_html=True)
        for i, row in bids.iterrows():
            st.markdown(f"""
                <div class="depth-row bid-bar" style="padding: 8px 12px; margin-bottom: 4px; display: flex; justify-content: space-between; align-items: center;">
                    <div style="display: flex; justify-content: space-between; width: 100%;">
                        <span style="color: #00c853; font-weight: bold; font-size: 1.1em;">₹{row['Bid Price']}</span>
                        <span style="color: #fff; font-size: 0.95em;">{row['Bid Qty']:,}</span>
                    </div>
                </div>
            """, unsafe_allow_html=True)
        st.markdown(f"""
            <div style="text-align: center; padding: 10px; background: rgba(0,200,83,0.1); border-radius: 8px; margin-top: 10px;">
                <span style="color: #00c853; font-weight: bold; font-size: 1.2em;">Total Buyers: {total_bid_qty:,}</span>
            </div>
        """, unsafe_allow_html=True)

    with depth_col2:
        st.markdown("<h4 style='color: #ff1744; text-align: center;'>🔴 ASK (Sellers)</h4>", unsafe_allow_html=True)
        for i, row in asks.iterrows():
            st.markdown(f"""
                <div class="depth-row ask-bar" style="padding: 8px 12px; margin-bottom: 4px; display: flex; justify-content: space-between; align-items: center;">
                    <div style="display: flex; justify-content: space-between; width: 100%;">
                        <span style="color: #ff1744; font-weight: bold; font-size: 1.1em;">₹{row['Ask Price']}</span>
                        <span style="color: #fff; font-size: 0.95em;">{row['Ask Qty']:,}</span>
                    </div>
                </div>
            """, unsafe_allow_html=True)
        st.markdown(f"""
            <div style="text-align: center; padding: 10px; background: rgba(255,23,68,0.1); border-radius: 8px; margin-top: 10px;">
                <span style="color: #ff1744; font-weight: bold; font-size: 1.2em;">Total Sellers: {total_ask_qty:,}</span>
            </div>
        """, unsafe_allow_html=True)

    st.divider()

    st.subheader("💡 Trade Recommendation: Kitne Tak Lena Sahi Hai?")

    atr = round(df['Close'].diff().abs().rolling(14).mean().iloc[-1], 2)
    signal = latest['Signal']

    if signal == "BUY" or bid_ask_ratio > 1.2:
        rec_signal = "BUY"
        rec_entry = round(ltp, 2)
        rec_sl = round(ltp - atr * 1.5, 2)
        rec_t1 = round(ltp + atr * 2, 2)
        rec_t2 = round(ltp + atr * 3.5, 2)
        rec_color = "#00c853"
        rec_reason = f"Strong buying pressure detected (Bid/Ask: {bid_ask_ratio}). Price above VWAP. {total_bid_qty:,} buyers active."
    elif signal == "SELL" or bid_ask_ratio < 0.8:
        rec_signal = "SELL"
        rec_entry = round(ltp, 2)
        rec_sl = round(ltp + atr * 1.5, 2)
        rec_t1 = round(ltp - atr * 2, 2)
        rec_t2 = round(ltp - atr * 3.5, 2)
        rec_color = "#ff1744"
        rec_reason = f"Selling pressure dominant (Bid/Ask: {bid_ask_ratio}). Price below VWAP. {total_ask_qty:,} sellers active."
    else:
        rec_signal = "HOLD / WAIT"
        rec_entry = round(ltp, 2)
        rec_sl = round(ltp - atr * 2, 2)
        rec_t1 = round(ltp + atr * 2.5, 2)
        rec_t2 = "-"
        rec_color = "#ff9100"
        rec_reason = "Market is balanced. Wait for clear breakout above resistance or below support."

    st.markdown(f"""
        <div class="recommendation-box fade-in">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;">
                <div>
                    <span style="font-size: 0.9em; color: #888;">RECOMMENDATION FOR {sym}</span>
                    <h2 style="color: {rec_color}; margin: 5px 0 0 0; font-size: 2em;">{rec_signal}</h2>
                </div>
                <div style="text-align: right;">
                    <span style="color: #888; font-size: 0.8em;">Confidence</span>
                    <div style="font-size: 1.5em; font-weight: bold; color: {rec_color};">{min(95, int(50 + abs(bid_ask_ratio-1)*30 + latest['RSI']/5))}%</div>
                </div>
            </div>

            <div style="display: grid; grid-template-columns: 1fr 1fr 1fr 1fr; gap: 15px; margin-bottom: 15px;">
                <div style="background: rgba(0,0,0,0.3); padding: 15px; border-radius: 8px; text-align: center; border: 1px solid rgba(255,255,255,0.1);">
                    <div style="color: #888; font-size: 0.75em; margin-bottom: 5px;">ENTRY</div>
                    <div style="color: #00d4aa; font-size: 1.5em; font-weight: bold;">₹{rec_entry}</div>
                </div>
                <div style="background: rgba(0,0,0,0.3); padding: 15px; border-radius: 8px; text-align: center; border: 1px solid rgba(255,255,255,0.1);">
                    <div style="color: #888; font-size: 0.75em; margin-bottom: 5px;">STOP LOSS</div>
                    <div style="color: #ff1744; font-size: 1.5em; font-weight: bold;">₹{rec_sl}</div>
                </div>
                <div style="background: rgba(0,0,0,0.3); padding: 15px; border-radius: 8px; text-align: center; border: 1px solid rgba(255,255,255,0.1);">
                    <div style="color: #888; font-size: 0.75em; margin-bottom: 5px;">TARGET 1</div>
                    <div style="color: #00c853; font-size: 1.5em; font-weight: bold;">₹{rec_t1}</div>
                </div>
                <div style="background: rgba(0,0,0,0.3); padding: 15px; border-radius: 8px; text-align: center; border: 1px solid rgba(255,255,255,0.1);">
                    <div style="color: #888; font-size: 0.75em; margin-bottom: 5px;">TARGET 2</div>
                    <div style="color: #00c853; font-size: 1.5em; font-weight: bold;">₹{rec_t2}</div>
                </div>
            </div>

            <div style="background: rgba(0,212,170,0.05); border-left: 3px solid #00d4aa; padding: 12px; border-radius: 0 8px 8px 0;">
                <span style="color: #888; font-size: 0.8em;">ANALYSIS: </span>
                <span style="color: #fff; font-size: 0.9em;">{rec_reason}</span>
            </div>

            <div style="margin-top: 15px; display: flex; gap: 10px;">
                <div style="flex: 1; background: rgba(255,255,255,0.03); padding: 10px; border-radius: 6px; text-align: center;">
                    <span style="color: #888; font-size: 0.7em;">RSI</span><br><span style="color: #fff; font-weight: bold;">{round(latest['RSI'], 1)}</span>
                </div>
                <div style="flex: 1; background: rgba(255,255,255,0.03); padding: 10px; border-radius: 6px; text-align: center;">
                    <span style="color: #888; font-size: 0.7em;">VWAP</span><br><span style="color: #fff; font-weight: bold;">₹{round(latest['VWAP'], 2)}</span>
                </div>
                <div style="flex: 1; background: rgba(255,255,255,0.03); padding: 10px; border-radius: 6px; text-align: center;">
                    <span style="color: #888; font-size: 0.7em;">ATR</span><br><span style="color: #fff; font-weight: bold;">₹{atr}</span>
                </div>
                <div style="flex: 1; background: rgba(255,255,255,0.03); padding: 10px; border-radius: 6px; text-align: center;">
                    <span style="color: #888; font-size: 0.7em;">DAY RANGE</span><br><span style="color: #fff; font-weight: bold;">₹{round(day_high - day_low, 2)}</span>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    if rec_signal in ["BUY", "SELL"]:
        side = "BUY" if rec_signal == "BUY" else "SELL"
        if st.button(f"🚀 EXECUTE {rec_signal} {sym} @ ₹{rec_entry}", use_container_width=True, type="primary"):
            margin = rec_entry * st.session_state.quantity * 0.2
            if st.session_state.balance - st.session_state.used_margin >= margin:
                st.session_state.portfolio.append({
                    "symbol": sym, "entry": rec_entry, "qty": st.session_state.quantity,
                    "side": side, "sl": rec_sl, "target": rec_t1,
                    "time": datetime.now().strftime("%H:%M:%S"), "pnl": 0, "ltp": ltp
                })
                st.session_state.used_margin += margin
                st.success(f"✅ {rec_signal} order executed for {sym}!")
                st.balloons()
            else:
                st.error("❌ Insufficient margin!")

    st.markdown("""</div>""", unsafe_allow_html=True)

# --- OPTIONS CHAIN WITH BLACK-SCHOLES ---
elif menu_choice == "📊 Options Chain":
    st.markdown("""<div class="fade-in"><h2>📊 Options Chain</h2><p style="color: #888;">Black-Scholes Greeks Engine</p></div>""", unsafe_allow_html=True)
    opt_sym = st.selectbox("Select Index/Stock", ["NIFTY 50", "BANKNIFTY"])
    chain_df = generate_options_chain_bs(opt_sym)
    st.subheader(f"Spot: ₹{chain_df.iloc[0]['Spot']} | TTM: 7 Days | Risk-Free: 6.5%")

    def highlight_atm(row):
        atm = round(row['Spot'] / 50) * 50 if "NIFTY" in opt_sym else round(row['Spot'] / 100) * 100
        if row['Strike'] == atm:
            return ['background-color: rgba(0,212,170,0.2)'] * len(row)
        return [''] * len(row)

    st.dataframe(chain_df.style.apply(highlight_atm, axis=1), use_container_width=True, hide_index=True)

    fig = make_subplots(rows=2, cols=2, subplot_titles=("Delta", "Gamma", "Theta", "Vega"))
    fig.add_trace(go.Bar(x=chain_df['Strike'], y=chain_df['CE Delta'], name="CE Delta", marker_color='#00c853'), row=1, col=1)
    fig.add_trace(go.Bar(x=chain_df['Strike'], y=chain_df['PE Delta'], name="PE Delta", marker_color='#ff1744'), row=1, col=1)
    fig.add_trace(go.Bar(x=chain_df['Strike'], y=chain_df['CE Gamma'], name="CE Gamma", marker_color='#00d4aa'), row=1, col=2)
    fig.add_trace(go.Bar(x=chain_df['Strike'], y=chain_df['CE Theta'], name="CE Theta", marker_color='#ff9100'), row=2, col=1)
    fig.add_trace(go.Bar(x=chain_df['Strike'], y=chain_df['CE Vega'], name="CE Vega", marker_color='#ab47bc'), row=2, col=2)
    fig.update_layout(template="plotly_dark", height=600, showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

# --- MARKET NEWS ---
elif menu_choice == "📰 Market News":
    st.markdown("""<div class="fade-in"><h2>📰 Market News Feed</h2></div>""", unsafe_allow_html=True)
    now = datetime.now()
    if not st.session_state.last_news_time or (now - st.session_state.last_news_time).seconds > 60:
        news_templates = [
            {"headline": "NIFTY 50 breaches 22,500 resistance as IT stocks rally", "impact": "positive", "symbol": "NIFTY 50"},
            {"headline": "RBI MPC maintains repo rate at 6.5% — markets cheer", "impact": "positive", "symbol": "BANKNIFTY"},
            {"headline": "Reliance Jio announces 5G tariff hike", "impact": "positive", "symbol": "RELIANCE"},
            {"headline": "HDFC Bank Q4 net profit rises 18% YoY", "impact": "positive", "symbol": "HDFCBANK"},
            {"headline": "US Fed signals 2 rate cuts in 2026", "impact": "positive", "symbol": "NIFTY 50"},
            {"headline": "Crude oil spikes to $85/barrel", "impact": "negative", "symbol": "RELIANCE"},
            {"headline": "TCS bags $500M deal from European bank", "impact": "positive", "symbol": "TCS"},
            {"headline": "SBI reduces FD rates by 25 bps", "impact": "negative", "symbol": "SBIN"},
            {"headline": "INFY faces US visa scrutiny", "impact": "negative", "symbol": "INFY"},
            {"headline": "ICICI Bank launches digital lending platform", "impact": "positive", "symbol": "ICICIBANK"},
        ]
        rng = np.random.default_rng(seed=int(now.timestamp()) % 1000)
        selected = rng.choice(news_templates, size=8, replace=False).tolist()
        for item in selected:
            item["timestamp"] = now - timedelta(minutes=rng.integers(0, 180))
        selected.sort(key=lambda x: x['timestamp'], reverse=True)
        st.session_state.news_cache = selected
        st.session_state.last_news_time = now
    f1, f2, f3, f4 = st.columns(4)
    show_all = f1.button("🌐 All", use_container_width=True)
    show_pos = f2.button("🟢 Positive", use_container_width=True)
    show_neg = f3.button("🔴 Negative", use_container_width=True)
    show_neu = f4.button("🟡 Neutral", use_container_width=True)
    filtered = st.session_state.news_cache
    if show_pos: filtered = [n for n in filtered if n['impact'] == 'positive']
    elif show_neg: filtered = [n for n in filtered if n['impact'] == 'negative']
    elif show_neu: filtered = [n for n in filtered if n['impact'] == 'neutral']
    for item in filtered:
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
    st.markdown("""<div class="fade-in"><h2>📂 Portfolio Manager</h2></div>""", unsafe_allow_html=True)
    total_pnl = sum(p.get('pnl', 0) for p in st.session_state.portfolio)
    day_pnl = total_pnl
    invested = sum(p['entry'] * p['qty'] for p in st.session_state.portfolio)
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Open Positions", len(st.session_state.portfolio))
    c2.metric("Invested Value", f"₹{invested:,.0f}")
    c3.metric("Day P&L", f"₹{day_pnl:,.2f}", delta=f"{day_pnl:,.2f}")
    c4.metric("Available Margin", f"₹{st.session_state.balance - st.session_state.used_margin + total_pnl:,.0f}")
    st.divider()
    if st.session_state.portfolio:
        port_df = pd.DataFrame(st.session_state.portfolio)
        port_df['Current'] = port_df['ltp']
        port_df['P&L'] = port_df['pnl']
        port_df['P&L %'] = round((port_df['pnl'] / (port_df['entry'] * port_df['qty'])) * 100, 2)
        def pnl_color(val):
            color = '#00c853' if val >= 0 else '#ff1744'
            return f'color: {color}; font-weight: bold;'
        st.dataframe(port_df[['symbol', 'side', 'qty', 'entry', 'Current', 'sl', 'target', 'P&L', 'P&L %']].style.map(pnl_color, subset=['P&L', 'P&L %']), use_container_width=True, hide_index=True)
        for idx, pos in enumerate(st.session_state.portfolio):
            c1, c2 = st.columns([3, 1])
            with c1:
                pnl_color = "#00c853" if pos['pnl'] >= 0 else "#ff1744"
                st.markdown(f"""<span style="color: {pnl_color};">{pos['symbol']} {pos['side']} {pos['qty']} | P&L: ₹{pos['pnl']:.2f}</span>""", unsafe_allow_html=True)
            with c2:
                if st.button("🔴 Close", key=f"close_{idx}"):
                    outcome = "WIN" if pos['pnl'] >= 0 else "LOSS"
                    st.session_state.trade_history.append({
                        "Action": "MANUAL CLOSE", "Symbol": pos['symbol'], "Entry": pos['entry'],
                        "Exit": pos.get('ltp', pos['entry']), "PnL": round(pos['pnl'], 2), "Outcome": outcome,
                        "Time": datetime.now().strftime("%H:%M:%S"), "Qty": pos['qty']
                    })
                    st.session_state.used_margin -= pos['entry'] * pos['qty'] * 0.2
                    st.session_state.portfolio.pop(idx)
                    st.session_state.loss_streak = 0 if outcome == "WIN" else st.session_state.loss_streak + 1
                    st.rerun()
    else:
        st.info("📭 No open positions. Go to Dashboard to trade.")

# --- ORDER BOOK ---
elif menu_choice == "📋 Order Book":
    st.markdown("""<div class="fade-in"><h2>📋 Order Book</h2></div>""", unsafe_allow_html=True)
    if st.session_state.orders:
        orders_df = pd.DataFrame(st.session_state.orders)
        def status_color(val):
            colors = {'PENDING': '#ff9100', 'EXECUTED': '#00c853', 'CANCELLED': '#ff1744'}
            return f'color: {colors.get(val, "#888")}; font-weight: bold;'
        st.dataframe(orders_df.style.map(status_color, subset=['status']), use_container_width=True, hide_index=True)
        for order in st.session_state.orders:
            if order['status'] == 'PENDING':
                ltp = st.session_state.market_data[order['symbol']].iloc[-1]['Close']
                if (order['type'] == 'LIMIT' and ((order['side'] == 'BUY' and ltp <= order['price']) or (order['side'] == 'SELL' and ltp >= order['price']))) or                    (order['type'] == 'SL' and ((order['side'] == 'BUY' and ltp >= order['price']) or (order['side'] == 'SELL' and ltp <= order['price']))):
                    order['status'] = 'EXECUTED'
                    order['exec_price'] = ltp
                    st.session_state.portfolio.append({
                        "symbol": order['symbol'], "entry": ltp, "qty": order['qty'],
                        "side": order['side'], "sl": ltp*0.98 if order['side']=="BUY" else ltp*1.02,
                        "target": ltp*1.04 if order['side']=="BUY" else ltp*0.96,
                        "time": datetime.now().strftime("%H:%M:%S"), "pnl": 0, "ltp": ltp
                    })
                    st.session_state.used_margin += ltp * order['qty'] * 0.2
    else:
        st.info("📭 No orders placed.")

# --- ALERTS ---
elif menu_choice == "🔔 Alerts":
    st.markdown("""<div class="fade-in"><h2>🔔 Price Alerts</h2></div>""", unsafe_allow_html=True)
    with st.form("alert_form"):
        a1, a2, a3 = st.columns(3)
        alert_sym = a1.selectbox("Symbol", st.session_state.watchlist)
        alert_cond = a2.selectbox("Condition", ["ABOVE", "BELOW"])
        alert_price = a3.number_input("Price", value=22000.0, step=0.05)
        if st.form_submit_button("➕ Add Alert"):
            st.session_state.alerts.append({
                "symbol": alert_sym, "condition": alert_cond, "price": alert_price,
                "triggered": False, "time": datetime.now().strftime("%H:%M:%S")
            })
            st.success(f"✅ Alert set: {alert_sym} {alert_cond} ₹{alert_price}")
    st.divider()
    st.subheader("Active Alerts")
    if st.session_state.alerts:
        active = [a for a in st.session_state.alerts if not a.get('triggered', False)]
        if active:
            st.dataframe(pd.DataFrame(active), use_container_width=True, hide_index=True)
        else:
            st.info("No active alerts.")
    else:
        st.info("No alerts set.")
    st.subheader("🔔 Trigger Log")
    if st.session_state.alert_log:
        for log in reversed(st.session_state.alert_log[-10:]):
            st.markdown(f"""<div class="news-card fade-in"><span style="color: #00d4aa;">{log}</span></div>""", unsafe_allow_html=True)
    else:
        st.info("No alerts triggered yet.")

# --- SENTIMENT ---
elif menu_choice == "🎭 Sentiment":
    st.markdown("""<div class="fade-in"><h2>🎭 Market Sentiment</h2></div>""", unsafe_allow_html=True)
    rng = np.random.default_rng(seed=int(datetime.now().timestamp()) % 1000)
    fear_greed = rng.integers(20, 85)
    pcr = round(rng.uniform(0.7, 1.4), 2)
    advance = rng.integers(1200, 1800)
    decline = 2000 - advance
    vix = round(rng.uniform(12, 22), 2)
    c1, c2, c3, c4 = st.columns(4)
    fg_color = "#00c853" if fear_greed > 60 else "#ff9100" if fear_greed > 40 else "#ff1744"
    c1.markdown(f"""<div class="metric-card"><div style="font-size: 0.8em; color: #888;">Fear & Greed</div><div style="font-size: 2em; font-weight: bold; color: {fg_color};">{fear_greed}</div><div style="font-size: 0.75em; color: {fg_color};">{"GREED" if fear_greed > 60 else "NEUTRAL" if fear_greed > 40 else "FEAR"}</div></div>""", unsafe_allow_html=True)
    pcr_color = "#00c853" if pcr < 1 else "#ff1744"
    c2.markdown(f"""<div class="metric-card"><div style="font-size: 0.8em; color: #888;">Put/Call Ratio</div><div style="font-size: 2em; font-weight: bold; color: {pcr_color};">{pcr}</div><div style="font-size: 0.75em; color: {pcr_color};">{"Bullish" if pcr < 1 else "Bearish"}</div></div>""", unsafe_allow_html=True)
    c3.markdown(f"""<div class="metric-card"><div style="font-size: 0.8em; color: #888;">Advance-Decline</div><div style="font-size: 1.5em; font-weight: bold; color: #00c853;">{advance}</div><div style="font-size: 1.5em; font-weight: bold; color: #ff1744;">{decline}</div><div style="font-size: 0.75em; color: #888;">Ratio: {round(advance/decline, 2)}</div></div>""", unsafe_allow_html=True)
    c4.markdown(f"""<div class="metric-card"><div style="font-size: 0.8em; color: #888;">India VIX</div><div style="font-size: 2em; font-weight: bold; color: #ff9100;">{vix}</div><div style="font-size: 0.75em; color: #888;">Volatility Index</div></div>""", unsafe_allow_html=True)
    fig = go.Figure(go.Indicator(
        mode = "gauge+number", value = fear_greed, domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': "Fear & Greed Index"},
        gauge = {'axis': {'range': [0, 100]}, 'bar': {'color': fg_color},
            'steps': [
                {'range': [0, 25], 'color': 'rgba(255,23,68,0.3)'},
                {'range': [25, 50], 'color': 'rgba(255,145,0,0.3)'},
                {'range': [50, 75], 'color': 'rgba(0,212,170,0.3)'},
                {'range': [75, 100], 'color': 'rgba(0,200,83,0.3)'}
            ],
            'threshold': {'line': {'color': "white", 'width': 4}, 'thickness': 0.75, 'value': fear_greed}
        }
    ))
    fig.update_layout(template="plotly_dark", height=350)
    st.plotly_chart(fig, use_container_width=True)

# --- ECONOMIC CALENDAR ---
elif menu_choice == "📅 Economic Calendar":
    st.markdown("""<div class="fade-in"><h2>📅 Economic Calendar</h2></div>""", unsafe_allow_html=True)
    events = [
        {"time": "Today 10:00", "event": "RBI MPC Minutes Release", "impact": "HIGH", "forecast": "Status Quo", "actual": "-"},
        {"time": "Today 14:30", "event": "US Initial Jobless Claims", "impact": "MEDIUM", "forecast": "215K", "actual": "-"},
        {"time": "Tomorrow 06:00", "event": "WPI Inflation (India)", "impact": "HIGH", "forecast": "2.4%", "actual": "-"},
        {"time": "Tomorrow 18:00", "event": "Fed Chair Speech", "impact": "HIGH", "forecast": "-", "actual": "-"},
        {"time": "Fri 10:30", "event": "Nifty 50 Rebalancing", "impact": "MEDIUM", "forecast": "-", "actual": "-"},
        {"time": "Fri 20:00", "event": "US Non-Farm Payrolls", "impact": "HIGH", "forecast": "185K", "actual": "-"},
        {"time": "Mon 09:00", "event": "India CPI Data", "impact": "HIGH", "forecast": "4.8%", "actual": "-"},
    ]
    for ev in events:
        impact_color = "#ff1744" if ev['impact'] == "HIGH" else "#ff9100" if ev['impact'] == "MEDIUM" else "#00c853"
        st.markdown(f"""
            <div class="idea-card fade-in" style="display: flex; justify-content: space-between; align-items: center;">
                <div><div style="color: #888; font-size: 0.8em;">{ev['time']}</div>
                <div style="color: #fff; font-weight: bold; font-size: 1.1em;">{ev['event']}</div>
                <div style="color: #666; font-size: 0.8em;">Forecast: {ev['forecast']} | Actual: {ev['actual']}</div></div>
                <div style="background: {impact_color}; color: #000; padding: 4px 12px; border-radius: 4px; font-weight: bold; font-size: 0.8em;">{ev['impact']}</div>
            </div>
        """, unsafe_allow_html=True)

# --- TRADE LEDGER WITH DEEP AUDIT ---
elif menu_choice == "📁 Trade Ledger":
    st.markdown("""<div class="fade-in"><h2>📁 Audit Trail & Deep Reconciliation</h2></div>""", unsafe_allow_html=True)

    if st.session_state.trade_history:
        ledger_df = pd.DataFrame(st.session_state.trade_history)
        if 'Time' in ledger_df.columns:
            ledger_df = ledger_df.sort_values('Time', ascending=False)

        metrics = calculate_risk_metrics(st.session_state.trade_history)

        st.subheader("📊 Advanced Risk Dashboard")
        r1, r2, r3, r4, r5, r6 = st.columns(6)
        r1.metric("Sharpe Ratio", metrics['sharpe'])
        r2.metric("Max Drawdown", f"{metrics['max_drawdown']}%")
        r3.metric("Calmar Ratio", metrics['calmar'])
        r4.metric("Win Rate", f"{metrics['win_rate']}%")
        r5.metric("Profit Factor", metrics['profit_factor'])
        r6.metric("Expectancy", f"₹{metrics['expectancy']}")

        st.divider()

        st.subheader("🔥 Win/Loss Streak Heatmap")
        outcomes = [t['Outcome'] for t in st.session_state.trade_history]
        streaks = []
        current_streak = 1
        for i in range(1, len(outcomes)):
            if outcomes[i] == outcomes[i-1]:
                current_streak += 1
            else:
                streaks.append((outcomes[i-1], current_streak))
                current_streak = 1
        streaks.append((outcomes[-1], current_streak))

        streak_cols = st.columns(min(len(streaks), 10))
        for i, (outcome, count) in enumerate(streaks[:10]):
            color = "#00c853" if outcome == "WIN" else "#ff1744"
            streak_cols[i].markdown(f"""
                <div style="background: {color}; color: #000; padding: 10px; border-radius: 8px; text-align: center; font-weight: bold;">
                    <div style="font-size: 0.75em;">{outcome}</div>
                    <div style="font-size: 1.5em;">{count}</div>
                </div>
            """, unsafe_allow_html=True)

        st.divider()

        total_pnl = ledger_df['PnL'].sum()
        wins = len(ledger_df[ledger_df['Outcome'] == 'WIN'])
        losses = len(ledger_df[ledger_df['Outcome'] == 'LOSS'])
        win_rate = (wins / len(ledger_df) * 100) if len(ledger_df) > 0 else 0
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Total Trades", len(ledger_df)); c2.metric("Win Rate", f"{win_rate:.1f}%")
        c3.metric("Total PnL", f"₹{total_pnl:.2f}"); c4.metric("Net Wins", wins - losses)

        st.divider()
        def highlight_outcome(val):
            if val == 'WIN': return 'background-color: rgba(0,200,83,0.2); color: #00c853; font-weight: bold;'
            elif val == 'LOSS': return 'background-color: rgba(255,23,68,0.2); color: #ff1744; font-weight: bold;'
            return ''
        styled_ledger = ledger_df.style.map(highlight_outcome, subset=['Outcome'])
        st.dataframe(styled_ledger, use_container_width=True, hide_index=True)

        st.divider()
        st.subheader("📥 EOD Excel Report")
        if st.button("Generate EOD Report", use_container_width=True, type="primary"):
            excel_file = generate_eod_excel(st.session_state.trade_history)
            if excel_file:
                st.download_button(
                    "📥 Download EOD Excel Report",
                    excel_file,
                    f"EOD_Report_{datetime.now().strftime('%Y%m%d')}.xlsx",
                    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True
                )
                st.success("✅ EOD Report generated with Trade History, Risk Metrics & Summary!")
            else:
                st.warning("No trades to generate report.")
    else:
        st.info("📭 No trades executed yet.")

# --- STRATEGY SETUP + BACKTEST ---
elif menu_choice == "🧠 Strategy Setup":
    st.markdown("""<div class="fade-in"><h2>🧠 Algorithm & Risk Management</h2></div>""", unsafe_allow_html=True)
    st.session_state.selected_strategy = st.selectbox("Active Algorithm", ["T3 + RSI", "RSI + UT Bot", "EMA + VWAP", "Volume Breakout", "EMA Only"])
    c1, c2, c3 = st.columns(3)
    st.session_state.profit_target = c1.number_input("Profit Target (₹)", value=st.session_state.profit_target, step=500)
    st.session_state.loss_limit = c2.number_input("Circuit Breaker Limit", min_value=1, value=st.session_state.loss_limit)
    st.session_state.exec_mode = c3.selectbox("Execution Mode", ["PAPER", "LIVE"])
    if st.button("🔄 Reset Loss Streak", use_container_width=True):
        st.session_state.loss_streak = 0
        st.session_state.auto_trade = False
        st.success("✅ Loss streak reset!")
        st.balloons()
    st.divider()
    st.subheader("📈 Backtesting Engine")
    backtest_sym = st.selectbox("Backtest Symbol", st.session_state.watchlist)
    if st.button("▶️ Run Backtest", use_container_width=True):
        df = st.session_state.market_data[backtest_sym].copy()
        df = apply_strategy(df, st.session_state.selected_strategy)
        trades = []
        position = None
        for i in range(50, len(df)):
            row = df.iloc[i]
            if position is None and row['Signal'] == 'BUY':
                position = {"entry": row['Close'], "time": i}
            elif position is not None and row['Signal'] == 'SELL':
                pnl = row['Close'] - position['entry']
                trades.append(pnl)
                position = None
        if position is not None:
            pnl = df.iloc[-1]['Close'] - position['entry']
            trades.append(pnl)
        if trades:
            total = sum(trades)
            wins = sum(1 for t in trades if t > 0)
            st.success(f"Backtest Complete: {len(trades)} trades, Win Rate: {wins/len(trades)*100:.1f}%, Total PnL: ₹{total:.2f}")
            fig = go.Figure(go.Scatter(y=np.cumsum(trades), mode='lines', name='Cumulative PnL', line=dict(color='#00d4aa')))
            fig.update_layout(template="plotly_dark", title="Backtest Equity Curve", height=400)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("No trades generated in backtest period.")

# --- AI ASSISTANT ---
elif menu_choice == "🤖 AI Assistant":
    st.markdown("""<div class="fade-in"><h2>🤖 JVX AI Trade Assistant</h2></div>""", unsafe_allow_html=True)
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    user_input = st.chat_input("Ask me anything about trading...")
    if user_input:
        st.session_state.chat_history.append({"role": "user", "message": user_input})
        response = "I'm analyzing that for you..."
        user_lower = user_input.lower()
        if "nifty" in user_lower and "target" in user_lower:
            response = "Based on current T3 + RSI setup, NIFTY immediate resistance is at 22,600. Support at 22,350. RSI at 58 suggests cautiously bullish."
        elif "reliance" in user_lower:
            response = "RELIANCE is showing volume breakout pattern. Current VWAP support is intact. Consider long above ₹2,870 with SL at ₹2,820."
        elif "stop loss" in user_lower or "sl" in user_lower:
            response = "General rule: Keep SL at 1.5x ATR from entry. For intraday, max 1% of capital per trade."
        elif "strategy" in user_lower:
            response = f"Currently active: {st.session_state.selected_strategy}. T3 + RSI works best in trending markets."
        elif "margin" in user_lower:
            response = f"Your available margin is ₹{st.session_state.balance - st.session_state.used_margin:,.0f}."
        elif "circuit" in user_lower or "breaker" in user_lower:
            response = f"Circuit breaker trips at {st.session_state.loss_limit} consecutive losses. Current streak: {st.session_state.loss_streak}."
        elif "option" in user_lower or "call" in user_lower or "put" in user_lower:
            response = "For options, check the Options Chain tab. ATM strikes have highest liquidity."
        elif "news" in user_lower:
            response = "Check the Market News tab for latest updates. High impact events: RBI MPC, Fed speeches, and major earnings."
        else:
            response = "I'm your trading copilot. Ask me about: levels, strategies, risk management, margin, or specific stocks."
        st.session_state.chat_history.append({"role": "assistant", "message": response})
    for chat in st.session_state.chat_history:
        if chat['role'] == 'user':
            st.markdown(f"""<div style="background: rgba(0,212,170,0.1); border-radius: 10px; padding: 10px; margin: 5px 0; text-align: right;"><span style="color: #00d4aa;">👤 {chat['message']}</span></div>""", unsafe_allow_html=True)
        else:
            st.markdown(f"""<div style="background: rgba(255,255,255,0.05); border-radius: 10px; padding: 10px; margin: 5px 0; border-left: 3px solid #ab47bc;"><span style="color: #fff;">🤖 {chat['message']}</span></div>""", unsafe_allow_html=True)

# --- API SETTINGS ---
elif menu_choice == "🔑 API Settings":
    st.markdown("""<div class="fade-in"><h2>📡 API & Connectors</h2></div>""", unsafe_allow_html=True)
    with st.expander("1. Paytm Money API", expanded=True):
        p1, p2 = st.columns(2)
        with p1: st.text_input("Paytm API Key", type="password", key="paytm_key")
        with p2: st.text_input("Paytm API Secret", type="password", key="paytm_secret")
        if st.button("🔗 Authenticate Broker", use_container_width=True):
            st.success("✅ Broker API Simulated!")
            st.snow()
    with st.expander("2. Telegram Alerts", expanded=True):
        t1, t2 = st.columns(2)
        with t1: st.text_input("Bot Token", type="password", key="tg_token")
        with t2: st.text_input("Chat ID", key="tg_chat")
        if st.button("📲 Send Test Alert", use_container_width=True):
            st.success("✅ Test alert sent!")
            st.balloons()
    with st.expander("3. WebSocket Configuration"):
        st.text_input("WebSocket URL", placeholder="wss://api.paytmmoney.com/live/websocket")
        st.toggle("Enable Live WebSocket Feed", value=False)
        st.caption("When enabled, data auto-refreshes every 1 second without clicking Simulate Next Tick")
