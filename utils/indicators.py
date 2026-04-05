import pandas as pd
import numpy as np
import ta

class TechnicalIndicators:
    """Advanced technical indicators calculation"""
    
    @staticmethod
    def add_all_indicators(df):
        """Add all technical indicators to dataframe"""
        if df is None or df.empty:
            return df
        
        df = df.copy()
        
        # Moving Averages
        df['sma_20'] = ta.trend.sma_indicator(df['close'], window=20)
        df['sma_50'] = ta.trend.sma_indicator(df['close'], window=50)
        df['ema_9'] = ta.trend.ema_indicator(df['close'], window=9)
        df['ema_20'] = ta.trend.ema_indicator(df['close'], window=20)
        
        # Bollinger Bands
        bb = ta.volatility.BollingerBands(df['close'], window=20, window_dev=2)
        df['bb_upper'] = bb.bollinger_hband()
        df['bb_middle'] = bb.bollinger_mavg()
        df['bb_lower'] = bb.bollinger_lband()
        df['bb_width'] = (df['bb_upper'] - df['bb_lower']) / df['bb_middle']
        
        # RSI
        df['rsi'] = ta.momentum.rsi(df['close'], window=14)
        
        # MACD
        macd = ta.trend.MACD(df['close'])
        df['macd'] = macd.macd()
        df['macd_signal'] = macd.macd_signal()
        df['macd_diff'] = macd.macd_diff()
        
        # Stochastic
        stoch = ta.momentum.StochasticOscillator(df['high'], df['low'], df['close'])
        df['stoch_k'] = stoch.stoch()
        df['stoch_d'] = stoch.stoch_signal()
        
        # ATR (Average True Range)
        df['atr'] = ta.volatility.average_true_range(df['high'], df['low'], df['close'], window=14)
        
        # Volume indicators
        df['volume_sma'] = df['volume'].rolling(window=20).mean()
        df['volume_ratio'] = df['volume'] / df['volume_sma']
        
        # Additional momentum indicators
        df['adx'] = ta.trend.adx(df['high'], df['low'], df['close'], window=14)
        df['williams_r'] = ta.momentum.williams_r(df['high'], df['low'], df['close'], lbp=14)
        df['cci'] = ta.trend.cci(df['high'], df['low'], df['close'], window=20)
        
        return df
    
    @staticmethod
    def generate_signals(df):
        """Generate buy/sell signals based on multiple indicators"""
        if df is None or df.empty:
            return df
        
        df = df.copy()
        
        # Initialize signals
        df['signal'] = 0
        df['signal_strength'] = 0
        
        # RSI signals
        df['rsi_signal'] = 0
        df.loc[df['rsi'] < 30, 'rsi_signal'] = 1  # Oversold - Buy
        df.loc[df['rsi'] > 70, 'rsi_signal'] = -1  # Overbought - Sell
        
        # MACD signals
        df['macd_signal_cross'] = 0
        df.loc[(df['macd'] > df['macd_signal']) & (df['macd'].shift(1) <= df['macd_signal'].shift(1)), 'macd_signal_cross'] = 1
        df.loc[(df['macd'] < df['macd_signal']) & (df['macd'].shift(1) >= df['macd_signal'].shift(1)), 'macd_signal_cross'] = -1
        
        # Bollinger Band signals
        df['bb_signal'] = 0
        df.loc[df['close'] < df['bb_lower'], 'bb_signal'] = 1
        df.loc[df['close'] > df['bb_upper'], 'bb_signal'] = -1
        
        # Stochastic signals
        df['stoch_signal'] = 0
        df.loc[(df['stoch_k'] < 20) & (df['stoch_d'] < 20), 'stoch_signal'] = 1
        df.loc[(df['stoch_k'] > 80) & (df['stoch_d'] > 80), 'stoch_signal'] = -1
        
        # Combine signals (weighted average)
        df['combined_signal'] = (
            df['rsi_signal'] * 0.25 +
            df['macd_signal_cross'] * 0.3 +
            df['bb_signal'] * 0.25 +
            df['stoch_signal'] * 0.2
        )
        
        # Final signal threshold
        df['signal'] = 0
        df.loc[df['combined_signal'] > 0.4, 'signal'] = 1  # Buy
        df.loc[df['combined_signal'] < -0.4, 'signal'] = -1  # Sell
        
        # Signal strength (0-100)
        df['signal_strength'] = abs(df['combined_signal']) * 100
        
        return df
