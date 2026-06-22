"""
Strategy Optimizer - Optimize strategy parameters based on performance
Uses historical data to find optimal parameter combinations
"""
import sqlite3
import numpy as np
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta
from pathlib import Path
from itertools import product
from ..utils.logger import setup_logger


logger = setup_logger(__name__)


class StrategyOptimizer:
    """
    Optimize trading strategy parameters
    
    Finds optimal values for:
    - Technical indicator periods (EMA, RSI, etc.)
    - Confidence thresholds
    - Risk/reward ratios
    - Position sizing
    """
    
    def __init__(self, db_path: str = "data/stockpilot.db"):
        """
        Initialize strategy optimizer
        
        Args:
            db_path: Path to SQLite database
        """
        self.db_path = db_path
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self._init_database()
    
    def _init_database(self):
        """Initialize optimization tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Optimization results table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS optimization_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                strategy TEXT NOT NULL,
                parameter_set TEXT NOT NULL,
                win_rate REAL,
                profit_factor REAL,
                sharpe_ratio REAL,
                total_pnl REAL,
                max_drawdown REAL,
                total_trades INTEGER,
                optimization_score REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Current optimal parameters table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS optimal_parameters (
                strategy TEXT PRIMARY KEY,
                parameters TEXT NOT NULL,
                score REAL,
                last_optimized TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
        logger.info("Strategy optimizer initialized")
    
    def optimize_strategy(self, strategy: str, parameter_ranges: Dict,
                         metric: str = 'sharpe_ratio', min_trades: int = 20) -> Dict:
        """
        Optimize strategy parameters
        
        Args:
            strategy: Strategy name
            parameter_ranges: Dict of parameter names to ranges
                Example: {'ema_fast': range(10, 30), 'ema_slow': range(40, 60)}
            metric: Optimization metric ('sharpe_ratio', 'profit_factor', 'win_rate')
            min_trades: Minimum trades needed for optimization
            
        Returns:
            Dictionary with optimal parameters and results
        """
        logger.info(f"Optimizing {strategy} strategy...")
        
        # Get historical trades for this strategy
        trades = self._get_strategy_trades(strategy)
        
        if len(trades) < min_trades:
            logger.warning(f"Not enough trades for optimization ({len(trades)}/{min_trades})")
            return None
        
        # Generate parameter combinations
        param_names = list(parameter_ranges.keys())
        param_values = [parameter_ranges[name] for name in param_names]
        combinations = list(product(*param_values))
        
        logger.info(f"Testing {len(combinations)} parameter combinations...")
        
        best_score = -np.inf
        best_params = None
        best_results = None
        
        # Test each combination
        for i, combo in enumerate(combinations):
            params = dict(zip(param_names, combo))
            
            # Simulate trades with these parameters
            results = self._simulate_with_parameters(trades, params, strategy)
            
            if not results or results['total_trades'] < min_trades:
                continue
            
            # Calculate optimization score
            score = self._calculate_optimization_score(results, metric)
            
            # Save result
            self._save_optimization_result(strategy, params, results, score)
            
            # Track best
            if score > best_score:
                best_score = score
                best_params = params
                best_results = results
            
            # Progress update
            if (i + 1) % 10 == 0:
                logger.info(f"Progress: {i+1}/{len(combinations)} combinations tested")
        
        if best_params:
            # Save optimal parameters
            self._save_optimal_parameters(strategy, best_params, best_score)
            
            logger.info(f"Optimization complete! Best {metric}: {best_score:.2f}")
            logger.info(f"Optimal parameters: {best_params}")
            
            return {
                'strategy': strategy,
                'parameters': best_params,
                'score': best_score,
                'results': best_results
            }
        
        return None
    
    def get_optimal_parameters(self, strategy: str) -> Optional[Dict]:
        """
        Get current optimal parameters for strategy
        
        Args:
            strategy: Strategy name
            
        Returns:
            Dictionary with optimal parameters or None
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM optimal_parameters 
            WHERE strategy = ?
        ''', (strategy,))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            import json
            return {
                'strategy': result['strategy'],
                'parameters': json.loads(result['parameters']),
                'score': result['score'],
                'last_optimized': result['last_optimized']
            }
        
        return None
    
    def needs_reoptimization(self, strategy: str, threshold_days: int = 30,
                            threshold_trades: int = 50) -> bool:
        """
        Check if strategy needs reoptimization
        
        Args:
            strategy: Strategy name
            threshold_days: Days since last optimization
            threshold_trades: New trades since last optimization
            
        Returns:
            True if needs reoptimization
        """
        optimal = self.get_optimal_parameters(strategy)
        
        if not optimal:
            return True
        
        # Check days since last optimization
        last_optimized = datetime.fromisoformat(optimal['last_optimized'])
        days_since = (datetime.now() - last_optimized).days
        
        if days_since >= threshold_days:
            return True
        
        # Check new trades since last optimization
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT COUNT(*) FROM trades 
            WHERE strategy = ? AND status = 'closed'
            AND exit_date >= ?
        ''', (strategy, optimal['last_optimized']))
        
        new_trades = cursor.fetchone()[0]
        conn.close()
        
        return new_trades >= threshold_trades
    
    def _get_strategy_trades(self, strategy: str) -> List[Dict]:
        """Get all closed trades for strategy"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM trades 
            WHERE strategy = ? AND status = 'closed'
            ORDER BY exit_date
        ''', (strategy,))
        
        trades = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return trades
    
    def _simulate_with_parameters(self, trades: List[Dict], params: Dict,
                                  strategy: str) -> Optional[Dict]:
        """
        Simulate trades with given parameters
        
        This is a simplified simulation. In reality, you'd re-run the strategy
        with these parameters on historical data.
        
        For now, we'll filter trades based on parameters like confidence threshold.
        """
        # Filter trades based on parameters
        filtered_trades = trades.copy()
        
        # Apply confidence threshold if specified
        if 'min_confidence' in params:
            filtered_trades = [
                t for t in filtered_trades 
                if t.get('confidence', 0) >= params['min_confidence']
            ]
        
        # Apply risk/reward filter if specified
        if 'min_risk_reward' in params:
            filtered_trades = [
                t for t in filtered_trades 
                if self._calculate_risk_reward(t) >= params['min_risk_reward']
            ]
        
        if not filtered_trades:
            return None
        
        # Calculate performance metrics
        wins = [t for t in filtered_trades if t.get('pnl', 0) > 0]
        losses = [t for t in filtered_trades if t.get('pnl', 0) < 0]
        
        win_rate = (len(wins) / len(filtered_trades)) * 100 if filtered_trades else 0
        
        total_profit = sum(t['pnl'] for t in wins if t.get('pnl'))
        total_loss = abs(sum(t['pnl'] for t in losses if t.get('pnl')))
        profit_factor = total_profit / total_loss if total_loss > 0 else 0
        
        total_pnl = sum(t.get('pnl', 0) for t in filtered_trades)
        
        # Calculate Sharpe ratio
        returns = [t.get('pnl_percent', 0) for t in filtered_trades if t.get('pnl_percent')]
        if returns:
            mean_return = np.mean(returns)
            std_return = np.std(returns)
            sharpe = (mean_return / std_return) * np.sqrt(252) if std_return > 0 else 0
        else:
            sharpe = 0
        
        # Calculate max drawdown
        max_dd = self._calculate_max_drawdown(filtered_trades)
        
        return {
            'total_trades': len(filtered_trades),
            'win_rate': win_rate,
            'profit_factor': profit_factor,
            'sharpe_ratio': sharpe,
            'total_pnl': total_pnl,
            'max_drawdown': max_dd,
            'avg_win': np.mean([t['pnl'] for t in wins if t.get('pnl')]) if wins else 0,
            'avg_loss': np.mean([t['pnl'] for t in losses if t.get('pnl')]) if losses else 0
        }
    
    def _calculate_risk_reward(self, trade: Dict) -> float:
        """Calculate risk/reward ratio for trade"""
        if not trade.get('entry_price') or not trade.get('stop_loss') or not trade.get('take_profit_1'):
            return 0
        
        risk = abs(trade['entry_price'] - trade['stop_loss'])
        reward = abs(trade['take_profit_1'] - trade['entry_price'])
        
        return reward / risk if risk > 0 else 0
    
    def _calculate_max_drawdown(self, trades: List[Dict]) -> float:
        """Calculate maximum drawdown"""
        if not trades:
            return 0
        
        cumulative_pnl = []
        running_total = 0
        
        for trade in trades:
            if trade.get('pnl'):
                running_total += trade['pnl']
                cumulative_pnl.append(running_total)
        
        if not cumulative_pnl:
            return 0
        
        peak = cumulative_pnl[0]
        max_dd = 0
        
        for pnl in cumulative_pnl:
            if pnl > peak:
                peak = pnl
            dd = ((peak - pnl) / peak) * 100 if peak > 0 else 0
            max_dd = max(max_dd, dd)
        
        return max_dd
    
    def _calculate_optimization_score(self, results: Dict, metric: str) -> float:
        """Calculate optimization score based on metric"""
        if metric == 'sharpe_ratio':
            return results['sharpe_ratio']
        elif metric == 'profit_factor':
            return results['profit_factor']
        elif metric == 'win_rate':
            return results['win_rate']
        elif metric == 'total_pnl':
            return results['total_pnl']
        else:
            # Combined score
            return (
                results['sharpe_ratio'] * 0.4 +
                results['profit_factor'] * 0.3 +
                results['win_rate'] * 0.2 +
                (100 - results['max_drawdown']) * 0.1
            )
    
    def _save_optimization_result(self, strategy: str, params: Dict,
                                  results: Dict, score: float):
        """Save optimization result to database"""
        import json
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO optimization_results 
                (strategy, parameter_set, win_rate, profit_factor, sharpe_ratio,
                 total_pnl, max_drawdown, total_trades, optimization_score)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                strategy,
                json.dumps(params),
                results['win_rate'],
                results['profit_factor'],
                results['sharpe_ratio'],
                results['total_pnl'],
                results['max_drawdown'],
                results['total_trades'],
                score
            ))
            conn.commit()
        except Exception as e:
            logger.error(f"Error saving optimization result: {e}")
        finally:
            conn.close()
    
    def _save_optimal_parameters(self, strategy: str, params: Dict, score: float):
        """Save optimal parameters to database"""
        import json
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT OR REPLACE INTO optimal_parameters 
                (strategy, parameters, score, last_optimized)
                VALUES (?, ?, ?, CURRENT_TIMESTAMP)
            ''', (strategy, json.dumps(params), score))
            conn.commit()
            logger.info(f"Saved optimal parameters for {strategy}")
        except Exception as e:
            logger.error(f"Error saving optimal parameters: {e}")
        finally:
            conn.close()
    
    def get_optimization_history(self, strategy: str, limit: int = 10) -> List[Dict]:
        """Get optimization history for strategy"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM optimization_results 
            WHERE strategy = ?
            ORDER BY optimization_score DESC
            LIMIT ?
        ''', (strategy, limit))
        
        results = []
        for row in cursor.fetchall():
            import json
            result = dict(row)
            result['parameter_set'] = json.loads(result['parameter_set'])
            results.append(result)
        
        conn.close()
        return results
