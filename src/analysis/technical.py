"""
Technical analysis indicators
"""
import pandas as pd
import numpy as np
from typing import Dict, Optional, Tuple
from ..utils.logger import setup_logger


logger = setup_logger(__name__)


class TechnicalAnalysis:
    """Calculate technical indicators for stock data"""
    
    def __init__(self):
        """Initialize technical analysis"""
        pass
    
    def calculate_rsi(self, df: pd.DataFrame, period: int = 14) -> pd.Series:
        """
        Calculate Relative Strength Index (RSI)
        
        Args:
            df: DataFrame with 'Close' column
            period: RSI period (default 14)
            
        Returns:
            Series with RSI values
        """
        try:
            delta = df['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
            
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            
            return rsi
        except Exception as e:
            logger.error(f"Error calculating RSI: {e}")
            return pd.Series()
    
    def calculate_macd(self, df: pd.DataFrame, fast: int = 12, 
                       slow: int = 26, signal: int = 9) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """
        Calculate MACD (Moving Average Convergence Divergence)
        
        Args:
            df: DataFrame with 'Close' column
            fast: Fast EMA period (default 12)
            slow: Slow EMA period (default 26)
            signal: Signal line period (default 9)
            
        Returns:
            Tuple of (MACD line, Signal line, Histogram)
        """
        try:
            ema_fast = df['Close'].ewm(span=fast, adjust=False).mean()
            ema_slow = df['Close'].ewm(span=slow, adjust=False).mean()
            
            macd_line = ema_fast - ema_slow
            signal_line = macd_line.ewm(span=signal, adjust=False).mean()
            histogram = macd_line - signal_line
            
            return macd_line, signal_line, histogram
        except Exception as e:
            logger.error(f"Error calculating MACD: {e}")
            return pd.Series(), pd.Series(), pd.Series()
    
    def calculate_bollinger_bands(self, df: pd.DataFrame, period: int = 20, 
                                  std_dev: float = 2.0) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """
        Calculate Bollinger Bands
        
        Args:
            df: DataFrame with 'Close' column
            period: Moving average period (default 20)
            std_dev: Standard deviation multiplier (default 2.0)
            
        Returns:
            Tuple of (Upper band, Middle band, Lower band)
        """
        try:
            middle_band = df['Close'].rolling(window=period).mean()
            std = df['Close'].rolling(window=period).std()
            
            upper_band = middle_band + (std * std_dev)
            lower_band = middle_band - (std * std_dev)
            
            return upper_band, middle_band, lower_band
        except Exception as e:
            logger.error(f"Error calculating Bollinger Bands: {e}")
            return pd.Series(), pd.Series(), pd.Series()
    
    def calculate_ema(self, df: pd.DataFrame, period: int) -> pd.Series:
        """
        Calculate Exponential Moving Average (EMA)
        
        Args:
            df: DataFrame with 'Close' column
            period: EMA period
            
        Returns:
            Series with EMA values
        """
        try:
            return df['Close'].ewm(span=period, adjust=False).mean()
        except Exception as e:
            logger.error(f"Error calculating EMA: {e}")
            return pd.Series()
    
    def calculate_sma(self, df: pd.DataFrame, period: int) -> pd.Series:
        """
        Calculate Simple Moving Average (SMA)
        
        Args:
            df: DataFrame with 'Close' column
            period: SMA period
            
        Returns:
            Series with SMA values
        """
        try:
            return df['Close'].rolling(window=period).mean()
        except Exception as e:
            logger.error(f"Error calculating SMA: {e}")
            return pd.Series()
    
    def calculate_atr(self, df: pd.DataFrame, period: int = 14) -> pd.Series:
        """
        Calculate Average True Range (ATR)
        
        Args:
            df: DataFrame with 'High', 'Low', 'Close' columns
            period: ATR period (default 14)
            
        Returns:
            Series with ATR values
        """
        try:
            high_low = df['High'] - df['Low']
            high_close = np.abs(df['High'] - df['Close'].shift())
            low_close = np.abs(df['Low'] - df['Close'].shift())
            
            true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
            atr = true_range.rolling(window=period).mean()
            
            return atr
        except Exception as e:
            logger.error(f"Error calculating ATR: {e}")
            return pd.Series()
    
    def calculate_stochastic(self, df: pd.DataFrame, k_period: int = 14, 
                            d_period: int = 3) -> Tuple[pd.Series, pd.Series]:
        """
        Calculate Stochastic Oscillator
        
        Args:
            df: DataFrame with 'High', 'Low', 'Close' columns
            k_period: %K period (default 14)
            d_period: %D period (default 3)
            
        Returns:
            Tuple of (%K, %D)
        """
        try:
            lowest_low = df['Low'].rolling(window=k_period).min()
            highest_high = df['High'].rolling(window=k_period).max()
            
            k_percent = 100 * ((df['Close'] - lowest_low) / (highest_high - lowest_low))
            d_percent = k_percent.rolling(window=d_period).mean()
            
            return k_percent, d_percent
        except Exception as e:
            logger.error(f"Error calculating Stochastic: {e}")
            return pd.Series(), pd.Series()
    
    def calculate_all_indicators(self, df: pd.DataFrame) -> Dict[str, pd.Series]:
        """
        Calculate all basic indicators
        
        Args:
            df: DataFrame with OHLCV data
            
        Returns:
            Dictionary of indicator name to Series
        """
        indicators = {}
        
        try:
            # RSI
            indicators['RSI'] = self.calculate_rsi(df)
            
            # MACD
            macd, signal, hist = self.calculate_macd(df)
            indicators['MACD'] = macd
            indicators['MACD_Signal'] = signal
            indicators['MACD_Hist'] = hist
            
            # Bollinger Bands
            bb_upper, bb_middle, bb_lower = self.calculate_bollinger_bands(df)
            indicators['BB_Upper'] = bb_upper
            indicators['BB_Middle'] = bb_middle
            indicators['BB_Lower'] = bb_lower
            
            # Moving Averages
            indicators['EMA_20'] = self.calculate_ema(df, 20)
            indicators['EMA_50'] = self.calculate_ema(df, 50)
            indicators['SMA_200'] = self.calculate_sma(df, 200)
            
            # ATR
            indicators['ATR'] = self.calculate_atr(df)
            
            # Stochastic
            stoch_k, stoch_d = self.calculate_stochastic(df)
            indicators['Stoch_K'] = stoch_k
            indicators['Stoch_D'] = stoch_d
            
            logger.info(f"Calculated {len(indicators)} indicators")
            
        except Exception as e:
            logger.error(f"Error calculating indicators: {e}")
        
        return indicators
    
    def get_latest_values(self, indicators: Dict[str, pd.Series]) -> Dict[str, float]:
        """
        Get the latest value for each indicator
        
        Args:
            indicators: Dictionary of indicators
            
        Returns:
            Dictionary of indicator name to latest value
        """
        latest = {}
        for name, series in indicators.items():
            if not series.empty:
                latest[name] = float(series.iloc[-1])
        return latest
    
    def is_oversold(self, rsi: float, threshold: float = 30) -> bool:
        """Check if RSI indicates oversold condition"""
        return rsi < threshold
    
    def is_overbought(self, rsi: float, threshold: float = 70) -> bool:
        """Check if RSI indicates overbought condition"""
        return rsi > threshold
    
    def is_bullish_macd_crossover(self, macd: pd.Series, signal: pd.Series) -> bool:
        """Check if MACD has bullish crossover"""
        if len(macd) < 2 or len(signal) < 2:
            return False
        
        # Current: MACD above signal, Previous: MACD below signal
        return macd.iloc[-1] > signal.iloc[-1] and macd.iloc[-2] <= signal.iloc[-2]
    
    def is_bearish_macd_crossover(self, macd: pd.Series, signal: pd.Series) -> bool:
        """Check if MACD has bearish crossover"""
        if len(macd) < 2 or len(signal) < 2:
            return False
        
        # Current: MACD below signal, Previous: MACD above signal
        return macd.iloc[-1] < signal.iloc[-1] and macd.iloc[-2] >= signal.iloc[-2]
    
    def is_price_above_ema(self, df: pd.DataFrame, ema_period: int = 20) -> bool:
        """Check if current price is above EMA"""
        ema = self.calculate_ema(df, ema_period)
        if ema.empty:
            return False
        return df['Close'].iloc[-1] > ema.iloc[-1]
    
    def is_price_below_ema(self, df: pd.DataFrame, ema_period: int = 20) -> bool:
        """Check if current price is below EMA"""
        ema = self.calculate_ema(df, ema_period)
        if ema.empty:
            return False
        return df['Close'].iloc[-1] < ema.iloc[-1]
    
    def calculate_adx(self, df: pd.DataFrame, period: int = 14) -> pd.Series:
        """
        Calculate Average Directional Index (ADX) - trend strength
        
        Args:
            df: DataFrame with High, Low, Close
            period: ADX period
            
        Returns:
            Series with ADX values
        """
        try:
            # Calculate +DM and -DM
            high_diff = df['High'].diff()
            low_diff = -df['Low'].diff()
            
            plus_dm = high_diff.where((high_diff > low_diff) & (high_diff > 0), 0)
            minus_dm = low_diff.where((low_diff > high_diff) & (low_diff > 0), 0)
            
            # Calculate ATR
            atr = self.calculate_atr(df, period)
            
            # Calculate +DI and -DI
            plus_di = 100 * (plus_dm.rolling(window=period).mean() / atr)
            minus_di = 100 * (minus_dm.rolling(window=period).mean() / atr)
            
            # Calculate DX and ADX
            dx = 100 * np.abs(plus_di - minus_di) / (plus_di + minus_di)
            adx = dx.rolling(window=period).mean()
            
            return adx
        except Exception as e:
            logger.error(f"Error calculating ADX: {e}")
            return pd.Series()
    
    def calculate_obv(self, df: pd.DataFrame) -> pd.Series:
        """
        Calculate On-Balance Volume (OBV)
        
        Args:
            df: DataFrame with Close and Volume
            
        Returns:
            Series with OBV values
        """
        try:
            obv = (np.sign(df['Close'].diff()) * df['Volume']).fillna(0).cumsum()
            return obv
        except Exception as e:
            logger.error(f"Error calculating OBV: {e}")
            return pd.Series()
    
    def calculate_vwap(self, df: pd.DataFrame) -> pd.Series:
        """
        Calculate Volume Weighted Average Price (VWAP)
        
        Args:
            df: DataFrame with High, Low, Close, Volume
            
        Returns:
            Series with VWAP values
        """
        try:
            typical_price = (df['High'] + df['Low'] + df['Close']) / 3
            vwap = (typical_price * df['Volume']).cumsum() / df['Volume'].cumsum()
            return vwap
        except Exception as e:
            logger.error(f"Error calculating VWAP: {e}")
            return pd.Series()
    
    def detect_support_resistance(self, df: pd.DataFrame, window: int = 20) -> Tuple[float, float]:
        """
        Detect support and resistance levels
        
        Args:
            df: DataFrame with High and Low
            window: Lookback window
            
        Returns:
            Tuple of (support, resistance)
        """
        try:
            recent_data = df.tail(window)
            support = recent_data['Low'].min()
            resistance = recent_data['High'].max()
            return support, resistance
        except Exception as e:
            logger.error(f"Error detecting support/resistance: {e}")
            return 0.0, 0.0
    
    def is_bullish_trend(self, df: pd.DataFrame) -> bool:
        """Check if stock is in bullish trend (price above EMAs)"""
        try:
            ema20 = self.calculate_ema(df, 20)
            ema50 = self.calculate_ema(df, 50)
            sma200 = self.calculate_sma(df, 200)
            
            if ema20.empty or ema50.empty or sma200.empty:
                return False
            
            current_price = df['Close'].iloc[-1]
            return (current_price > ema20.iloc[-1] > ema50.iloc[-1] > sma200.iloc[-1])
        except:
            return False
    
    def is_bearish_trend(self, df: pd.DataFrame) -> bool:
        """Check if stock is in bearish trend (price below EMAs)"""
        try:
            ema20 = self.calculate_ema(df, 20)
            ema50 = self.calculate_ema(df, 50)
            sma200 = self.calculate_sma(df, 200)
            
            if ema20.empty or ema50.empty or sma200.empty:
                return False
            
            current_price = df['Close'].iloc[-1]
            return (current_price < ema20.iloc[-1] < ema50.iloc[-1] < sma200.iloc[-1])
        except:
            return False
