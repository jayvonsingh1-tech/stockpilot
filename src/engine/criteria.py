"""
Criteria Checker - Validates signals against mandatory criteria
"""
from typing import Dict, List, Optional
import pandas as pd
from datetime import datetime, timedelta
from ..analysis.technical import TechnicalAnalysis
from ..utils.logger import setup_logger
from ..utils.config import get_config
from ..utils.helpers import calculate_risk_reward_ratio


logger = setup_logger(__name__)


class CriteriaChecker:
    """Validates trading signals against mandatory criteria"""
    
    def __init__(self):
        """Initialize criteria checker"""
        self.config = get_config()
        self.ta = TechnicalAnalysis()
        self.criteria_config = self.config.load_criteria()
        
    def check_all_criteria(self, signal: Dict, df: pd.DataFrame, 
                          current_positions: Optional[List[Dict]] = None) -> tuple[bool, List[str]]:
        """
        Check all mandatory criteria for a signal
        
        Args:
            signal: Signal dictionary
            df: Price data DataFrame
            current_positions: List of current open positions
            
        Returns:
            Tuple of (all_passed, failed_criteria_list)
        """
        failed = []
        
        # 1. Trend Confirmation
        if not self._check_trend_confirmation(signal, df):
            failed.append("Trend Confirmation")
        
        # 2. Volume Confirmation
        if not self._check_volume_confirmation(df):
            failed.append("Volume Confirmation")
        
        # 3. Risk/Reward Ratio
        if not self._check_risk_reward(signal):
            failed.append("Risk/Reward Ratio")
        
        # 4. RSI Confirmation
        if not self._check_rsi_confirmation(signal, df):
            failed.append("RSI Confirmation")
        
        # 5. MACD Alignment
        if not self._check_macd_alignment(signal, df):
            failed.append("MACD Alignment")
        
        # 6. Support/Resistance
        if not self._check_support_resistance(signal, df):
            failed.append("Support/Resistance")
        
        # 7. No Earnings Conflict (placeholder - needs earnings data)
        if not self._check_earnings_conflict(signal):
            failed.append("Earnings Conflict")
        
        # 8. Sector Correlation
        if not self._check_sector_correlation(signal, current_positions):
            failed.append("Sector Correlation")
        
        # 9. Confidence Score
        if not self._check_confidence_score(signal):
            failed.append("Confidence Score")
        
        # 10. Multi-Timeframe Agreement (placeholder - needs multi-TF data)
        if not self._check_multi_timeframe(signal, df):
            failed.append("Multi-Timeframe Agreement")
        
        all_passed = len(failed) == 0
        
        if not all_passed:
            logger.debug(f"Signal for {signal['ticker']} failed criteria: {', '.join(failed)}")
        
        return all_passed, failed
    
    def _check_trend_confirmation(self, signal: Dict, df: pd.DataFrame) -> bool:
        """Check if trend is confirmed by moving averages"""
        criteria = self.criteria_config.get('1_trend_confirmation', {})
        if not criteria.get('enabled', True):
            return True
        
        try:
            ema20 = self.ta.calculate_ema(df, 20)
            ema50 = self.ta.calculate_ema(df, 50)
            
            if ema20.empty or ema50.empty:
                return False
            
            current_price = df['Close'].iloc[-1]
            ema20_val = ema20.iloc[-1]
            ema50_val = ema50.iloc[-1]
            
            if signal['action'] == 'BUY':
                # For buy: price should be above EMAs or near them
                return current_price >= ema20_val * 0.98
            else:
                # For sell: price should be below EMAs or near them
                return current_price <= ema20_val * 1.02
                
        except Exception as e:
            logger.error(f"Error checking trend confirmation: {e}")
            return False
    
    def _check_volume_confirmation(self, df: pd.DataFrame) -> bool:
        """Check if volume is above average"""
        criteria = self.criteria_config.get('2_volume_confirmation', {})
        if not criteria.get('enabled', True):
            return True
        
        try:
            min_multiplier = criteria.get('min_volume_multiplier', 1.2)
            
            current_volume = df['Volume'].iloc[-1]
            avg_volume = df['Volume'].rolling(20).mean().iloc[-1]
            
            return current_volume >= avg_volume * min_multiplier
            
        except Exception as e:
            logger.error(f"Error checking volume confirmation: {e}")
            return False
    
    def _check_risk_reward(self, signal: Dict) -> bool:
        """Check if risk/reward ratio meets minimum"""
        criteria = self.criteria_config.get('3_risk_reward_ratio', {})
        if not criteria.get('enabled', True):
            return True
        
        try:
            min_ratio = criteria.get('min_ratio', 2.0)
            
            rr_ratio = calculate_risk_reward_ratio(
                signal['entry_price'],
                signal['stop_loss'],
                signal['take_profit_1']
            )
            
            return rr_ratio >= min_ratio
            
        except Exception as e:
            logger.error(f"Error checking risk/reward: {e}")
            return False
    
    def _check_rsi_confirmation(self, signal: Dict, df: pd.DataFrame) -> bool:
        """Check RSI is not overbought for buys or oversold for sells"""
        criteria = self.criteria_config.get('4_rsi_confirmation', {})
        if not criteria.get('enabled', True):
            return True
        
        try:
            rsi = self.ta.calculate_rsi(df)
            if rsi.empty:
                return False
            
            rsi_val = rsi.iloc[-1]
            
            if signal['action'] == 'BUY':
                max_rsi = criteria.get('buy_max_rsi', 70)
                return rsi_val <= max_rsi
            else:
                min_rsi = criteria.get('sell_min_rsi', 30)
                return rsi_val >= min_rsi
                
        except Exception as e:
            logger.error(f"Error checking RSI confirmation: {e}")
            return False
    
    def _check_macd_alignment(self, signal: Dict, df: pd.DataFrame) -> bool:
        """Check MACD momentum aligns with trade direction"""
        criteria = self.criteria_config.get('5_macd_alignment', {})
        if not criteria.get('enabled', True):
            return True
        
        try:
            macd, macd_signal, _ = self.ta.calculate_macd(df)
            if macd.empty or macd_signal.empty:
                return False
            
            macd_val = macd.iloc[-1]
            signal_val = macd_signal.iloc[-1]
            
            if signal['action'] == 'BUY':
                # MACD should be above signal line for buys
                return macd_val >= signal_val
            else:
                # MACD should be below signal line for sells
                return macd_val <= signal_val
                
        except Exception as e:
            logger.error(f"Error checking MACD alignment: {e}")
            return False
    
    def _check_support_resistance(self, signal: Dict, df: pd.DataFrame) -> bool:
        """Check if entry is near support (buy) or resistance (sell)"""
        criteria = self.criteria_config.get('6_support_resistance', {})
        if not criteria.get('enabled', True):
            return True
        
        try:
            proximity_pct = criteria.get('proximity_percent', 2.0) / 100
            current_price = df['Close'].iloc[-1]
            
            # Simple support/resistance using recent highs/lows
            recent_high = df['High'].tail(20).max()
            recent_low = df['Low'].tail(20).min()
            
            if signal['action'] == 'BUY':
                # Check if near support (recent low)
                distance = abs(current_price - recent_low) / recent_low
                return distance <= proximity_pct * 2  # More lenient for buys
            else:
                # Check if near resistance (recent high)
                distance = abs(current_price - recent_high) / recent_high
                return distance <= proximity_pct * 2  # More lenient for sells
                
        except Exception as e:
            logger.error(f"Error checking support/resistance: {e}")
            return True  # Don't fail on this criteria error
    
    def _check_earnings_conflict(self, signal: Dict) -> bool:
        """Check if earnings date conflicts (placeholder)"""
        criteria = self.criteria_config.get('7_no_earnings_conflict', {})
        if not criteria.get('enabled', True):
            return True
        
        # TODO: Implement earnings date checking
        # For now, pass this criteria
        return True
    
    def _check_sector_correlation(self, signal: Dict, 
                                  current_positions: Optional[List[Dict]]) -> bool:
        """Check if not overexposed to one sector"""
        criteria = self.criteria_config.get('8_sector_correlation', {})
        if not criteria.get('enabled', True):
            return True
        
        if not current_positions:
            return True
        
        try:
            max_per_sector = criteria.get('max_positions_per_sector', 2)
            
            # TODO: Get sector from signal (needs fundamental data)
            # For now, pass this criteria
            return True
            
        except Exception as e:
            logger.error(f"Error checking sector correlation: {e}")
            return True
    
    def _check_confidence_score(self, signal: Dict) -> bool:
        """Check if confidence meets minimum threshold"""
        criteria = self.criteria_config.get('9_confidence_score', {})
        if not criteria.get('enabled', True):
            return True
        
        try:
            min_confidence = criteria.get('min_confidence', 85)
            return signal.get('confidence', 0) >= min_confidence
            
        except Exception as e:
            logger.error(f"Error checking confidence score: {e}")
            return False
    
    def _check_multi_timeframe(self, signal: Dict, df: pd.DataFrame) -> bool:
        """Check if signal confirmed on multiple timeframes (placeholder)"""
        criteria = self.criteria_config.get('10_multi_timeframe', {})
        if not criteria.get('enabled', True):
            return True
        
        # TODO: Implement multi-timeframe analysis
        # For now, pass this criteria
        return True
