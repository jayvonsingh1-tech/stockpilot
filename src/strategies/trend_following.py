"""
Trend Following Strategy
"""
from typing import Dict, Optional
import pandas as pd
from ..analysis.technical import TechnicalAnalysis
from ..utils.logger import setup_logger


logger = setup_logger(__name__)


class TrendFollowingStrategy:
    """Trend following strategy - trades in direction of dominant trend"""
    
    def __init__(self):
        """Initialize trend following strategy"""
        self.ta = TechnicalAnalysis()
        self.name = "Trend Following"
        
    def analyze(self, df: pd.DataFrame, ticker: str) -> Optional[Dict]:
        """
        Analyze for trend following opportunities
        
        Args:
            df: DataFrame with OHLCV data
            ticker: Stock ticker
            
        Returns:
            Signal dictionary or None
        """
        try:
            if len(df) < 200:  # Need enough data for 200 SMA
                return None
            
            # Calculate indicators
            ema20 = self.ta.calculate_ema(df, 20)
            ema50 = self.ta.calculate_ema(df, 50)
            sma200 = self.ta.calculate_sma(df, 200)
            adx = self.ta.calculate_adx(df)
            atr = self.ta.calculate_atr(df)
            
            if ema20.empty or ema50.empty or sma200.empty or adx.empty:
                return None
            
            current_price = df['Close'].iloc[-1]
            ema20_val = ema20.iloc[-1]
            ema50_val = ema50.iloc[-1]
            sma200_val = sma200.iloc[-1]
            adx_val = adx.iloc[-1]
            atr_val = atr.iloc[-1]
            
            # Check for bullish trend
            if self._is_bullish_setup(current_price, ema20_val, ema50_val, sma200_val, adx_val):
                # Look for pullback entry
                if self._is_pullback_buy(df, ema20_val):
                    return self._create_buy_signal(
                        ticker, current_price, atr_val, ema20_val
                    )
            
            # Check for bearish trend
            elif self._is_bearish_setup(current_price, ema20_val, ema50_val, sma200_val, adx_val):
                # Look for pullback entry
                if self._is_pullback_sell(df, ema20_val):
                    return self._create_sell_signal(
                        ticker, current_price, atr_val, ema20_val
                    )
            
            return None
            
        except Exception as e:
            logger.error(f"Error in trend following analysis for {ticker}: {e}")
            return None
    
    def _is_bullish_setup(self, price: float, ema20: float, ema50: float, 
                         sma200: float, adx: float) -> bool:
        """Check if bullish trend setup exists"""
        # Price above all EMAs and strong trend
        return (price > ema20 > ema50 > sma200 and adx > 25)
    
    def _is_bearish_setup(self, price: float, ema20: float, ema50: float,
                         sma200: float, adx: float) -> bool:
        """Check if bearish trend setup exists"""
        # Price below all EMAs and strong trend
        return (price < ema20 < ema50 < sma200 and adx > 25)
    
    def _is_pullback_buy(self, df: pd.DataFrame, ema20: float) -> bool:
        """Check if price has pulled back to EMA20 for buy entry"""
        current_price = df['Close'].iloc[-1]
        prev_price = df['Close'].iloc[-2]
        
        # Price touching or just above EMA20
        distance_pct = ((current_price - ema20) / ema20) * 100
        return -1 <= distance_pct <= 2  # Within 1% below to 2% above
    
    def _is_pullback_sell(self, df: pd.DataFrame, ema20: float) -> bool:
        """Check if price has pulled back to EMA20 for sell entry"""
        current_price = df['Close'].iloc[-1]
        
        # Price touching or just below EMA20
        distance_pct = ((current_price - ema20) / ema20) * 100
        return -2 <= distance_pct <= 1  # Within 2% below to 1% above
    
    def _create_buy_signal(self, ticker: str, price: float, atr: float, 
                          ema20: float) -> Dict:
        """Create buy signal"""
        stop_loss = price - (2 * atr)  # 2 ATR stop
        take_profit_1 = price + (3 * atr)  # 3 ATR target
        take_profit_2 = price + (5 * atr)  # 5 ATR target
        take_profit_3 = price + (7 * atr)  # 7 ATR target
        
        return {
            'ticker': ticker,
            'action': 'BUY',
            'strategy': self.name,
            'entry_price': round(price, 2),
            'stop_loss': round(stop_loss, 2),
            'take_profit_1': round(take_profit_1, 2),
            'take_profit_2': round(take_profit_2, 2),
            'take_profit_3': round(take_profit_3, 2),
            'timeframe': 'Swing Trade (3-7 days)',
            'reasoning': [
                'Strong uptrend confirmed (price > EMA20 > EMA50 > SMA200)',
                'ADX shows strong trend strength',
                'Price pulled back to EMA20 support',
                'Good risk/reward setup'
            ]
        }
    
    def _create_sell_signal(self, ticker: str, price: float, atr: float,
                           ema20: float) -> Dict:
        """Create sell signal"""
        stop_loss = price + (2 * atr)  # 2 ATR stop
        take_profit_1 = price - (3 * atr)  # 3 ATR target
        take_profit_2 = price - (5 * atr)  # 5 ATR target
        take_profit_3 = price - (7 * atr)  # 7 ATR target
        
        return {
            'ticker': ticker,
            'action': 'SELL',
            'strategy': self.name,
            'entry_price': round(price, 2),
            'stop_loss': round(stop_loss, 2),
            'take_profit_1': round(take_profit_1, 2),
            'take_profit_2': round(take_profit_2, 2),
            'take_profit_3': round(take_profit_3, 2),
            'timeframe': 'Swing Trade (3-7 days)',
            'reasoning': [
                'Strong downtrend confirmed (price < EMA20 < EMA50 < SMA200)',
                'ADX shows strong trend strength',
                'Price pulled back to EMA20 resistance',
                'Good risk/reward setup'
            ]
        }
