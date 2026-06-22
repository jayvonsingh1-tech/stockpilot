"""
Context Builder for Conversational AI
Gathers all relevant trading data for AI conversations
Phase 5 Feature
"""
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from ..engine.trade_database import TradeDatabase
from ..engine.trade_database_v2 import TradeDatabaseV2
from ..learning.performance_tracker import PerformanceTracker
from ..learning.preference_learner import PreferenceLearner
from ..data.fetcher import MarketDataFetcher
from ..utils.logger import setup_logger

logger = setup_logger(__name__)


class ContextBuilder:
    """Build comprehensive trading context for AI conversations"""
    
    def __init__(self):
        """Initialize context builder with database connections"""
        self.db = TradeDatabase()
        self.db_v2 = TradeDatabaseV2()
        self.performance_tracker = PerformanceTracker()
        self.preference_learner = PreferenceLearner()
        self.fetcher = MarketDataFetcher()
    
    def build_context(self, user_message: str = "") -> Dict:
        """
        Build comprehensive context for AI conversation
        
        Args:
            user_message: User's message (can help determine what context to include)
            
        Returns:
            Dictionary with all relevant trading data
        """
        try:
            context = {
                'portfolio': self._get_portfolio_context(),
                'recent_trades': self._get_recent_trades_context(),
                'performance': self._get_performance_context(),
                'strategies': self._get_strategy_context(),
                'preferences': self._get_preferences_context(),
                'market': self._get_market_context(user_message)
            }
            
            logger.info("Context built successfully for AI conversation")
            return context
            
        except Exception as e:
            logger.error(f"Error building context: {e}")
            return {}
    
    def _get_portfolio_context(self) -> Dict:
        """Get current portfolio status"""
        try:
            open_trades = self.db.get_open_trades()
            
            total_value = 0
            total_investment = 0
            unrealized_pnl = 0
            
            for trade in open_trades:
                # Get current price
                current_price = self.fetcher.get_current_price(trade['ticker'])
                if current_price:
                    shares = trade.get('shares', 0)
                    entry_price = trade.get('entry_price', 0)
                    
                    current_value = current_price * shares
                    investment = entry_price * shares
                    
                    total_value += current_value
                    total_investment += investment
                    
                    if trade['action'] == 'BUY':
                        unrealized_pnl += (current_price - entry_price) * shares
                    else:
                        unrealized_pnl += (entry_price - current_price) * shares
            
            unrealized_pnl_percent = (unrealized_pnl / total_investment * 100) if total_investment > 0 else 0
            
            return {
                'open_trades': len(open_trades),
                'total_value': total_value,
                'total_investment': total_investment,
                'unrealized_pnl': unrealized_pnl,
                'unrealized_pnl_percent': unrealized_pnl_percent,
                'positions': [
                    {
                        'ticker': trade['ticker'],
                        'shares': trade.get('shares', 0),
                        'entry_price': trade.get('entry_price', 0),
                        'current_price': self.fetcher.get_current_price(trade['ticker']),
                        'days_held': trade.get('days_held', 0)
                    }
                    for trade in open_trades[:10]  # Top 10 positions
                ]
            }
            
        except Exception as e:
            logger.error(f"Error getting portfolio context: {e}")
            return {}
    
    def _get_recent_trades_context(self, limit: int = 10) -> List[Dict]:
        """Get recent closed trades"""
        try:
            # Get all trades and filter closed ones
            all_trades = self.db.get_all_trades()
            closed_trades = [t for t in all_trades if t.get('status') == 'CLOSED']
            
            # Sort by date (most recent first)
            closed_trades.sort(key=lambda x: x.get('exit_date', ''), reverse=True)
            
            recent = []
            for trade in closed_trades[:limit]:
                entry_price = trade.get('entry_price', 0)
                exit_price = trade.get('exit_price', 0)
                shares = trade.get('shares', 0)
                
                if trade['action'] == 'BUY':
                    pnl = (exit_price - entry_price) * shares
                else:
                    pnl = (entry_price - exit_price) * shares
                
                pnl_percent = (pnl / (entry_price * shares) * 100) if entry_price > 0 and shares > 0 else 0
                
                recent.append({
                    'ticker': trade.get('ticker', 'N/A'),
                    'action': trade.get('action', 'N/A'),
                    'entry_price': entry_price,
                    'exit_price': exit_price,
                    'pnl': pnl,
                    'pnl_percent': pnl_percent,
                    'strategy': trade.get('strategy', 'N/A'),
                    'exit_reason': trade.get('exit_reason', 'N/A'),
                    'days_held': trade.get('days_held', 0)
                })
            
            return recent
            
        except Exception as e:
            logger.error(f"Error getting recent trades context: {e}")
            return []
    
    def _get_performance_context(self) -> Dict:
        """Get overall performance metrics"""
        try:
            stats = self.db.get_performance_stats()
            
            # Get recent performance (last 30 days)
            try:
                recent_metrics = self.performance_tracker.get_performance_summary(days=30)
            except:
                recent_metrics = {}
            
            return {
                'total_trades': stats.get('total_trades', 0),
                'winning_trades': stats.get('winning_trades', 0),
                'losing_trades': stats.get('losing_trades', 0),
                'win_rate': stats.get('win_rate', 0),
                'total_pnl': stats.get('total_pnl', 0),
                'avg_profit': stats.get('avg_profit', 0),
                'avg_loss': stats.get('avg_loss', 0),
                'best_trade': stats.get('best_trade', 0),
                'worst_trade': stats.get('worst_trade', 0),
                'profit_factor': stats.get('profit_factor', 0),
                'avg_hold_days': stats.get('avg_hold_days', 0),
                'recent_30d': recent_metrics
            }
            
        except Exception as e:
            logger.error(f"Error getting performance context: {e}")
            return {}
    
    def _get_strategy_context(self) -> Dict:
        """Get strategy-specific performance"""
        try:
            strategies = {}
            
            # Get all trades
            all_trades = self.db.get_all_trades()
            
            # Group by strategy
            for trade in all_trades:
                if trade.get('status') != 'CLOSED':
                    continue
                
                strategy = trade.get('strategy', 'Unknown')
                if strategy not in strategies:
                    strategies[strategy] = {
                        'trades': 0,
                        'wins': 0,
                        'losses': 0,
                        'total_pnl': 0
                    }
                
                strategies[strategy]['trades'] += 1
                
                # Calculate P&L
                entry_price = trade.get('entry_price', 0)
                exit_price = trade.get('exit_price', 0)
                shares = trade.get('shares', 0)
                
                if trade['action'] == 'BUY':
                    pnl = (exit_price - entry_price) * shares
                else:
                    pnl = (entry_price - exit_price) * shares
                
                strategies[strategy]['total_pnl'] += pnl
                
                if pnl > 0:
                    strategies[strategy]['wins'] += 1
                else:
                    strategies[strategy]['losses'] += 1
            
            # Calculate win rates
            for strategy in strategies:
                total = strategies[strategy]['trades']
                if total > 0:
                    strategies[strategy]['win_rate'] = (strategies[strategy]['wins'] / total) * 100
                else:
                    strategies[strategy]['win_rate'] = 0
            
            return strategies
            
        except Exception as e:
            logger.error(f"Error getting strategy context: {e}")
            return {}
    
    def _get_preferences_context(self) -> Dict:
        """Get user's learned preferences"""
        try:
            # Try to get preferences from preference learner
            try:
                prefs = self.preference_learner.get_preference_summary()
                return prefs
            except:
                pass
            
            # Fallback: analyze from trades
            all_trades = self.db.get_all_trades()
            
            if not all_trades:
                return {}
            
            # Count strategy usage
            strategy_counts = {}
            for trade in all_trades:
                strategy = trade.get('strategy', 'Unknown')
                strategy_counts[strategy] = strategy_counts.get(strategy, 0) + 1
            
            # Find favorite
            favorite_strategy = max(strategy_counts, key=strategy_counts.get) if strategy_counts else None
            
            # Calculate average confidence of taken trades
            confidences = [t.get('confidence', 0) for t in all_trades if t.get('confidence')]
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0
            
            return {
                'favorite_strategy': favorite_strategy,
                'min_confidence': int(avg_confidence * 0.9) if avg_confidence > 0 else 80,
                'total_trades_taken': len(all_trades),
                'strategy_distribution': strategy_counts
            }
            
        except Exception as e:
            logger.error(f"Error getting preferences context: {e}")
            return {}
    
    def _get_market_context(self, user_message: str) -> Dict:
        """Get market data if ticker mentioned in message"""
        try:
            # Extract ticker from message
            import re
            ticker_match = re.search(r'\b([A-Z]{1,5})\b', user_message.upper())
            
            if not ticker_match:
                return {}
            
            ticker = ticker_match.group(1)
            
            # Get current price
            current_price = self.fetcher.get_current_price(ticker)
            
            if not current_price:
                return {}
            
            return {
                'ticker': ticker,
                'current_price': current_price,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting market context: {e}")
            return {}


def create_context_builder() -> ContextBuilder:
    """
    Create a context builder instance
    
    Returns:
        ContextBuilder instance
    """
    return ContextBuilder()
