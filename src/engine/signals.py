"""
Signal Generator - Combines strategies and generates trading signals
Enhanced with Phase 4 Learning System
"""
from typing import Dict, List, Optional
import pandas as pd
from ..data.fetcher import MarketDataFetcher
from ..analysis.technical import TechnicalAnalysis
from ..analysis.fundamental import FundamentalAnalysis
from ..strategies.trend_following import TrendFollowingStrategy
from ..strategies.mean_reversion import MeanReversionStrategy
from ..strategies.breakout import BreakoutStrategy
from ..strategies.value_investment import ValueInvestmentStrategy
from .criteria import CriteriaChecker
from .risk import RiskManager
from ..learning.performance_tracker import PerformanceTracker
from ..learning.confidence_calibrator import ConfidenceCalibrator
from ..learning.preference_learner import PreferenceLearner
from ..learning.strategy_optimizer import StrategyOptimizer
from ..utils.logger import setup_logger
from ..utils.helpers import calculate_risk_reward_ratio
from ..utils.config import get_config


logger = setup_logger(__name__)


class SignalGenerator:
    """
    Generates trading signals using multiple strategies
    Enhanced with machine learning and self-improvement
    """
    
    def __init__(self, risk_manager: Optional[RiskManager] = None, enable_learning: bool = True):
        """
        Initialize signal generator
        
        Args:
            risk_manager: Optional risk manager instance
            enable_learning: Enable learning system (default: True)
        """
        self.config = get_config()
        self.data_fetcher = MarketDataFetcher()
        self.ta = TechnicalAnalysis()
        self.fa = FundamentalAnalysis()
        self.criteria_checker = CriteriaChecker()
        self.risk_manager = risk_manager or RiskManager()
        
        # Initialize strategies (including value investment)
        self.strategies = [
            TrendFollowingStrategy(),
            MeanReversionStrategy(),
            BreakoutStrategy(),
            ValueInvestmentStrategy()
        ]
        
        self.min_confidence = self.config.get('signals.min_confidence', 80)
        
        # Phase 4: Initialize learning system
        self.enable_learning = enable_learning
        if enable_learning:
            self.performance_tracker = PerformanceTracker()
            self.confidence_calibrator = ConfidenceCalibrator()
            self.preference_learner = PreferenceLearner()
            self.strategy_optimizer = StrategyOptimizer()
            logger.info("Learning system enabled")
        else:
            logger.info("Learning system disabled")
        
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
                    
                    # Validate confidence score
                    if confidence is None or confidence < 0:
                        logger.warning(f"Invalid confidence score for {ticker}: {confidence}")
                        continue
                    
                    signal['confidence'] = confidence
                    
                    # Check if meets minimum confidence
                    if confidence >= self.min_confidence:
                        # Phase 4: Check user preferences
                        if self.enable_learning and hasattr(self, 'preference_learner'):
                            should_send, reason = self.preference_learner.should_send_signal(signal)
                            if not should_send:
                                logger.info(f"Signal for {ticker} filtered by preferences: {reason}")
                                continue
                        
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
                        
                        # Add timeframe (Phase 4A)
                        signal['timeframe'] = self._determine_timeframe(signal.get('strategy', 'Unknown'))
                        
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
        Enhanced with Phase 4 confidence calibration
        
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
            
            raw_confidence = min(confidence, 99)  # Cap at 99%
            
            # Phase 4: Apply confidence calibration
            if self.enable_learning and hasattr(self, 'confidence_calibrator'):
                strategy = signal.get('strategy', 'Unknown')
                calibrated_confidence = self.confidence_calibrator.get_calibrated_confidence(
                    strategy, raw_confidence
                )
                logger.debug(f"Confidence calibrated: {raw_confidence}% → {calibrated_confidence}%")
                return calibrated_confidence
            
            return raw_confidence
            
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
    
    def _determine_timeframe(self, strategy: str) -> str:
        """
        Determine timeframe based on strategy (Phase 4A)
        
        Args:
            strategy: Strategy name
            
        Returns:
            Timeframe string: 'day', 'swing', 'position', or 'long'
        """
        strategy_lower = strategy.lower()
        
        if 'value' in strategy_lower or 'investment' in strategy_lower:
            return 'long'
        elif 'position' in strategy_lower:
            return 'position'
        elif 'swing' in strategy_lower or 'trend' in strategy_lower or 'breakout' in strategy_lower:
            return 'swing'
        elif 'day' in strategy_lower or 'scalp' in strategy_lower or 'mean' in strategy_lower:
            return 'swing'  # Default to swing for mean reversion
        else:
            return 'swing'  # Default
    
    def learn_from_trades(self, min_trades: int = 10):
        """
        Learn from trading history and improve
        Phase 4: Machine learning integration
        
        Args:
            min_trades: Minimum trades needed for learning
        """
        if not self.enable_learning:
            logger.warning("Learning system is disabled")
            return
        
        logger.info("Starting learning process...")
        
        # Update performance metrics
        logger.info("Calculating performance metrics...")
        self.performance_tracker.calculate_daily_metrics()
        
        # Update strategy performance
        logger.info("Updating strategy performance...")
        for strategy in self.strategies:
            strategy_name = strategy.__class__.__name__
            self.performance_tracker.update_strategy_performance(strategy_name)
        
        # Calibrate confidence scores
        logger.info("Calibrating confidence scores...")
        self.confidence_calibrator.calibrate_all_strategies(min_sample_size=min_trades)
        
        # Learn user preferences
        logger.info("Learning user preferences...")
        self.preference_learner.learn_from_trades(min_trades=min_trades)
        
        logger.info("Learning complete!")
    
    def optimize_strategies(self, min_trades: int = 20):
        """
        Optimize strategy parameters
        Phase 4: Strategy optimization
        
        Args:
            min_trades: Minimum trades needed for optimization
        """
        if not self.enable_learning:
            logger.warning("Learning system is disabled")
            return
        
        logger.info("Starting strategy optimization...")
        
        for strategy in self.strategies:
            strategy_name = strategy.__class__.__name__
            
            # Check if needs reoptimization
            if self.strategy_optimizer.needs_reoptimization(strategy_name):
                logger.info(f"Optimizing {strategy_name}...")
                
                # Define parameter ranges (example)
                param_ranges = {
                    'min_confidence': range(75, 95, 5),
                    'min_risk_reward': [1.5, 2.0, 2.5, 3.0]
                }
                
                # Optimize
                result = self.strategy_optimizer.optimize_strategy(
                    strategy_name,
                    param_ranges,
                    metric='sharpe_ratio',
                    min_trades=min_trades
                )
                
                if result:
                    logger.info(f"{strategy_name} optimized: {result['parameters']}")
            else:
                logger.info(f"{strategy_name} doesn't need reoptimization yet")
        
        logger.info("Optimization complete!")
    
    def get_learning_report(self) -> Dict:
        """
        Get comprehensive learning report
        Phase 4: Learning insights
        
        Returns:
            Dictionary with learning insights
        """
        if not self.enable_learning:
            return {'error': 'Learning system is disabled'}
        
        report = {
            'performance': self.performance_tracker.get_performance_summary(),
            'preferences': self.preference_learner.get_preference_summary(),
            'calibration': {},
            'optimization': {}
        }
        
        # Get calibration report for each strategy
        for strategy in self.strategies:
            strategy_name = strategy.__class__.__name__
            report['calibration'][strategy_name] = self.confidence_calibrator.get_calibration_report(strategy_name)
            
            # Get strategy bias
            bias = self.confidence_calibrator.get_strategy_bias(strategy_name)
            report['calibration'][strategy_name]['bias'] = bias
            
            # Get optimal parameters
            optimal = self.strategy_optimizer.get_optimal_parameters(strategy_name)
            if optimal:
                report['optimization'][strategy_name] = optimal
        
        return report
    
    def auto_improve(self):
        """
        Automatically improve based on recent performance
        Phase 4: Self-improvement
        
        This runs periodically to keep the bot improving
        """
        if not self.enable_learning:
            return
        
        logger.info("=" * 60)
        logger.info("AUTO-IMPROVEMENT PROCESS")
        logger.info("=" * 60)
        
        try:
            # Learn from recent trades
            self.learn_from_trades(min_trades=10)
            
            # Optimize if enough data
            self.optimize_strategies(min_trades=20)
            
            # Update min confidence based on preferences
            preferred_conf = self.preference_learner.get_preference('preferred_confidence')
            if preferred_conf:
                new_min_conf = int(preferred_conf)
                if new_min_conf != self.min_confidence:
                    logger.info(f"Updating min confidence: {self.min_confidence}% → {new_min_conf}%")
                    self.min_confidence = new_min_conf
            
            logger.info("Auto-improvement complete!")
            
        except Exception as e:
            logger.error(f"Error in auto-improvement: {e}")
