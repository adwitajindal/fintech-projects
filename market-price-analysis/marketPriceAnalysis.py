import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import yfinance as yf
from datetime import date

st.set_page_config(page_title="Stock Market Analysis")

st.title("Market Price Analysis")

# --------------- Inputs --------------
stock_name = st.text_input("Enter Stock Ticker (e.g., RELIANCE.NS, TCS.NS)")

col1, col2 = st.columns(2)

with col1:
    start_date = st.date_input("Start Date", value=date(2020, 1, 1))

with col2:
    end_date = st.date_input("End Date", value=date.today())

# -------------- Validation --------------
if start_date > date.today() or end_date > date.today():
    st.error("Future dates are not allowed.")

elif end_date <= start_date:
    st.error("End date must be after start date.")

elif stock_name:

    df = yf.download(stock_name, start=start_date, end=end_date)

    if df.empty:
        st.error("No data found. Check ticker symbol or date range.")
    else:
        df = df[['Close']]
        df['Daily_Return'] = df['Close'].pct_change()
        df['SMA_10'] = df['Close'].rolling(10).mean()
        df['SMA_30'] = df['Close'].rolling(30).mean()

        # ------------ Price Chart --------------
        st.subheader("Price Trend with SMA")

        fig1, ax1 = plt.subplots(figsize=(6,3))
        ax1.plot(df['Close'], label='Close Price')
        ax1.plot(df['SMA_10'], label='SMA 10')
        ax1.plot(df['SMA_30'], label='SMA 30')
        ax1.legend()
        plt.tight_layout()
        st.pyplot(fig1)

        # ------------- Histogram -----------------
        st.subheader("Daily Returns Distribution")

        fig2, ax2 = plt.subplots(figsize=(6,3))
        df['Daily_Return'].dropna().hist(bins=50, ax=ax2)
        plt.tight_layout()
        st.pyplot(fig2)

        # ------------- Top 5 Days ----------------
        top5 = df.sort_values('Daily_Return', ascending=False).head(5).copy()

        top5['Daily_Return'] = top5['Daily_Return'].round(2)
        top5['Close'] = top5['Close'].round(2) 

        st.dataframe(top5[['Close', 'Daily_Return']])

        # ----------- Volatility --------------------
        volatility = df['Daily_Return'].std()
        st.write("Volatility:", round(volatility, 5))