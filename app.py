import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# Import utilities
from utils.data_fetcher import DataFetcher
from utils.indicators import TechnicalIndicators
from utils.risk_manager import RiskManager
from utils.ai_signals import AITradingSignals
from utils.chart_config import ChartConfig

# Page configuration
st.set_page_config(
    page_title="AI Trading Dashboard",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load custom CSS
def load_css():
    with open('styles/mobile.css') as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

load_css()

# Initialize session state
if 'risk_manager' not in st.session_state:
    st.session_state.risk_manager = RiskManager()
if 'ai_model' not in st.session_state:
    st.session_state.ai_model = AITradingSignals()
if 'data_fetcher' not in st.session_state:
    st.session_state.data_fetcher = DataFetcher()

# Sidebar
with st.sidebar:
    st.title("⚡ AI Trading Dashboard")
    st.markdown("---")
    
    # Asset selection
    st.subheader("📊 Market Selection")
    asset_type = st.selectbox(
        "Asset Type",
        ["Forex", "Crypto", "Commodities"],
        help="Select market type for trading"
    )
    
    if asset_type == "Forex":
        selected_asset = st.selectbox(
            "Currency Pair", 
            list(DataFetcher.FOREX_PAIRS.keys())
        )
        symbol = DataFetcher.FOREX_PAIRS[selected_asset]
    elif asset_type == "Crypto":
        selected_asset = st.selectbox(
            "Cryptocurrency",
            list(DataFetcher.CRYPTO_PAIRS.keys())
        )
        symbol = DataFetcher.CRYPTO_PAIRS[selected_asset]
    else:
        selected_asset = st.selectbox(
            "Commodity",
            list(DataFetcher.COMMODITIES.keys())
        )
        symbol = DataFetcher.COMMODITIES[selected_asset]
    
    # Timeframe selection
    st.subheader("⏰ Time Settings")
    timeframe = st.selectbox(
        "Timeframe",
        ["1m", "5m", "15m", "30m", "1h", "4h", "1d"],
        index=4
    )
    
    period = st.selectbox(
        "Period",
        ["1d", "5d", "1mo", "3mo", "6mo", "1y"],
        index=3
    )
    
    st.markdown("---")
    
    # Trading settings
    st.subheader("🛡️ Risk Management")
    risk_percent = st.slider("Risk per trade (%)", 0.5, 5.0, 2.0, 0.5)
    risk_reward_ratio = st.slider("Risk/Reward Ratio", 1.0, 4.0, 2.0, 0.5)
    trailing_stop = st.slider("Trailing Stop (%)", 0.5, 5.0, 2.0, 0.5)
    
    st.markdown("---")
    
    # AI Settings
    st.subheader("🤖 AI Trading")
    use_ai = st.checkbox("Enable AI Signals", value=True)
    if use_ai:
        st.info("AI model analyzes market patterns and generates predictive signals")
    
    # Account info
    st.markdown("---")
    st.subheader("💰 Account")
    summary = st.session_state.risk_manager.get_account_summary()
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Balance", f"${summary['balance']:,.2f}")
        st.metric("Win Rate", f"{summary['win_rate']:.1f}%")
    with col2:
        st.metric("Total P&L", f"${summary['total_pnl']:,.2f}", 
                  delta=f"${summary['daily_pnl']:,.2f}")
        st.metric("Active Trades", summary['active_trades'])

# Main content area
st.title(f"📈 {selected_asset} Trading Dashboard")
st.caption(f"Real-time analysis powered by AI | Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# Fetch data
with st.spinner("Fetching market data..."):
    df = st.session_state.data_fetcher.fetch_historical_data(symbol, timeframe, period)

if df is not None and not df.empty:
    # Add technical indicators
    df = TechnicalIndicators.add_all_indicators(df)
    df = TechnicalIndicators.generate_signals(df)
    
    # AI prediction
    if use_ai:
        if not st.session_state.ai_model.is_trained:
            st.session_state.ai_model.train_model(df)
        ai_signal, ai_confidence = st.session_state.ai_model.predict_signal(df)
    else:
        ai_signal, ai_confidence = 0, 0
    
    # Display current price and metrics
    current_price = df['close'].iloc[-1]
    price_change = df['close'].iloc[-1] - df['close'].iloc[-2]
    price_change_pct = (price_change / df['close'].iloc[-2]) * 100
    
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.metric("Current Price", f"${current_price:.4f}", 
                  delta=f"{price_change_pct:.2f}%")
    with col2:
        st.metric("24h High", f"${df['high'].tail(24).max():.4f}")
    with col3:
        st.metric("24h Low", f"${df['low'].tail(24).min():.4f}")
    with col4:
        signal_color = "🟢" if df['signal'].iloc[-1] == 1 else "🔴" if df['signal'].iloc[-1] == -1 else "⚪"
        st.metric("Signal", f"{signal_color} {'BUY' if df['signal'].iloc[-1] == 1 else 'SELL' if df['signal'].iloc[-1] == -1 else 'HOLD'}")
    with col5:
        st.metric("RSI", f"{df['rsi'].iloc[-1]:.1f}")
    
    # Chart tabs
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Price Chart", "📉 Indicators", "🤖 AI Analysis", "🛡️ Risk Management"])
    
    with tab1:
        # Create candlestick chart
        fig = ChartConfig.create_candlestick_chart(df, f"{selected_asset} - {timeframe} Chart")
        st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        # Technical indicators display
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Momentum Indicators")
            st.metric("RSI (14)", f"{df['rsi'].iloc[-1]:.1f}", 
                      delta="Oversold" if df['rsi'].iloc[-1] < 30 else "Overbought" if df['rsi'].iloc[-1] > 70 else "Neutral")
            st.metric("MACD", f"{df['macd'].iloc[-1]:.4f}", 
                      delta="Bullish" if df['macd'].iloc[-1] > df['macd_signal'].iloc[-1] else "Bearish")
            st.metric("Stochastic", f"{df['stoch_k'].iloc[-1]:.1f}")
            st.metric("ADX", f"{df['adx'].iloc[-1]:.1f}")
        
        with col2:
            st.subheader("Volatility Indicators")
            st.metric("ATR", f"{df['atr'].iloc[-1]:.4f}")
            st.metric("Bollinger Width", f"{df['bb_width'].iloc[-1]:.2%}")
            st.metric("Volume Ratio", f"{df['volume_ratio'].iloc[-1]:.2f}x")
            st.metric("Volatility (20)", f"{df['returns'].tail(20).std():.2%}")
        
        # Multiple indicator chart
        selected_indicators = st.multiselect(
            "Select indicators to display",
            ['rsi', 'macd', 'stoch_k', 'adx', 'bb_width', 'volume_ratio'],
            default=['rsi', 'macd']
        )
        
        if selected_indicators:
            fig2 = ChartConfig.create_multi_indicator_chart(df, selected_indicators)
            st.plotly_chart(fig2, use_container_width=True)
    
    with tab3:
        st.subheader("🤖 AI-Powered Trading Analysis")
        
        # AI Signal Display
        if use_ai:
            col1, col2, col3 = st.columns(3)
            with col1:
                signal_text = "BUY" if ai_signal == 1 else "SELL" if ai_signal == -1 else "HOLD"
                signal_color = "green" if ai_signal == 1 else "red" if ai_signal == -1 else "gray"
                st.markdown(f"""
                <div style='text-align: center; padding: 20px; background-color: {signal_color}20; border-radius: 10px;'>
                    <h3>AI Signal</h3>
                    <h1 style='color: {signal_color};'>{signal_text}</h1>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.metric("Confidence", f"{ai_confidence}%")
            with col3:
                st.metric("Model Status", "Trained ✓" if st.session_state.ai_model.is_trained else "Training...")
            
            # Feature importance
            st.subheader("📊 Key Market Factors")
            
            # Display current technical state
            tech_state = {
                "RSI": "Oversold (Bullish)" if df['rsi'].iloc[-1] < 30 else "Overbought (Bearish)" if df['rsi'].iloc[-1] > 70 else "Neutral",
                "MACD": "Bullish Crossover" if df['macd'].iloc[-1] > df['macd_signal'].iloc[-1] and df['macd'].iloc[-2] <= df['macd_signal'].iloc[-2] else "Bearish Crossover" if df['macd'].iloc[-1] < df['macd_signal'].iloc[-1] and df['macd'].iloc[-2] >= df['macd_signal'].iloc[-2] else "No Signal",
                "Bollinger Bands": "Price Below Lower Band (Buy)" if df['close'].iloc[-1] < df['bb_lower'].iloc[-1] else "Price Above Upper Band (Sell)" if df['close'].iloc[-1] > df['bb_upper'].iloc[-1] else "Within Bands",
                "Volume": "High Volume" if df['volume_ratio'].iloc[-1] > 1.5 else "Normal Volume",
                "Trend": "Strong Trend" if df['adx'].iloc[-1] > 25 else "Weak Trend"
            }
            
            for key, value in tech_state.items():
                st.write(f"**{key}:** {value}")
        else:
            st.info("Enable AI signals in the sidebar to get AI-powered trading analysis")
        
        # Combined signal
        st.subheader("🎯 Combined Trading Signal")
        combined_score = df['combined_signal'].iloc[-1]
        
        if combined_score > 0.3:
            st.success(f"**STRONG BUY SIGNAL** - Score: {combined_score:.2f}")
            st.write("Multiple indicators suggest upward momentum")
        elif combined_score < -0.3:
            st.error(f"**STRONG SELL SIGNAL** - Score: {combined_score:.2f}")
            st.write("Multiple indicators suggest downward momentum")
        else:
            st.warning(f"**NEUTRAL/HOLD** - Score: {combined_score:.2f}")
            st.write("Wait for clearer signals before entering a trade")
    
    with tab4:
        st.subheader("🛡️ Risk Management & Anti-Loss System")
        
        # Risk status
        risk_ok, risk_message = st.session_state.risk_manager.check_risk_limits()
        
        if risk_ok:
            st.success(f"✅ {risk_message}")
        else:
            st.error(f"⚠️ {risk_message}")
        
        # Position calculator
        st.subheader("📐 Position Size Calculator")
        
        col1, col2 = st.columns(2)
        with col1:
            entry_price = st.number_input("Entry Price", value=float(current_price), format="%.4f")
            stop_loss_percent = st.number_input("Stop Loss %", value=risk_percent, min_value=0.5, max_value=5.0, step=0.5)
        
        with col2:
            account_balance = st.session_state.risk_manager.balance
            st.metric("Account Balance", f"${account_balance:,.2f}")
            
            if entry_price:
                stop_loss = entry_price * (1 - stop_loss_percent/100)
                position_size = st.session_state.risk_manager.calculate_position_size(
                    entry_price, stop_loss, risk_percent
                )
                st.metric("Recommended Position Size", f"{position_size:.4f} units")
                st.metric("Stop Loss Price", f"${stop_loss:.4f}")
                st.metric("Risk Amount", f"${account_balance * risk_percent / 100:.2f}")
        
        # Active trades
        if st.session_state.risk_manager.active_trades:
            st.subheader("📋 Active Trades")
            for trade in st.session_state.risk_manager.active_trades:
                st.write(f"**{trade['type']}** {trade['symbol']} - Entry: ${trade['entry_price']:.4f} - Size: {trade['size']:.4f}")
        else:
            st.info("No active trades")
        
        # Trade history
        if st.session_state.risk_manager.trade_history:
            st.subheader("📜 Trade History")
            history_df = pd.DataFrame(st.session_state.risk_manager.trade_history[-10:])
            st.dataframe(history_df[['symbol', 'type', 'entry_price', 'exit_price', 'pnl']], use_container_width=True)
        
        # Manual trade entry
        st.subheader("✏️ Manual Trade Entry")
        col1, col2, col3 = st.columns(3)
        with col1:
            trade_type = st.selectbox("Trade Type", ["BUY", "SELL"])
        with col2:
            trade_size = st.number_input("Position Size", min_value=0.01, value=0.01, step=0.01)
        with col3:
            if st.button("Execute Trade", type="primary"):
                trade = {
                    'id': len(st.session_state.risk_manager.trade_history) + 1,
                    'symbol': selected_asset,
                    'type': trade_type,
                    'entry_price': current_price,
                    'size': trade_size,
                    'entry_time': datetime.now()
                }
                st.session_state.risk_manager.add_trade(trade)
                st.success(f"Trade executed: {trade_type} {trade_size} units at ${current_price:.4f}")
                st.rerun()

else:
    st.error("Failed to fetch market data. Please check your internet connection and try again.")

# Footer
st.markdown("---")
st.caption("⚠️ **Disclaimer:** This dashboard is for educational purposes only. Trading involves substantial risk of loss. Always conduct your own research before trading.")
