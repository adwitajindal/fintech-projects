import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="Stock Candlestick Visualizer", layout="wide")


st.markdown("""
    <style>
    .main {
        padding-top: 2rem;
    }
    h1 {
        color: #1f77b4;
        text-align: center;
        font-size: 2.5rem;
        margin-bottom: 0rem;
    }
    .subtitle {
        text-align: center;
        color: #666;
        margin-bottom: 2rem;
        font-size: 1rem;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("📈 Stock Candlestick Visualizer")
st.markdown('<div class="subtitle">Real-time stock analysis with technical indicators</div>', unsafe_allow_html=True)

# ------------------- Sidebar Inputs ---------------------
st.sidebar.header("⚙️ Configuration")
ticker = st.sidebar.text_input("Enter Stock Ticker", "AAPL", key="ticker_input").upper()
period = st.sidebar.selectbox("Select Period", ["1mo", "3mo", "6mo", "1y", "5y"], key="period_select")
interval = st.sidebar.selectbox("Select Interval", ["1d", "1wk", "1mo"], key="interval_select")

st.sidebar.divider()
show_sma = st.sidebar.checkbox("Show Moving Averages", value=True)
show_signals = st.sidebar.checkbox("Show Trading Signals", value=True)
show_markers = st.sidebar.checkbox("Show Bullish/Bearish Markers", value=True)

# ------------------- Fetching the data ---------------------
@st.cache_data
def fetch_stock_data(ticker, period, interval):
    try:
        data = yf.download(ticker, period=period, interval=interval, progress=False)
        
        if data.empty:
            return pd.DataFrame()
        
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.get_level_values(0)
        
        data = data.dropna()
        
        return data
    except KeyError as e:
        st.error(f"Ticker not found: {ticker}")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Error fetching data: {type(e).__name__}: {str(e)}")
        return pd.DataFrame()

with st.spinner(f"📊 Fetching data for {ticker}..."):
    data = fetch_stock_data(ticker, period, interval)

if data.empty:
    st.error("❌ Invalid ticker symbol or no data available")
    st.stop()

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Current Price", f"${float(data['Close'].iloc[-1]):.2f}")
with col2:
    change = float(data['Close'].iloc[-1]) - float(data['Close'].iloc[0])
    change_pct = (change / float(data['Close'].iloc[0])) * 100
    st.metric("Period Change", f"${change:.2f}", f"{change_pct:.2f}%")
with col3:
    st.metric("Data Points", len(data))

st.divider()

# ------------------- Candlestick Chart ---------------------
fig = go.Figure()

fig.add_trace(go.Candlestick(
    x=data.index,
    open=data["Open"].astype(float),
    high=data["High"].astype(float),
    low=data["Low"].astype(float),
    close=data["Close"].astype(float),
    name='OHLC',
    increasing_line_color='#26a69a',
    decreasing_line_color='#ef553b'
))

# ------------------- Add moving averages ---------------------
data['SMA20'] = data['Close'].rolling(window=20).mean()
data['SMA50'] = data['Close'].rolling(window=50).mean()

if show_sma:
    fig.add_trace(go.Scatter(
        x=data.index,
        y=data['SMA20'],
        line=dict(width=2, color='#636EFA'),
        name='SMA 20',
        hovertemplate='<b>SMA 20</b><br>%{x|%Y-%m-%d}<br>$%{y:.2f}<extra></extra>'
    ))

    fig.add_trace(go.Scatter(
        x=data.index,
        y=data['SMA50'],
        line=dict(width=2, color='#FF6692'),
        name='SMA 50',
        hovertemplate='<b>SMA 50</b><br>%{x|%Y-%m-%d}<br>$%{y:.2f}<extra></extra>'
    ))

# ------------------- highlighting bullish and bearish days -------------
if show_markers:
    data['Bullish'] = data['Close'] > data['Open']

    bullish_days = data[data['Bullish']]
    bearish_days = data[~data['Bullish']]

    fig.add_trace(go.Scatter(
        x=bullish_days.index,
        y=bullish_days['Close'],
        mode='markers',
        marker=dict(symbol='triangle-up', size=6, color='#26a69a'),
        name='Bullish',
        hovertemplate='<b>Bullish</b><br>%{x|%Y-%m-%d}<extra></extra>',
        showlegend=True
    ))

    fig.add_trace(go.Scatter(
        x=bearish_days.index,
        y=bearish_days['Close'], # FIX: Changed 'close' to 'Close'
        mode='markers',
        marker=dict(symbol='triangle-down', size=6, color='#ef553b'),
        name='Bearish',
        hovertemplate='<b>Bearish</b><br>%{x|%Y-%m-%d}<extra></extra>',
        showlegend=True
    ))


# ------------------- Adding simple trading signals ---------------------
if show_signals:
    data['Signal'] = 0
    data.loc[data['SMA20'] > data['SMA50'], 'Signal'] = 1
    data['Position'] = data['Signal'].diff()

    buy_signals = data[data['Position'] == 1]
    sell_signals = data[data['Position'] == -1]

    fig.add_trace(go.Scatter(
        x=buy_signals.index,
        y=buy_signals['Close'],
        mode='markers',
        marker=dict(symbol='star', size=15, color='#00CC96'),
        name='Buy Signal',
        hovertemplate='<b>BUY</b><br>%{x|%Y-%m-%d}<br>$%{y:.2f}<extra></extra>'
    ))

    fig.add_trace(go.Scatter(
        x=sell_signals.index,
        y=sell_signals['Close'], # FIX: Changed 'close' to 'Close'
        mode='markers',
        marker=dict(symbol='x', size=15, color='#FF6692'),
        name='Sell Signal',
        hovertemplate='<b>SELL</b><br>%{x|%Y-%m-%d}<br>$%{y:.2f}<extra></extra>'
    ))

# ------------------- Update layout and display chart ---------------------
fig.update_layout(
    title=dict(
        text=f"<b>{ticker} Candlestick Chart</b> | Period: {period} | Interval: {interval}",
        x=0.5,
        xanchor='center',
        font=dict(size=18)
    ),
    yaxis=dict(
        autorange=True,
        title="Price (USD)",
        gridcolor='#e5e5e5',
        showgrid=True
    ),
    xaxis=dict(
        title="Date",
        gridcolor='#e5e5e5',
        showgrid=True,
        range=[data.index[max(0, len(data) - 60)], data.index[-1]]
    ),
    xaxis_rangeslider_visible=False,
    template='plotly_white',
    hovermode='x unified',
    height=600,
    showlegend=True,
    legend=dict(
        x=0.01,
        y=0.99,
        bgcolor='rgba(255, 255, 255, 0.8)',
        bordercolor='#e5e5e5',
        borderwidth=1
    ),
    font=dict(family="Arial, sans-serif", size=12),
    margin=dict(l=50, r=50, t=80, b=50)
)

st.plotly_chart(fig, use_container_width=True)

# ------------------- Display Data Table ---------------------
st.divider()
st.subheader("📊 Data Summary")
display_data = data[['Open', 'High', 'Low', 'Close', 'Volume']].tail(10).copy()
display_data['Change %'] = ((display_data['Close'] - display_data['Open']) / display_data['Open'] * 100).round(2)
st.dataframe(display_data.style.format("{:.2f}"), use_container_width=True)