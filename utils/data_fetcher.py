import yfinance as yf
import ccxt
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import streamlit as st

class DataFetcher:
    """Market data fetcher for forex, crypto, and commodities"""
    
    # Asset categories with symbols
    FOREX_PAIRS = {
        "EUR/USD": "EURUSD=X",
        "GBP/USD": "GBPUSD=X",
        "USD/JPY": "JPY=X",
        "AUD/USD": "AUDUSD=X",
        "USD/CAD": "CAD=X",
        "USD/CHF": "CHF=X",
        "NZD/USD": "NZDUSD=X"
    }
    
    CRYPTO_PAIRS = {
        "BTC/USD": "BTC-USD",
        "ETH/USD": "ETH-USD",
        "XRP/USD": "XRP-USD",
        "SOL/USD": "SOL-USD",
        "ADA/USD": "ADA-USD",
        "DOGE/USD": "DOGE-USD"
    }
    
    COMMODITIES = {
        "Gold (XAU/USD)": "GC=F",
        "Silver (XAG/USD)": "SI=F",
        "Crude Oil": "CL=F"
    }
    
    @staticmethod
    @st.cache_data(ttl=60)
    def fetch_historical_data(symbol, interval="1h", period="7d"):
        """Fetch historical price data"""
        try:
            ticker = yf.Ticker(symbol)
            df = ticker.history(period=period, interval=interval)
            
            if df.empty:
                return None
                
            df = df.rename(columns={
                'Open': 'open',
                'High': 'high',
                'Low': 'low',
                'Close': 'close',
                'Volume': 'volume'
            })
            
            # Add additional columns
            df['returns'] = df['close'].pct_change()
            df['log_returns'] = np.log(df['close'] / df['close'].shift(1))
            
            return df
        except Exception as e:
            st.error(f"Error fetching data: {str(e)}")
            return None
    
    @staticmethod
    def fetch_live_price(symbol):
        """Fetch latest price"""
        try:
            ticker = yf.Ticker(symbol)
            data = ticker.history(period="1d", interval="1m")
            if not data.empty:
                return data['Close'].iloc[-1]
            return None
        except:
            return None
    
    @staticmethod
    def get_all_assets():
        """Get all available assets"""
        assets = {}
        assets.update(DataFetcher.FOREX_PAIRS)
        assets.update(DataFetcher.CRYPTO_PAIRS)
        assets.update(DataFetcher.COMMODITIES)
        return assets
