import pandas as pd
import numpy as np
from datetime import datetime

class RiskManager:
    """Anti-loss and risk management system"""
    
    def __init__(self):
        self.active_trades = []
        self.trade_history = []
        self.balance = 10000  # Starting balance
        self.max_daily_loss = 500  # Maximum daily loss
        self.max_consecutive_losses = 3
        self.consecutive_losses = 0
        self.daily_pnl = 0
        self.last_reset_date = datetime.now().date()
    
    def reset_daily(self):
        """Reset daily loss tracking"""
        today = datetime.now().date()
        if today != self.last_reset_date:
            self.daily_pnl = 0
            self.consecutive_losses = 0
            self.last_reset_date = today
    
    def check_risk_limits(self):
        """Check if risk limits are breached"""
        self.reset_daily()
        
        if self.daily_pnl <= -self.max_daily_loss:
            return False, f"Daily loss limit reached: ${abs(self.daily_pnl)}"
        
        if self.consecutive_losses >= self.max_consecutive_losses:
            return False, f"Max consecutive losses reached: {self.consecutive_losses}"
        
        return True, "Risk limits OK"
    
    def calculate_stop_loss(self, entry_price, position_type, risk_percent=2):
        """Calculate stop loss price"""
        atr = self._calculate_atr()
        risk_amount = self.balance * (risk_percent / 100)
        
        if position_type == "BUY":
            stop_loss = entry_price - (atr * 1.5)
        else:
            stop_loss = entry_price + (atr * 1.5)
        
        return max(stop_loss, entry_price * 0.95)  # Max 5% loss
    
    def calculate_take_profit(self, entry_price, position_type, risk_reward_ratio=2):
        """Calculate take profit price"""
        atr = self._calculate_atr()
        
        if position_type == "BUY":
            take_profit = entry_price + (atr * (1.5 * risk_reward_ratio))
        else:
            take_profit = entry_price - (atr * (1.5 * risk_reward_ratio))
        
        return take_profit
    
    def calculate_position_size(self, entry_price, stop_loss, risk_percent=2):
        """Calculate optimal position size"""
        risk_amount = self.balance * (risk_percent / 100)
        risk_per_unit = abs(entry_price - stop_loss)
        
        if risk_per_unit > 0:
            position_size = risk_amount / risk_per_unit
            return min(position_size, self.balance / entry_price)  # Max 100% of balance
        return 0
    
    def _calculate_atr(self, period=14):
        """Calculate ATR for volatility-based stops"""
        # Simplified ATR calculation
        return 0.01  # Default 1% for forex
    
    def add_trade(self, trade):
        """Add a new trade to active trades"""
        self.active_trades.append(trade)
    
    def close_trade(self, trade_id, exit_price):
        """Close a trade and record P&L"""
        for trade in self.active_trades:
            if trade['id'] == trade_id:
                if trade['type'] == "BUY":
                    pnl = (exit_price - trade['entry_price']) * trade['size']
                else:
                    pnl = (trade['entry_price'] - exit_price) * trade['size']
                
                trade['exit_price'] = exit_price
                trade['pnl'] = pnl
                trade['exit_time'] = datetime.now()
                
                self.trade_history.append(trade)
                self.active_trades.remove(trade)
                
                self.balance += pnl
                self.daily_pnl += pnl
                
                if pnl < 0:
                    self.consecutive_losses += 1
                else:
                    self.consecutive_losses = 0
                
                return pnl
        return None
    
    def get_trailing_stop(self, current_price, entry_price, highest_price, trail_percent=2):
        """Calculate trailing stop loss"""
        if current_price > highest_price:
            highest_price = current_price
        
        if entry_price is not None:
            trailing_stop = highest_price * (1 - trail_percent / 100)
            return trailing_stop, highest_price
        
        return None, highest_price
    
    def get_account_summary(self):
        """Get account summary metrics"""
        total_trades = len(self.trade_history)
        winning_trades = len([t for t in self.trade_history if t.get('pnl', 0) > 0])
        losing_trades = len([t for t in self.trade_history if t.get('pnl', 0) < 0])
        
        win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
        
        total_pnl = sum([t.get('pnl', 0) for t in self.trade_history])
        
        return {
            'balance': self.balance,
            'total_pnl': total_pnl,
            'total_trades': total_trades,
            'winning_trades': winning_trades,
            'losing_trades': losing_trades,
            'win_rate': win_rate,
            'active_trades': len(self.active_trades),
            'daily_pnl': self.daily_pnl,
            'consecutive_losses': self.consecutive_losses
        }
