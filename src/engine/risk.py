"""
Risk Manager - Manages position sizing and risk limits
"""
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from ..utils.logger import setup_logger
from ..utils.config import get_config


logger = setup_logger(__name__)


class RiskManager:
    """Manages trading risk and position sizing"""
    
    def __init__(self, initial_capital: float = 10000):
        """
        Initialize risk manager
        
        Args:
            initial_capital: Starting portfolio value
        """
        self.config = get_config()
        self.initial_capital = initial_capital
        self.current_capital = initial_capital
        self.daily_pnl = 0.0
        self.daily_reset_time = datetime.now().date()
        self.current_positions = []
        
        # Load risk parameters
        risk_config = self.config.get('risk', {})
        self.max_risk_per_trade = risk_config.get('max_risk_per_trade_percent', 2.0) / 100
        self.daily_loss_limit = risk_config.get('daily_loss_limit_percent', 3.0) / 100
        self.max_sector_exposure = risk_config.get('max_sector_exposure', 2)
        self.min_risk_reward = risk_config.get('min_risk_reward_ratio', 2.0)
        
        signal_config = self.config.get('signals', {})
        self.max_concurrent_positions = signal_config.get('max_concurrent_positions', 5)
        
    def calculate_position_size(self, signal: Dict, confidence: int) -> Dict:
        """
        Calculate position size based on risk parameters
        
        Args:
            signal: Signal dictionary with entry and stop loss
            confidence: Confidence score (0-100)
            
        Returns:
            Dictionary with position sizing details
        """
        try:
            entry_price = signal['entry_price']
            stop_loss = signal['stop_loss']
            
            # Calculate risk per share
            risk_per_share = abs(entry_price - stop_loss)
            
            if risk_per_share == 0:
                logger.warning(f"Zero risk per share for {signal['ticker']}")
                return self._create_position_size_result(0, 0, "Zero risk")
            
            # Calculate base position size
            risk_amount = self.current_capital * self.max_risk_per_trade
            base_shares = int(risk_amount / risk_per_share)
            
            # Adjust based on confidence
            confidence_multiplier = self._get_confidence_multiplier(confidence)
            adjusted_shares = int(base_shares * confidence_multiplier)
            
            # Calculate position value
            position_value = adjusted_shares * entry_price
            
            # Check if position exceeds available capital
            max_position_value = self.current_capital * 0.25  # Max 25% per position
            if position_value > max_position_value:
                adjusted_shares = int(max_position_value / entry_price)
                position_value = adjusted_shares * entry_price
            
            # Calculate actual risk
            actual_risk = adjusted_shares * risk_per_share
            risk_percent = (actual_risk / self.current_capital) * 100
            
            return {
                'shares': adjusted_shares,
                'position_value': round(position_value, 2),
                'risk_amount': round(actual_risk, 2),
                'risk_percent': round(risk_percent, 2),
                'confidence_multiplier': confidence_multiplier,
                'approved': True,
                'reason': 'Position sized within risk limits'
            }
            
        except Exception as e:
            logger.error(f"Error calculating position size: {e}")
            return self._create_position_size_result(0, 0, f"Error: {e}")
    
    def _get_confidence_multiplier(self, confidence: int) -> float:
        """
        Get position size multiplier based on confidence
        
        Args:
            confidence: Confidence score (0-100)
            
        Returns:
            Multiplier (0.5 to 1.5)
        """
        if confidence >= 95:
            return 1.5  # 50% larger position
        elif confidence >= 90:
            return 1.25
        elif confidence >= 85:
            return 1.0  # Standard position
        elif confidence >= 80:
            return 0.75
        else:
            return 0.5  # 50% smaller position
    
    def _create_position_size_result(self, shares: int, value: float, reason: str) -> Dict:
        """Create position size result dictionary"""
        return {
            'shares': shares,
            'position_value': value,
            'risk_amount': 0,
            'risk_percent': 0,
            'confidence_multiplier': 0,
            'approved': False,
            'reason': reason
        }
    
    def check_risk_limits(self, signal: Dict) -> tuple[bool, str]:
        """
        Check if signal passes all risk limits
        
        Args:
            signal: Signal dictionary
            
        Returns:
            Tuple of (approved, reason)
        """
        # Reset daily P&L if new day
        self._check_daily_reset()
        
        # Check daily loss limit
        if not self._check_daily_loss_limit():
            return False, "Daily loss limit reached"
        
        # Check max concurrent positions
        if not self._check_max_positions():
            return False, f"Maximum {self.max_concurrent_positions} positions already open"
        
        # Check sector exposure (placeholder)
        if not self._check_sector_exposure(signal):
            return False, "Maximum sector exposure reached"
        
        # Check minimum risk/reward
        if not self._check_min_risk_reward(signal):
            return False, f"Risk/reward below minimum {self.min_risk_reward}:1"
        
        return True, "All risk checks passed"
    
    def _check_daily_reset(self):
        """Reset daily P&L if new day"""
        today = datetime.now().date()
        if today > self.daily_reset_time:
            self.daily_pnl = 0.0
            self.daily_reset_time = today
            logger.info("Daily P&L reset")
    
    def _check_daily_loss_limit(self) -> bool:
        """Check if daily loss limit has been hit"""
        daily_loss_percent = (self.daily_pnl / self.current_capital) * 100
        
        if daily_loss_percent <= -self.daily_loss_limit * 100:
            logger.warning(f"Daily loss limit reached: {daily_loss_percent:.2f}%")
            return False
        
        return True
    
    def _check_max_positions(self) -> bool:
        """Check if max concurrent positions reached"""
        return len(self.current_positions) < self.max_concurrent_positions
    
    def _check_sector_exposure(self, signal: Dict) -> bool:
        """Check sector exposure limits (placeholder)"""
        # TODO: Implement sector tracking
        return True
    
    def _check_min_risk_reward(self, signal: Dict) -> bool:
        """Check if risk/reward meets minimum"""
        try:
            entry = signal['entry_price']
            stop = signal['stop_loss']
            target = signal['take_profit_1']
            
            risk = abs(entry - stop)
            reward = abs(target - entry)
            
            if risk == 0:
                logger.warning(f"Zero risk detected for {signal.get('ticker', 'unknown')}")
                return False
            
            if reward == 0:
                logger.warning(f"Zero reward detected for {signal.get('ticker', 'unknown')}")
                return False
            
            rr_ratio = reward / risk
            return rr_ratio >= self.min_risk_reward
            
        except Exception as e:
            logger.error(f"Error checking risk/reward: {e}")
            return False
    
    def add_position(self, signal: Dict, shares: int, entry_price: float):
        """
        Add a new position to tracking
        
        Args:
            signal: Signal dictionary
            shares: Number of shares
            entry_price: Entry price
        """
        position = {
            'ticker': signal['ticker'],
            'action': signal['action'],
            'shares': shares,
            'entry_price': entry_price,
            'stop_loss': signal['stop_loss'],
            'take_profit': signal['take_profit_1'],
            'entry_time': datetime.now(),
            'strategy': signal.get('strategy', 'Unknown')
        }
        
        self.current_positions.append(position)
        logger.info(f"Added position: {signal['action']} {shares} shares of {signal['ticker']} @ ${entry_price}")
    
    def remove_position(self, ticker: str, exit_price: float) -> Optional[Dict]:
        """
        Remove a position and calculate P&L
        
        Args:
            ticker: Stock ticker
            exit_price: Exit price
            
        Returns:
            Position dictionary with P&L or None
        """
        for i, pos in enumerate(self.current_positions):
            if pos['ticker'] == ticker:
                position = self.current_positions.pop(i)
                
                # Calculate P&L
                if position['action'] == 'BUY':
                    pnl = (exit_price - position['entry_price']) * position['shares']
                else:
                    pnl = (position['entry_price'] - exit_price) * position['shares']
                
                position['exit_price'] = exit_price
                position['exit_time'] = datetime.now()
                position['pnl'] = pnl
                position['pnl_percent'] = (pnl / (position['entry_price'] * position['shares'])) * 100
                
                # Update capital and daily P&L
                self.current_capital += pnl
                self.daily_pnl += pnl
                
                logger.info(f"Closed position: {ticker} with P&L ${pnl:.2f} ({position['pnl_percent']:.2f}%)")
                
                return position
        
        logger.warning(f"Position not found: {ticker}")
        return None
    
    def get_portfolio_summary(self) -> Dict:
        """
        Get current portfolio summary
        
        Returns:
            Dictionary with portfolio metrics
        """
        total_value = self.current_capital
        
        # Add unrealized P&L from open positions (placeholder)
        # TODO: Get current prices and calculate unrealized P&L
        
        return {
            'current_capital': round(self.current_capital, 2),
            'initial_capital': self.initial_capital,
            'total_pnl': round(self.current_capital - self.initial_capital, 2),
            'total_pnl_percent': round(((self.current_capital - self.initial_capital) / self.initial_capital) * 100, 2),
            'daily_pnl': round(self.daily_pnl, 2),
            'daily_pnl_percent': round((self.daily_pnl / self.current_capital) * 100, 2),
            'open_positions': len(self.current_positions),
            'available_slots': self.max_concurrent_positions - len(self.current_positions),
            'risk_per_trade_percent': self.max_risk_per_trade * 100,
            'daily_loss_limit_percent': self.daily_loss_limit * 100
        }
    
    def update_capital(self, new_capital: float):
        """Update current capital"""
        self.current_capital = new_capital
        logger.info(f"Capital updated to ${new_capital:.2f}")
