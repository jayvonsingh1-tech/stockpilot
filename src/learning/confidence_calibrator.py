"""
Confidence Calibrator - Learn and improve confidence score accuracy
Adjusts confidence scoring based on actual trade outcomes
"""
import sqlite3
import numpy as np
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta
from pathlib import Path
from ..utils.logger import setup_logger


logger = setup_logger(__name__)


class ConfidenceCalibrator:
    """
    Calibrate confidence scores based on actual results
    
    The bot learns:
    - If 90% confidence signals actually win 90% of the time
    - Which strategies are over/under confident
    - How to adjust future confidence scores
    """
    
    def __init__(self, db_path: str = "data/stockpilot.db"):
        """
        Initialize confidence calibrator
        
        Args:
            db_path: Path to SQLite database
        """
        self.db_path = db_path
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self._init_database()
    
    def _init_database(self):
        """Initialize calibration tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Confidence calibration table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS confidence_calibration (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                strategy TEXT NOT NULL,
                confidence_bucket INTEGER NOT NULL,
                predicted_win_rate REAL,
                actual_win_rate REAL,
                sample_size INTEGER,
                calibration_factor REAL,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(strategy, confidence_bucket)
            )
        ''')
        
        conn.commit()
        conn.close()
        logger.info("Confidence calibrator initialized")
    
    def calibrate_all_strategies(self, min_sample_size: int = 10):
        """
        Calibrate confidence scores for all strategies
        
        Args:
            min_sample_size: Minimum trades needed for calibration
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Get all strategies with closed trades
        cursor.execute('''
            SELECT DISTINCT strategy FROM trades 
            WHERE status = 'closed' AND confidence IS NOT NULL
        ''')
        
        strategies = [row['strategy'] for row in cursor.fetchall()]
        conn.close()
        
        for strategy in strategies:
            self.calibrate_strategy(strategy, min_sample_size)
    
    def calibrate_strategy(self, strategy: str, min_sample_size: int = 10):
        """
        Calibrate confidence scores for a specific strategy
        
        Args:
            strategy: Strategy name
            min_sample_size: Minimum trades needed for calibration
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Get all closed trades for this strategy
        cursor.execute('''
            SELECT confidence, pnl FROM trades 
            WHERE strategy = ? AND status = 'closed' 
            AND confidence IS NOT NULL AND pnl IS NOT NULL
        ''', (strategy,))
        
        trades = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        if len(trades) < min_sample_size:
            logger.info(f"Not enough trades for {strategy} calibration ({len(trades)}/{min_sample_size})")
            return
        
        # Group trades by confidence bucket (10% buckets)
        confidence_buckets = {}
        
        for trade in trades:
            bucket = (trade['confidence'] // 10) * 10  # Round to nearest 10
            
            if bucket not in confidence_buckets:
                confidence_buckets[bucket] = {'wins': 0, 'total': 0}
            
            confidence_buckets[bucket]['total'] += 1
            if trade['pnl'] > 0:
                confidence_buckets[bucket]['wins'] += 1
        
        # Calculate calibration factors for each bucket
        for bucket, data in confidence_buckets.items():
            if data['total'] < 5:  # Need at least 5 trades per bucket
                continue
            
            predicted_win_rate = bucket
            actual_win_rate = (data['wins'] / data['total']) * 100
            
            # Calculate calibration factor
            # If actual > predicted: bot is too conservative (increase confidence)
            # If actual < predicted: bot is too optimistic (decrease confidence)
            calibration_factor = actual_win_rate / predicted_win_rate if predicted_win_rate > 0 else 1.0
            
            # Save calibration
            self._save_calibration(
                strategy, bucket, predicted_win_rate, actual_win_rate,
                data['total'], calibration_factor
            )
            
            logger.info(
                f"{strategy} - Confidence {bucket}%: "
                f"Predicted {predicted_win_rate}%, Actual {actual_win_rate:.1f}%, "
                f"Factor {calibration_factor:.2f}"
            )
    
    def get_calibrated_confidence(self, strategy: str, raw_confidence: int) -> int:
        """
        Get calibrated confidence score
        
        Args:
            strategy: Strategy name
            raw_confidence: Raw confidence score (0-100)
            
        Returns:
            Calibrated confidence score (0-100)
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Get calibration factor for this confidence bucket
        bucket = (raw_confidence // 10) * 10
        
        cursor.execute('''
            SELECT calibration_factor, sample_size FROM confidence_calibration 
            WHERE strategy = ? AND confidence_bucket = ?
        ''', (strategy, bucket))
        
        result = cursor.fetchone()
        conn.close()
        
        if not result or result['sample_size'] < 10:
            # Not enough data, return raw confidence
            return raw_confidence
        
        # Apply calibration factor
        calibrated = raw_confidence * result['calibration_factor']
        
        # Clamp to 0-100 range
        calibrated = max(0, min(100, calibrated))
        
        logger.debug(
            f"{strategy}: Raw confidence {raw_confidence}% → "
            f"Calibrated {calibrated:.0f}% (factor: {result['calibration_factor']:.2f})"
        )
        
        return int(calibrated)
    
    def get_calibration_report(self, strategy: Optional[str] = None) -> Dict:
        """
        Get calibration report
        
        Args:
            strategy: Optional strategy to filter by
            
        Returns:
            Calibration report dictionary
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        if strategy:
            cursor.execute('''
                SELECT * FROM confidence_calibration 
                WHERE strategy = ? AND sample_size >= 5
                ORDER BY confidence_bucket
            ''', (strategy,))
        else:
            cursor.execute('''
                SELECT * FROM confidence_calibration 
                WHERE sample_size >= 5
                ORDER BY strategy, confidence_bucket
            ''')
        
        calibrations = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        # Calculate overall accuracy
        if calibrations:
            accuracy_scores = [
                100 - abs(c['actual_win_rate'] - c['predicted_win_rate'])
                for c in calibrations
            ]
            overall_accuracy = np.mean(accuracy_scores)
        else:
            overall_accuracy = 0
        
        return {
            'overall_accuracy': round(overall_accuracy, 2),
            'calibrations': calibrations,
            'total_buckets': len(calibrations)
        }
    
    def needs_recalibration(self, strategy: str, threshold_days: int = 7) -> bool:
        """
        Check if strategy needs recalibration
        
        Args:
            strategy: Strategy name
            threshold_days: Days since last calibration
            
        Returns:
            True if needs recalibration
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT MAX(last_updated) as last_update FROM confidence_calibration 
            WHERE strategy = ?
        ''', (strategy,))
        
        result = cursor.fetchone()
        conn.close()
        
        if not result or not result[0]:
            return True
        
        last_update = datetime.fromisoformat(result[0])
        days_since = (datetime.now() - last_update).days
        
        return days_since >= threshold_days
    
    def get_strategy_bias(self, strategy: str) -> Dict:
        """
        Determine if strategy is over/under confident
        
        Args:
            strategy: Strategy name
            
        Returns:
            Dictionary with bias information
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT 
                AVG(calibration_factor) as avg_factor,
                AVG(actual_win_rate - predicted_win_rate) as avg_diff,
                SUM(sample_size) as total_trades
            FROM confidence_calibration 
            WHERE strategy = ? AND sample_size >= 5
        ''', (strategy,))
        
        result = cursor.fetchone()
        conn.close()
        
        if not result or not result['total_trades']:
            return {
                'bias': 'unknown',
                'factor': 1.0,
                'description': 'Not enough data'
            }
        
        avg_factor = result['avg_factor']
        avg_diff = result['avg_diff']
        
        if avg_factor > 1.1:
            bias = 'under_confident'
            description = f'Strategy is too conservative. Actual performance is {avg_diff:.1f}% better than predicted.'
        elif avg_factor < 0.9:
            bias = 'over_confident'
            description = f'Strategy is too optimistic. Actual performance is {abs(avg_diff):.1f}% worse than predicted.'
        else:
            bias = 'well_calibrated'
            description = 'Strategy confidence scores are accurate.'
        
        return {
            'bias': bias,
            'factor': round(avg_factor, 2),
            'avg_difference': round(avg_diff, 2),
            'description': description,
            'total_trades': result['total_trades']
        }
    
    def _save_calibration(self, strategy: str, confidence_bucket: int,
                         predicted_win_rate: float, actual_win_rate: float,
                         sample_size: int, calibration_factor: float):
        """Save calibration to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT OR REPLACE INTO confidence_calibration 
                (strategy, confidence_bucket, predicted_win_rate, actual_win_rate,
                 sample_size, calibration_factor, last_updated)
                VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            ''', (
                strategy, confidence_bucket, predicted_win_rate, actual_win_rate,
                sample_size, calibration_factor
            ))
            conn.commit()
        except Exception as e:
            logger.error(f"Error saving calibration: {e}")
        finally:
            conn.close()
    
    def auto_calibrate_on_trade_close(self, trade_id: int):
        """
        Automatically recalibrate when a trade closes
        
        Args:
            trade_id: ID of closed trade
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Get trade details
        cursor.execute('SELECT strategy FROM trades WHERE id = ?', (trade_id,))
        trade = cursor.fetchone()
        conn.close()
        
        if not trade:
            return
        
        strategy = trade['strategy']
        
        # Check if needs recalibration
        if self.needs_recalibration(strategy, threshold_days=7):
            logger.info(f"Auto-calibrating {strategy} after trade close")
            self.calibrate_strategy(strategy)
