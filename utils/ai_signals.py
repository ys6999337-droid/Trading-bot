import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
import warnings
warnings.filterwarnings('ignore')

class AITradingSignals:
    """AI-powered trading signal generation"""
    
    def __init__(self):
        self.model = RandomForestClassifier(n_estimators=100, random_state=42)
        self.scaler = StandardScaler()
        self.is_trained = False
    
    def prepare_features(self, df):
        """Prepare features for ML model"""
        if df is None or len(df) < 50:
            return None
        
        features = pd.DataFrame()
        
        # Price-based features
        features['returns_1'] = df['returns'].shift(1)
        features['returns_2'] = df['returns'].shift(2)
        features['returns_3'] = df['returns'].shift(3)
        
        # Technical indicators
        if 'rsi' in df.columns:
            features['rsi'] = df['rsi']
            features['rsi_signal'] = (df['rsi'] < 30).astype(int) - (df['rsi'] > 70).astype(int)
        
        if 'macd_diff' in df.columns:
            features['macd_diff'] = df['macd_diff']
            features['macd_cross'] = ((df['macd'] > df['macd_signal']) & (df['macd'].shift(1) <= df['macd_signal'].shift(1))).astype(int)
        
        if 'bb_width' in df.columns:
            features['bb_width'] = df['bb_width']
            features['bb_position'] = (df['close'] - df['bb_lower']) / (df['bb_upper'] - df['bb_lower'])
        
        if 'volume_ratio' in df.columns:
            features['volume_ratio'] = df['volume_ratio']
        
        # Volatility features
        features['volatility'] = df['returns'].rolling(window=20).std()
        
        # Target: Next period return
        features['target'] = (df['returns'].shift(-1) > 0).astype(int)
        
        return features.dropna()
    
    def train_model(self, df):
        """Train the ML model"""
        features = self.prepare_features(df)
        
        if features is None or len(features) < 100:
            return False
        
        X = features.drop('target', axis=1)
        y = features['target']
        
        # Scale features
        X_scaled = self.scaler.fit_transform(X)
        
        # Train model
        self.model.fit(X_scaled, y)
        self.is_trained = True
        
        return True
    
    def predict_signal(self, df):
        """Predict trading signal"""
        if not self.is_trained or df is None or len(df) < 50:
            return 0, 0
        
        features = self.prepare_features(df)
        
        if features is None:
            return 0, 0
        
        X = features.drop('target', axis=1)
        X_scaled = self.scaler.transform(X)
        
        # Get prediction probabilities
        predictions = self.model.predict(X_scaled)
        probabilities = self.model.predict_proba(X_scaled)
        
        # Latest signal
        latest_pred = predictions[-1] if len(predictions) > 0 else 0
        latest_prob = probabilities[-1][1] if len(probabilities) > 0 else 0.5
        
        # Convert to trading signal
        if latest_pred == 1 and latest_prob > 0.6:
            signal = 1  # Buy
            confidence = int(latest_prob * 100)
        elif latest_pred == 0 and latest_prob > 0.6:
            signal = -1  # Sell
            confidence = int((1 - latest_prob) * 100)
        else:
            signal = 0  # Hold
            confidence = 50
        
        return signal, confidence
