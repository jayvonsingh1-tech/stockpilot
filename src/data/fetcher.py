"""
Market data fetcher using yfinance
"""
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import time
from ..utils.logger import setup_logger
from ..utils.helpers import get_market_for_ticker


logger = setup_logger(__name__)


class MarketDataFetcher:
    """Fetches market data from yfinance"""
    
    def __init__(self):
        """Initialize the market data fetcher"""
        self.cache = {}
        self.cache_duration = 60  # Cache data for 60 seconds
        
    def fetch_ohlcv(self, ticker: str, period: str = "1d", 
                     interval: str = "1h") -> Optional[pd.DataFrame]:
        """
        Fetch OHLCV (Open, High, Low, Close, Volume) data
        
        Args:
            ticker: Stock ticker symbol
            period: Data period (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)
            interval: Data interval (1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo)
            
        Returns:
            DataFrame with OHLCV data or None if error
        """
        cache_key = f"{ticker}_{period}_{interval}"
        
        # Check cache
        if cache_key in self.cache:
            cached_data, cached_time = self.cache[cache_key]
            if time.time() - cached_time < self.cache_duration:
                logger.debug(f"Using cached data for {ticker}")
                return cached_data
        
        try:
            logger.info(f"Fetching data for {ticker} (period={period}, interval={interval})")
            stock = yf.Ticker(ticker)
            df = stock.history(period=period, interval=interval)
            
            if df.empty:
                logger.warning(f"No data returned for {ticker}")
                return None
            
            # Cache the data
            self.cache[cache_key] = (df, time.time())
            
            logger.info(f"Successfully fetched {len(df)} candles for {ticker}")
            return df
            
        except Exception as e:
            logger.error(f"Error fetching data for {ticker}: {e}")
            return None
    
    def fetch_multiple_timeframes(self, ticker: str, 
                                  timeframes: List[str] = None) -> Dict[str, pd.DataFrame]:
        """
        Fetch data for multiple timeframes
        
        Args:
            ticker: Stock ticker symbol
            timeframes: List of timeframe strings (e.g., ['1h', '1d'])
            
        Returns:
            Dictionary mapping timeframe to DataFrame
        """
        if timeframes is None:
            timeframes = ['1h', '1d']
        
        data = {}
        for tf in timeframes:
            # Map timeframe to period and interval
            period, interval = self._map_timeframe(tf)
            df = self.fetch_ohlcv(ticker, period=period, interval=interval)
            if df is not None:
                data[tf] = df
        
        return data
    
    def _map_timeframe(self, timeframe: str) -> Tuple[str, str]:
        """
        Map timeframe string to period and interval
        
        Args:
            timeframe: Timeframe string (e.g., '1h', '1d')
            
        Returns:
            Tuple of (period, interval)
        """
        mapping = {
            '1min': ('1d', '1m'),
            '5min': ('5d', '5m'),
            '15min': ('5d', '15m'),
            '1h': ('1mo', '1h'),
            '1d': ('1y', '1d'),
            '1wk': ('5y', '1wk'),
        }
        
        return mapping.get(timeframe, ('1mo', '1h'))
    
    def get_current_price(self, ticker: str) -> Optional[float]:
        """
        Get current price for a ticker
        
        Args:
            ticker: Stock ticker symbol
            
        Returns:
            Current price or None if error
        """
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            
            # Try different price fields
            price = info.get('currentPrice') or info.get('regularMarketPrice')
            
            if price:
                logger.debug(f"Current price for {ticker}: {price}")
                return float(price)
            
            # Fallback: get latest close from history
            df = self.fetch_ohlcv(ticker, period='1d', interval='1m')
            if df is not None and not df.empty:
                return float(df['Close'].iloc[-1])
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting current price for {ticker}: {e}")
            return None
    
    def get_stock_info(self, ticker: str) -> Optional[Dict]:
        """
        Get stock information (company name, sector, etc.)
        
        Args:
            ticker: Stock ticker symbol
            
        Returns:
            Dictionary with stock info or None if error
        """
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            
            return {
                'ticker': ticker,
                'name': info.get('longName', ticker),
                'sector': info.get('sector', 'Unknown'),
                'industry': info.get('industry', 'Unknown'),
                'market_cap': info.get('marketCap', 0),
                'currency': info.get('currency', 'USD'),
                'exchange': info.get('exchange', 'Unknown'),
            }
            
        except Exception as e:
            logger.error(f"Error getting info for {ticker}: {e}")
            return None
    
    def get_volume_average(self, ticker: str, days: int = 20) -> Optional[float]:
        """
        Get average volume over specified days
        
        Args:
            ticker: Stock ticker symbol
            days: Number of days for average
            
        Returns:
            Average volume or None if error
        """
        try:
            df = self.fetch_ohlcv(ticker, period=f"{days}d", interval='1d')
            if df is not None and not df.empty:
                return float(df['Volume'].mean())
            return None
        except Exception as e:
            logger.error(f"Error calculating average volume for {ticker}: {e}")
            return None
    
    def is_data_available(self, ticker: str) -> bool:
        """
        Check if data is available for a ticker
        
        Args:
            ticker: Stock ticker symbol
            
        Returns:
            True if data available, False otherwise
        """
        df = self.fetch_ohlcv(ticker, period='1d', interval='1h')
        return df is not None and not df.empty
    
    def clear_cache(self):
        """Clear the data cache"""
        self.cache.clear()
        logger.info("Data cache cleared")
