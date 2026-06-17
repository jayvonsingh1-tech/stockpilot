"""
Mean Reversion Strategy
"""
from typing import Dict, Optional
import pandas as pd
from ..analysis.technical import TechnicalAnalysis
from ..utils.logger import setup_logger


logger = setup_logger(__name__)


class MeanReversionStrategy:
    """Mean reversion strategy - trades when price deviates from mean"""
    
    def __init__(self):
        """Initialize mean reversion strategy"""
        self.ta = TechnicalAnalysis()
        self.name = "Mean Reversion"
        
    def analyze(self, df: pd.DataFrame, ticker: str) -> Optional[Dict]:
        """
        Analyze for mean reversion opportunities
        
        Args:
            df: DataFrame with OHLCV data
            ticker: Stock ticker
            
        Returns:
            Signal dictionary or None
        """
        try:
            if len(df) < 50:
                return None
            
            # Calculate indicators
            bb_upper, bb_middle, bb_lower = self.ta.calculate_bollinger_bands(df)
            rsi = self.ta.calculate_rsi(df)
            ema50 = self.ta.calculate_ema(df, 50)
            atr = self.ta.calculate_atr(df)
            
            if bb_upper.empty or rsi.empty or ema50.empty:
                return None
            
            current_price = df['Close'].iloc[-1]
            bb_upper_val = bb_upper.iloc[-1]
            bb_middle_val = bb_middle.iloc[-1]
            bb_lower_val = bb_lower.iloc[-1]
            rsi_val = rsi.iloc[-1]
            ema50_val = ema50.iloc[-1]
            atr_val = atr.iloc[-1]
            
            # Check for oversold in uptrend (buy)
            if self._is_oversold_in_uptrend(current_price, bb_lower_val, rsi_val, ema50_val):
                return self._create_buy_signal(
                    ticker, current_price, atr_val, bb_middle_val
                )
            
            # Check for overbought in downtrend (sell)
            elif self._is_overbought_in_downtrend(current_price, bb_upper_val, rsi_val, ema50_val):
                return self._create_sell_signal(
                    ticker, current_price, atr_val, bb_middle_val
                )
            
            return None
            
        except Exception as e:
            logger.error(f"Error in mean reversion analysis for {ticker}: {e}")
            return None
    
    def _is_oversold_in_uptrend(self, price: float, bb_lower: float, 
                                rsi: float, ema50: float) -> bool:
        """Check if oversold in uptrend"""
        # Price near lower BB, RSI oversold, but overall uptrend
        return (price <= bb_lower * 1.02 and  # Within 2% of lower BB
                rsi < 35 and  # Oversold
                price > ema50 * 0.95)  # Still in uptrend (within 5% of EMA50)
    
    def _is_overbought_in_downtrend(self, price: float, bb_upper: float,
                                    rsi: float, ema50: float) -> bool:
        """Check if overbought in downtrend"""
        # Price near upper BB, RSI overbought, but overall downtrend
        return (price >= bb_upper * 0.98 and  # Within 2% of upper BB
                rsi > 65 and  # Overbought
                price < ema50 * 1.05)  # Still in downtrend
    
    def _create_buy_signal(self, ticker: str, price: float, atr: float,
                          bb_middle: float) -> Dict:
        """Create buy signal"""
        stop_loss = price - (1.5 * atr)  # Tight stop for mean reversion
        take_profit_1 = bb_middle  # Target middle BB
        take_profit_2 = price + (2 * atr)
        take_profit_3 = price + (3 * atr)
        
        return {
            'ticker': ticker,
            'action': 'BUY',
            'strategy': self.name,
            'entry_price': round(price, 2),
            'stop_loss': round(stop_loss, 2),
            'take_profit_1': round(take_profit_1, 2),
            'take_profit_2': round(take_profit_2, 2),
            'take_profit_3': round(take_profit_3, 2),
            'timeframe': 'Swing Trade (2-5 days)',
            'reasoning': [
                'Price at lower Bollinger Band (oversold)',
                'RSI shows oversold condition',
                'Overall trend still bullish (above EMA50)',
                'Mean reversion expected back to middle BB'
            ]
        }
    
    def _create_sell_signal(self, ticker: str, price: float, atr: float,
                           bb_middle: float) -> Dict:
        """Create sell signal"""
        stop_loss = price + (1.5 * atr)
        take_profit_1 = bb_middle  # Target middle BB
        take_profit_2 = price - (2 * atr)
        take_profit_3 = price - (3 * atr)
        
        return {
            'ticker': ticker,
            'action': 'SELL',
            'strategy': self.name,
            'entry_price': round(price, 2),
            'stop_loss': round(stop_loss, 2),
            'take_profit_1': round(take_profit_1, 2),
            'take_profit_2': round(take_profit_2, 2),
            'take_profit_3': round(take_profit_3, 2),
            'timeframe': 'Swing Trade (2-5 days)',
            'reasoning': [
                'Price at upper Bollinger Band (overbought)',
                'RSI shows overbought condition',
                'Overall trend still bearish (below EMA50)',
                'Mean reversion expected back to middle BB'
            ]
        }
