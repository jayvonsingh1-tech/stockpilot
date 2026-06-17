"""
Signal Generator - Combines strategies and generates trading signals
"""
from typing import Dict, List, Optional
import pandas as pd
from ..data.fetcher import MarketDataFetcher
from ..analysis.technical import TechnicalAnalysis
from ..strategies.trend_following import TrendFollowingStrategy
from ..strategies.mean_reversion import MeanReversionStrategy
from ..strategies.breakout import BreakoutStrategy
from .criteria import CriteriaChecker
from .risk import RiskManager
from ..utils.logger import setup_logger
from ..utils.helpers import calculate_risk_reward_ratio
from ..utils.config import get_config


logger = setup_logger(__name__)


class SignalGenerator:
    """Generates trading signals using multiple strategies"""
    
    def __init__(self, risk_manager: Optional[RiskManager] = None):
        """Initialize signal generator"""
        self.config = get_config()
        self.data_fetcher = MarketDataFetcher()
        self.ta = TechnicalAnalysis()
        self.criteria_checker = CriteriaChecker()
        self.risk_manager = risk_manager or RiskManager()
        
        # Initialize strategies
        self.strategies = [
            TrendFollowingStrategy(),
            MeanReversionStrategy(),
            BreakoutStrategy()
        ]
        
        self.min_confidence = self.config.get('signals.min_confidence', 80)
        
    def scan_for_signals(self, tickers: List[str]) -> List[Dict]:
        """
        Scan multiple tickers for trading signals
        
        Args:
            tickers: List of stock tickers to scan
            
        Returns:
            List of signal dictionaries
        """
        signals = []
        
        for ticker in tickers:
            try:
                signal = self.generate_signal(ticker)
                if signal:
                    signals.append(signal)
            except Exception as e:
                logger.error(f"Error scanning {ticker}: {e}")
                continue
        
        return signals
    
    def generate_signal(self, ticker: str) -> Optional[Dict]:
        """
        Generate signal for a single ticker
        
        Args:
            ticker: Stock ticker
            
        Returns:
            Signal dictionary or None
        """
        try:
            # Fetch data
            df = self.data_fetcher.fetch_ohlcv(ticker, period='3mo', interval='1d')
            if df is None or len(df) < 50:
                logger.debug(f"Insufficient data for {ticker}")
                return None
            
            # Try each strategy
            for strategy in self.strategies:
                signal = strategy.analyze(df, ticker)
                if signal:
                    # Add confidence score
                    confidence = self._calculate_confidence(signal, df)
                    signal['confidence'] = confidence
                    
                    # Check if meets minimum confidence
                    if confidence >= self.min_confidence:
                        # Check risk limits
                        risk_approved, risk_reason = self.risk_manager.check_risk_limits(signal)
                        if not risk_approved:
                            logger.info(f"Signal for {ticker} rejected by risk manager: {risk_reason}")
                            continue
                        
                        # Check mandatory criteria
                        criteria_passed, failed_criteria = self.criteria_checker.check_all_criteria(
                            signal, df, self.risk_manager.current_positions
                        )
                        
                        if not criteria_passed:
                            logger.info(f"Signal for {ticker} failed criteria: {', '.join(failed_criteria)}")
                            continue
                        
                        # Calculate position size
                        position_size = self.risk_manager.calculate_position_size(signal, confidence)
                        signal['position_size'] = position_size
                        
                        # Add additional info
                        signal = self._enrich_signal(signal, df)
                        logger.info(f"✓ Signal generated for {ticker}: {signal['action']} at {confidence}% confidence")
                        return signal
            
            return None
            
        except Exception as e:
            logger.error(f"Error generating signal for {ticker}: {e}")
            return None
    
    def _calculate_confidence(self, signal: Dict, df: pd.DataFrame) -> int:
        """
        Calculate confidence score for a signal
        
        Args:
            signal: Signal dictionary
            df: Price data
            
        Returns:
            Confidence score (0-100)
        """
        try:
            confidence = 70  # Base confidence
            
            # Calculate indicators
            rsi = self.ta.calculate_rsi(df)
            macd, macd_signal, _ = self.ta.calculate_macd(df)
            adx = self.ta.calculate_adx(df)
            
            if rsi.empty or macd.empty or adx.empty:
                return confidence
            
            rsi_val = rsi.iloc[-1]
            adx_val = adx.iloc[-1]
            
            # Bonus for strong trend
            if adx_val > 30:
                confidence += 10
            elif adx_val > 25:
                confidence += 5
            
            # Bonus for RSI confirmation
            if signal['action'] == 'BUY' and 30 < rsi_val < 50:
                confidence += 10
            elif signal['action'] == 'SELL' and 50 < rsi_val < 70:
                confidence += 10
            
            # Bonus for MACD confirmation
            if signal['action'] == 'BUY' and macd.iloc[-1] > macd_signal.iloc[-1]:
                confidence += 5
            elif signal['action'] == 'SELL' and macd.iloc[-1] < macd_signal.iloc[-1]:
                confidence += 5
            
            # Bonus for good risk/reward
            risk_reward = calculate_risk_reward_ratio(
                signal['entry_price'],
                signal['stop_loss'],
                signal['take_profit_1']
            )
            if risk_reward >= 3:
                confidence += 10
            elif risk_reward >= 2:
                confidence += 5
            
            return min(confidence, 99)  # Cap at 99%
            
        except Exception as e:
            logger.error(f"Error calculating confidence: {e}")
            return 70
    
    def _enrich_signal(self, signal: Dict, df: pd.DataFrame) -> Dict:
        """
        Add additional information to signal
        
        Args:
            signal: Signal dictionary
            df: Price data
            
        Returns:
            Enriched signal dictionary
        """
        try:
            # Calculate percentages
            entry = signal['entry_price']
            stop = signal['stop_loss']
            tp1 = signal['take_profit_1']
            tp2 = signal.get('take_profit_2', tp1)
            tp3 = signal.get('take_profit_3', tp1)
            
            signal['stop_loss_percent'] = round(((stop - entry) / entry) * 100, 1)
            signal['tp1_percent'] = round(((tp1 - entry) / entry) * 100, 1)
            signal['tp2_percent'] = round(((tp2 - entry) / entry) * 100, 1)
            signal['tp3_percent'] = round(((tp3 - entry) / entry) * 100, 1)
            
            # Calculate risk/reward
            signal['risk_reward'] = round(calculate_risk_reward_ratio(entry, stop, tp1), 1)
            
            # Add order type
            signal['order_type'] = 'Limit Order'
            
            # Add market
            ticker = signal['ticker']
            signal['market'] = 'LSE' if ticker.endswith('.L') else 'NASDAQ'
            
            # Get stock info
            info = self.data_fetcher.get_stock_info(signal['ticker'])
            if info:
                signal['name'] = info.get('name', signal['ticker'])
            else:
                signal['name'] = signal['ticker']
            
            # Format reasoning as string
            if isinstance(signal.get('reasoning'), list):
                signal['reasoning'] = '\n• '.join([''] + signal['reasoning'])
            
            return signal
            
        except Exception as e:
            logger.error(f"Error enriching signal: {e}")
            return signal
