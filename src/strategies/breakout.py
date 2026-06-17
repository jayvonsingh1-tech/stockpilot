"""
Breakout Strategy
"""
from typing import Dict, Optional
import pandas as pd
from ..analysis.technical import TechnicalAnalysis
from ..utils.logger import setup_logger


logger = setup_logger(__name__)


class BreakoutStrategy:
    """Breakout strategy - trades breakouts from consolidation"""
    
    def __init__(self):
        """Initialize breakout strategy"""
        self.ta = TechnicalAnalysis()
        self.name = "Breakout"
        
    def analyze(self, df: pd.DataFrame, ticker: str) -> Optional[Dict]:
        """
        Analyze for breakout opportunities
        
        Args:
            df: DataFrame with OHLCV data
            ticker: Stock ticker
            
        Returns:
            Signal dictionary or None
        """
        try:
            if len(df) < 30:
                return None
            
            # Calculate indicators
            atr = self.ta.calculate_atr(df)
            volume = df['Volume']
            
            if atr.empty:
                return None
            
            current_price = df['Close'].iloc[-1]
            current_volume = volume.iloc[-1]
            avg_volume = volume.rolling(20).mean().iloc[-1]
            atr_val = atr.iloc[-1]
            
            # Check for consolidation breakout
            if self._is_bullish_breakout(df, current_volume, avg_volume):
                return self._create_buy_signal(ticker, current_price, atr_val)
            
            elif self._is_bearish_breakout(df, current_volume, avg_volume):
                return self._create_sell_signal(ticker, current_price, atr_val)
            
            return None
            
        except Exception as e:
            logger.error(f"Error in breakout analysis for {ticker}: {e}")
            return None
    
    def _is_bullish_breakout(self, df: pd.DataFrame, current_vol: float, 
                            avg_vol: float) -> bool:
        """Check if bullish breakout exists"""
        # Get recent high
        recent_high = df['High'].tail(20).max()
        current_price = df['Close'].iloc[-1]
        prev_close = df['Close'].iloc[-2]
        
        # Breakout conditions
        return (current_price > recent_high and  # Breaking above recent high
                prev_close <= recent_high and  # Previous close was below
                current_vol > avg_vol * 1.5)  # Volume surge
    
    def _is_bearish_breakout(self, df: pd.DataFrame, current_vol: float,
                             avg_vol: float) -> bool:
        """Check if bearish breakout exists"""
        # Get recent low
        recent_low = df['Low'].tail(20).min()
        current_price = df['Close'].iloc[-1]
        prev_close = df['Close'].iloc[-2]
        
        # Breakdown conditions
        return (current_price < recent_low and  # Breaking below recent low
                prev_close >= recent_low and  # Previous close was above
                current_vol > avg_vol * 1.5)  # Volume surge
    
    def _create_buy_signal(self, ticker: str, price: float, atr: float) -> Dict:
        """Create buy signal"""
        stop_loss = price - (1.5 * atr)
        take_profit_1 = price + (2 * atr)
        take_profit_2 = price + (4 * atr)
        take_profit_3 = price + (6 * atr)
        
        return {
            'ticker': ticker,
            'action': 'BUY',
            'strategy': self.name,
            'entry_price': round(price, 2),
            'stop_loss': round(stop_loss, 2),
            'take_profit_1': round(take_profit_1, 2),
            'take_profit_2': round(take_profit_2, 2),
            'take_profit_3': round(take_profit_3, 2),
            'timeframe': 'Day Trade (1-3 days)',
            'reasoning': [
                'Price breaking above recent consolidation high',
                'Volume surge confirms breakout strength',
                'Momentum trade with tight stop'
            ]
        }
    
    def _create_sell_signal(self, ticker: str, price: float, atr: float) -> Dict:
        """Create sell signal"""
        stop_loss = price + (1.5 * atr)
        take_profit_1 = price - (2 * atr)
        take_profit_2 = price - (4 * atr)
        take_profit_3 = price - (6 * atr)
        
        return {
            'ticker': ticker,
            'action': 'SELL',
            'strategy': self.name,
            'entry_price': round(price, 2),
            'stop_loss': round(stop_loss, 2),
            'take_profit_1': round(take_profit_1, 2),
            'take_profit_2': round(take_profit_2, 2),
            'take_profit_3': round(take_profit_3, 2),
            'timeframe': 'Day Trade (1-3 days)',
            'reasoning': [
                'Price breaking below recent consolidation low',
                'Volume surge confirms breakdown strength',
                'Momentum trade with tight stop'
            ]
        }
