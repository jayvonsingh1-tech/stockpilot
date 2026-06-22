"""
Performance Tracker - Track and analyze trading performance
Calculates metrics like win rate, Sharpe ratio, profit factor, etc.
"""
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from pathlib import Path
import numpy as np
from ..utils.logger import setup_logger


logger = setup_logger(__name__)


class PerformanceTracker:
    """Track and analyze trading performance with advanced metrics"""
    
    def __init__(self, db_path: str = "data/stockpilot.db"):
        """
        Initialize performance tracker
        
        Args:
            db_path: Path to SQLite database
        """
        self.db_path = db_path
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self._init_database()
    
    def _init_database(self):
        """Initialize performance tracking tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Performance metrics table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS performance_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date DATE UNIQUE NOT NULL,
                capital REAL,
                daily_pnl REAL,
                daily_pnl_percent REAL,
                total_pnl REAL,
                total_pnl_percent REAL,
                open_positions INTEGER,
                trades_today INTEGER,
                win_rate REAL,
                sharpe_ratio REAL,
                sortino_ratio REAL,
                profit_factor REAL,
                max_drawdown REAL,
                avg_win REAL,
                avg_loss REAL,
                largest_win REAL,
                largest_loss REAL,
                avg_hold_days REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Strategy performance table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS strategy_performance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                strategy TEXT NOT NULL,
                period TEXT NOT NULL,
                signals_sent INTEGER DEFAULT 0,
                signals_taken INTEGER DEFAULT 0,
                trades_won INTEGER DEFAULT 0,
                trades_lost INTEGER DEFAULT 0,
                win_rate REAL,
                avg_profit REAL,
                avg_loss REAL,
                profit_factor REAL,
                total_pnl REAL,
                confidence_accuracy REAL,
                avg_confidence INTEGER,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(strategy, period)
            )
        ''')
        
        conn.commit()
        conn.close()
        logger.info("Performance tracker database initialized")
    
    def calculate_daily_metrics(self, date: Optional[str] = None) -> Dict:
        """
        Calculate performance metrics for a specific date
        
        Args:
            date: Date to calculate metrics for (defaults to today)
            
        Returns:
            Dictionary with performance metrics
        """
        if not date:
            date = datetime.now().strftime('%Y-%m-%d')
        
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Get all closed trades up to this date
        cursor.execute('''
            SELECT * FROM trades 
            WHERE status = 'closed' 
            AND exit_date <= ?
            ORDER BY exit_date
        ''', (date,))
        
        trades = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        if not trades:
            return self._empty_metrics(date)
        
        # Calculate metrics
        metrics = {
            'date': date,
            'capital': self._calculate_capital(trades),
            'daily_pnl': self._calculate_daily_pnl(trades, date),
            'daily_pnl_percent': 0,
            'total_pnl': sum(t['pnl'] for t in trades if t['pnl']),
            'total_pnl_percent': 0,
            'open_positions': self._count_open_positions(date),
            'trades_today': self._count_trades_today(trades, date),
            'win_rate': self._calculate_win_rate(trades),
            'sharpe_ratio': self._calculate_sharpe_ratio(trades),
            'sortino_ratio': self._calculate_sortino_ratio(trades),
            'profit_factor': self._calculate_profit_factor(trades),
            'max_drawdown': self._calculate_max_drawdown(trades),
            'avg_win': self._calculate_avg_win(trades),
            'avg_loss': self._calculate_avg_loss(trades),
            'largest_win': self._calculate_largest_win(trades),
            'largest_loss': self._calculate_largest_loss(trades),
            'avg_hold_days': self._calculate_avg_hold_days(trades)
        }
        
        # Calculate percentages
        if metrics['capital'] > 0:
            metrics['daily_pnl_percent'] = (metrics['daily_pnl'] / metrics['capital']) * 100
            metrics['total_pnl_percent'] = (metrics['total_pnl'] / metrics['capital']) * 100
        
        return metrics
    
    def save_daily_metrics(self, metrics: Dict):
        """Save daily metrics to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT OR REPLACE INTO performance_metrics 
                (date, capital, daily_pnl, daily_pnl_percent, total_pnl, total_pnl_percent,
                 open_positions, trades_today, win_rate, sharpe_ratio, sortino_ratio,
                 profit_factor, max_drawdown, avg_win, avg_loss, largest_win, largest_loss,
                 avg_hold_days)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                metrics['date'], metrics['capital'], metrics['daily_pnl'],
                metrics['daily_pnl_percent'], metrics['total_pnl'], metrics['total_pnl_percent'],
                metrics['open_positions'], metrics['trades_today'], metrics['win_rate'],
                metrics['sharpe_ratio'], metrics['sortino_ratio'], metrics['profit_factor'],
                metrics['max_drawdown'], metrics['avg_win'], metrics['avg_loss'],
                metrics['largest_win'], metrics['largest_loss'], metrics['avg_hold_days']
            ))
            conn.commit()
            logger.info(f"Saved daily metrics for {metrics['date']}")
        except Exception as e:
            logger.error(f"Error saving daily metrics: {e}")
        finally:
            conn.close()
    
    def update_strategy_performance(self, strategy: str, period: str = 'all_time'):
        """
        Update performance metrics for a specific strategy
        
        Args:
            strategy: Strategy name
            period: Time period ('all_time', 'month', 'week')
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Get date filter
        date_filter = self._get_date_filter(period)
        
        # Get all trades for this strategy
        query = '''
            SELECT * FROM trades 
            WHERE strategy = ? AND status = 'closed'
        '''
        params = [strategy]
        
        if date_filter:
            query += ' AND exit_date >= ?'
            params.append(date_filter)
        
        cursor.execute(query, params)
        trades = [dict(row) for row in cursor.fetchall()]
        
        # Get all signals for this strategy
        signal_query = '''
            SELECT COUNT(*) as count FROM signals 
            WHERE strategy = ?
        '''
        signal_params = [strategy]
        
        if date_filter:
            signal_query += ' AND created_at >= ?'
            signal_params.append(date_filter)
        
        cursor.execute(signal_query, signal_params)
        signals_sent = cursor.fetchone()['count']
        
        conn.close()
        
        if not trades:
            return
        
        # Calculate strategy metrics
        signals_taken = len(trades)
        trades_won = len([t for t in trades if t['pnl'] and t['pnl'] > 0])
        trades_lost = len([t for t in trades if t['pnl'] and t['pnl'] < 0])
        win_rate = (trades_won / len(trades)) * 100 if trades else 0
        
        wins = [t['pnl'] for t in trades if t['pnl'] and t['pnl'] > 0]
        losses = [abs(t['pnl']) for t in trades if t['pnl'] and t['pnl'] < 0]
        
        avg_profit = np.mean(wins) if wins else 0
        avg_loss = np.mean(losses) if losses else 0
        profit_factor = sum(wins) / sum(losses) if losses and sum(losses) > 0 else 0
        total_pnl = sum(t['pnl'] for t in trades if t['pnl'])
        
        # Calculate confidence accuracy
        confidence_accuracy = self._calculate_confidence_accuracy(trades)
        avg_confidence = np.mean([t['confidence'] for t in trades if t['confidence']]) if trades else 0
        
        # Save to database
        self._save_strategy_performance(
            strategy, period, signals_sent, signals_taken, trades_won, trades_lost,
            win_rate, avg_profit, avg_loss, profit_factor, total_pnl,
            confidence_accuracy, avg_confidence
        )
    
    def get_performance_summary(self, days: int = 30) -> Dict:
        """
        Get performance summary for last N days
        
        Args:
            days: Number of days to look back
            
        Returns:
            Performance summary dictionary
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cutoff_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
        
        # Get recent metrics
        cursor.execute('''
            SELECT * FROM performance_metrics 
            WHERE date >= ?
            ORDER BY date DESC
            LIMIT 1
        ''', (cutoff_date,))
        
        latest = cursor.fetchone()
        
        if not latest:
            conn.close()
            return self._empty_summary()
        
        latest = dict(latest)
        
        # Get strategy breakdown
        cursor.execute('''
            SELECT * FROM strategy_performance 
            WHERE period = 'all_time'
            ORDER BY win_rate DESC
        ''')
        
        strategies = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return {
            'capital': latest['capital'],
            'total_pnl': latest['total_pnl'],
            'total_pnl_percent': latest['total_pnl_percent'],
            'win_rate': latest['win_rate'],
            'sharpe_ratio': latest['sharpe_ratio'],
            'profit_factor': latest['profit_factor'],
            'max_drawdown': latest['max_drawdown'],
            'avg_win': latest['avg_win'],
            'avg_loss': latest['avg_loss'],
            'open_positions': latest['open_positions'],
            'strategies': strategies
        }
    
    def _calculate_capital(self, trades: List[Dict]) -> float:
        """Calculate current capital"""
        initial_capital = 50000  # Default starting capital
        total_pnl = sum(t['pnl'] for t in trades if t['pnl'])
        return initial_capital + total_pnl
    
    def _calculate_daily_pnl(self, trades: List[Dict], date: str) -> float:
        """Calculate P&L for specific date"""
        daily_trades = [t for t in trades if t['exit_date'] and t['exit_date'].startswith(date)]
        return sum(t['pnl'] for t in daily_trades if t['pnl'])
    
    def _count_open_positions(self, date: str) -> int:
        """Count open positions on date"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT COUNT(*) FROM trades 
            WHERE status = 'open' 
            AND entry_date <= ?
        ''', (date,))
        
        count = cursor.fetchone()[0]
        conn.close()
        return count
    
    def _count_trades_today(self, trades: List[Dict], date: str) -> int:
        """Count trades closed today"""
        return len([t for t in trades if t['exit_date'] and t['exit_date'].startswith(date)])
    
    def _calculate_win_rate(self, trades: List[Dict]) -> float:
        """Calculate win rate"""
        if not trades:
            return 0
        wins = len([t for t in trades if t['pnl'] and t['pnl'] > 0])
        return (wins / len(trades)) * 100
    
    def _calculate_sharpe_ratio(self, trades: List[Dict]) -> float:
        """Calculate Sharpe ratio"""
        if not trades:
            return 0
        
        returns = [t['pnl_percent'] for t in trades if t['pnl_percent']]
        if not returns:
            return 0
        
        mean_return = np.mean(returns)
        std_return = np.std(returns)
        
        if std_return == 0:
            return 0
        
        # Annualized Sharpe ratio (assuming 252 trading days)
        sharpe = (mean_return / std_return) * np.sqrt(252)
        return round(sharpe, 2)
    
    def _calculate_sortino_ratio(self, trades: List[Dict]) -> float:
        """Calculate Sortino ratio (downside deviation)"""
        if not trades:
            return 0
        
        returns = [t['pnl_percent'] for t in trades if t['pnl_percent']]
        if not returns:
            return 0
        
        mean_return = np.mean(returns)
        downside_returns = [r for r in returns if r < 0]
        
        if not downside_returns:
            return 0
        
        downside_std = np.std(downside_returns)
        
        if downside_std == 0:
            return 0
        
        sortino = (mean_return / downside_std) * np.sqrt(252)
        return round(sortino, 2)
    
    def _calculate_profit_factor(self, trades: List[Dict]) -> float:
        """Calculate profit factor"""
        wins = sum(t['pnl'] for t in trades if t['pnl'] and t['pnl'] > 0)
        losses = abs(sum(t['pnl'] for t in trades if t['pnl'] and t['pnl'] < 0))
        
        if losses == 0:
            return 0
        
        return round(wins / losses, 2)
    
    def _calculate_max_drawdown(self, trades: List[Dict]) -> float:
        """Calculate maximum drawdown"""
        if not trades:
            return 0
        
        # Sort by exit date
        sorted_trades = sorted(trades, key=lambda x: x['exit_date'] or '')
        
        # Calculate cumulative P&L
        cumulative_pnl = []
        running_total = 0
        
        for trade in sorted_trades:
            if trade['pnl']:
                running_total += trade['pnl']
                cumulative_pnl.append(running_total)
        
        if not cumulative_pnl:
            return 0
        
        # Calculate drawdown
        peak = cumulative_pnl[0]
        max_dd = 0
        
        for pnl in cumulative_pnl:
            if pnl > peak:
                peak = pnl
            dd = ((peak - pnl) / peak) * 100 if peak > 0 else 0
            max_dd = max(max_dd, dd)
        
        return round(max_dd, 2)
    
    def _calculate_avg_win(self, trades: List[Dict]) -> float:
        """Calculate average winning trade"""
        wins = [t['pnl'] for t in trades if t['pnl'] and t['pnl'] > 0]
        return round(np.mean(wins), 2) if wins else 0
    
    def _calculate_avg_loss(self, trades: List[Dict]) -> float:
        """Calculate average losing trade"""
        losses = [t['pnl'] for t in trades if t['pnl'] and t['pnl'] < 0]
        return round(np.mean(losses), 2) if losses else 0
    
    def _calculate_largest_win(self, trades: List[Dict]) -> float:
        """Calculate largest winning trade"""
        wins = [t['pnl'] for t in trades if t['pnl'] and t['pnl'] > 0]
        return round(max(wins), 2) if wins else 0
    
    def _calculate_largest_loss(self, trades: List[Dict]) -> float:
        """Calculate largest losing trade"""
        losses = [t['pnl'] for t in trades if t['pnl'] and t['pnl'] < 0]
        return round(min(losses), 2) if losses else 0
    
    def _calculate_avg_hold_days(self, trades: List[Dict]) -> float:
        """Calculate average hold time in days"""
        hold_days = [t['hold_days'] for t in trades if t['hold_days']]
        return round(np.mean(hold_days), 1) if hold_days else 0
    
    def _calculate_confidence_accuracy(self, trades: List[Dict]) -> float:
        """Calculate how accurate confidence scores are"""
        if not trades:
            return 0
        
        # Group trades by confidence level
        confidence_groups = {}
        
        for trade in trades:
            if not trade['confidence'] or not trade['pnl']:
                continue
            
            conf_bucket = (trade['confidence'] // 10) * 10  # Round to nearest 10
            
            if conf_bucket not in confidence_groups:
                confidence_groups[conf_bucket] = {'wins': 0, 'total': 0}
            
            confidence_groups[conf_bucket]['total'] += 1
            if trade['pnl'] > 0:
                confidence_groups[conf_bucket]['wins'] += 1
        
        # Calculate accuracy score
        accuracy_scores = []
        
        for conf, data in confidence_groups.items():
            actual_win_rate = (data['wins'] / data['total']) * 100
            expected_win_rate = conf
            accuracy = 100 - abs(actual_win_rate - expected_win_rate)
            accuracy_scores.append(accuracy)
        
        return round(np.mean(accuracy_scores), 2) if accuracy_scores else 0
    
    def _save_strategy_performance(self, strategy: str, period: str, signals_sent: int,
                                   signals_taken: int, trades_won: int, trades_lost: int,
                                   win_rate: float, avg_profit: float, avg_loss: float,
                                   profit_factor: float, total_pnl: float,
                                   confidence_accuracy: float, avg_confidence: float):
        """Save strategy performance to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT OR REPLACE INTO strategy_performance 
                (strategy, period, signals_sent, signals_taken, trades_won, trades_lost,
                 win_rate, avg_profit, avg_loss, profit_factor, total_pnl,
                 confidence_accuracy, avg_confidence, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            ''', (
                strategy, period, signals_sent, signals_taken, trades_won, trades_lost,
                win_rate, avg_profit, avg_loss, profit_factor, total_pnl,
                confidence_accuracy, avg_confidence
            ))
            conn.commit()
            logger.info(f"Updated strategy performance for {strategy} ({period})")
        except Exception as e:
            logger.error(f"Error saving strategy performance: {e}")
        finally:
            conn.close()
    
    def _get_date_filter(self, period: str) -> Optional[str]:
        """Get date filter for period"""
        if period == 'all_time':
            return None
        elif period == 'month':
            return (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        elif period == 'week':
            return (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
        return None
    
    def _empty_metrics(self, date: str) -> Dict:
        """Return empty metrics"""
        return {
            'date': date,
            'capital': 50000,
            'daily_pnl': 0,
            'daily_pnl_percent': 0,
            'total_pnl': 0,
            'total_pnl_percent': 0,
            'open_positions': 0,
            'trades_today': 0,
            'win_rate': 0,
            'sharpe_ratio': 0,
            'sortino_ratio': 0,
            'profit_factor': 0,
            'max_drawdown': 0,
            'avg_win': 0,
            'avg_loss': 0,
            'largest_win': 0,
            'largest_loss': 0,
            'avg_hold_days': 0
        }
    
    def _empty_summary(self) -> Dict:
        """Return empty summary"""
        return {
            'capital': 50000,
            'total_pnl': 0,
            'total_pnl_percent': 0,
            'win_rate': 0,
            'sharpe_ratio': 0,
            'profit_factor': 0,
            'max_drawdown': 0,
            'avg_win': 0,
            'avg_loss': 0,
            'open_positions': 0,
            'strategies': []
        }
