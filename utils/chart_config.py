import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd

class ChartConfig:
    """TradingView-style chart configuration"""
    
    @staticmethod
    def create_candlestick_chart(df, title="Price Chart"):
        """Create interactive candlestick chart"""
        if df is None or df.empty:
            return go.Figure()
        
        fig = make_subplots(
            rows=3, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.05,
            row_heights=[0.6, 0.2, 0.2],
            subplot_titles=(title, "RSI", "Volume")
        )
        
        # Candlestick chart
        fig.add_trace(
            go.Candlestick(
                x=df.index,
                open=df['open'],
                high=df['high'],
                low=df['low'],
                close=df['close'],
                name="Price",
                showlegend=False
            ),
            row=1, col=1
        )
        
        # Add moving averages
        if 'sma_20' in df.columns:
            fig.add_trace(
                go.Scatter(x=df.index, y=df['sma_20'], name="SMA 20",
                          line=dict(color='orange', width=1)),
                row=1, col=1
            )
        
        if 'sma_50' in df.columns:
            fig.add_trace(
                go.Scatter(x=df.index, y=df['sma_50'], name="SMA 50",
                          line=dict(color='blue', width=1)),
                row=1, col=1
            )
        
        # Add Bollinger Bands
        if 'bb_upper' in df.columns and 'bb_lower' in df.columns:
            fig.add_trace(
                go.Scatter(x=df.index, y=df['bb_upper'], name="BB Upper",
                          line=dict(color='gray', width=1, dash='dash')),
                row=1, col=1
            )
            fig.add_trace(
                go.Scatter(x=df.index, y=df['bb_lower'], name="BB Lower",
                          line=dict(color='gray', width=1, dash='dash')),
                row=1, col=1
            )
        
        # RSI
        if 'rsi' in df.columns:
            fig.add_trace(
                go.Scatter(x=df.index, y=df['rsi'], name="RSI",
                          line=dict(color='purple', width=1)),
                row=2, col=1
            )
            fig.add_hline(y=70, line_dash="dash", line_color="red", row=2, col=1)
            fig.add_hline(y=30, line_dash="dash", line_color="green", row=2, col=1)
        
        # Volume
        colors = ['red' if close < open else 'green' for close, open in zip(df['close'], df['open'])]
        fig.add_trace(
            go.Bar(x=df.index, y=df['volume'], name="Volume",
                  marker_color=colors, showlegend=False),
            row=3, col=1
        )
        
        # Update layout
        fig.update_layout(
            template="plotly_dark",
            height=800,
            xaxis_rangeslider_visible=False,
            hovermode='x unified'
        )
        
        fig.update_xaxes(title_text="Date", row=3, col=1)
        fig.update_yaxes(title_text="Price", row=1, col=1)
        fig.update_yaxes(title_text="RSI", row=2, col=1)
        fig.update_yaxes(title_text="Volume", row=3, col=1)
        
        return fig
    
    @staticmethod
    def create_multi_indicator_chart(df, indicators):
        """Create chart with multiple indicators"""
        if df is None or df.empty:
            return go.Figure()
        
        fig = make_subplots(
            rows=len(indicators) + 1, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.03,
            subplot_titles=["Price"] + [ind.upper() for ind in indicators]
        )
        
        # Price chart
        fig.add_trace(
            go.Scatter(x=df.index, y=df['close'], name="Close",
                      line=dict(color='white', width=1)),
            row=1, col=1
        )
        
        # Add indicators
        for i, indicator in enumerate(indicators, start=2):
            if indicator in df.columns:
                fig.add_trace(
                    go.Scatter(x=df.index, y=df[indicator], name=indicator.upper(),
                              line=dict(width=1)),
                    row=i, col=1
                )
        
        fig.update_layout(template="plotly_dark", height=600, showlegend=False)
        
        return fig
