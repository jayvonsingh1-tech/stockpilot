"""
Preference Learner - Learn user trading preferences and personalize signals
Learns which signals you take, skip, and why
"""
import sqlite3
import numpy as np
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from pathlib import Path
from collections import Counter
from ..utils.logger import setup_logger


logger = setup_logger(__name__)


class PreferenceLearner:
    """
    Learn user trading preferences to personalize future signals
    
    Learns:
    - Which strategies you prefer
    - Which confidence levels you take
    - Preferred sectors/tickers
    - Preferred timeframes
    - Risk tolerance
    - Position sizing preferences
    """
    
    def __init__(self, db_path: str = "data/stockpilot.db"):
        """
        Initialize preference learner
        
        Args:
            db_path: Path to SQLite database
        """
        self.db_path = db_path
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self._init_database()
    
    def _init_database(self):
        """Initialize preference tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # User preferences table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_preferences (
                key TEXT PRIMARY KEY,
                value TEXT,
                confidence REAL DEFAULT 0.5,
                sample_size INTEGER DEFAULT 0,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Signal feedback table (track which signals were taken/skipped)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS signal_feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                signal_id INTEGER,
                ticker TEXT,
                strategy TEXT,
                confidence INTEGER,
                action TEXT,
                timeframe TEXT,
                sector TEXT,
                feedback TEXT,
                reason TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
        logger.info("Preference learner initialized")
    
    def learn_from_trades(self, min_trades: int = 10):
        """
        Learn preferences from actual trading history
        
        Args:
            min_trades: Minimum trades needed to establish preference
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Get all trades
        cursor.execute('''
            SELECT * FROM trades 
            WHERE user_taken = 1
            ORDER BY entry_date DESC
        ''')
        
        trades = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        if len(trades) < min_trades:
            logger.info(f"Not enough trades for preference learning ({len(trades)}/{min_trades})")
            return
        
        # Learn strategy preferences
        self._learn_strategy_preference(trades)
        
        # Learn confidence threshold
        self._learn_confidence_threshold(trades)
        
        # Learn timeframe preference
        self._learn_timeframe_preference(trades)
        
        # Learn sector preferences
        self._learn_sector_preferences(trades)
        
        # Learn risk tolerance
        self._learn_risk_tolerance(trades)
        
        logger.info(f"Learned preferences from {len(trades)} trades")
    
    def _learn_strategy_preference(self, trades: List[Dict]):
        """Learn which strategies user prefers"""
        strategies = [t['strategy'] for t in trades if t['strategy']]
        
        if not strategies:
            return
        
        strategy_counts = Counter(strategies)
        total = len(strategies)
        
        # Calculate preference scores
        for strategy, count in strategy_counts.items():
            preference_score = count / total
            self._save_preference(
                f'strategy_{strategy}',
                str(preference_score),
                preference_score,
                count
            )
            logger.info(f"Strategy preference: {strategy} = {preference_score:.2f} ({count} trades)")
    
    def _learn_confidence_threshold(self, trades: List[Dict]):
        """Learn minimum confidence level user typically takes"""
        confidences = [t['confidence'] for t in trades if t['confidence']]
        
        if not confidences:
            return
        
        min_confidence = np.percentile(confidences, 25)  # 25th percentile
        avg_confidence = np.mean(confidences)
        
        self._save_preference('min_confidence', str(int(min_confidence)), 0.8, len(confidences))
        self._save_preference('preferred_confidence', str(int(avg_confidence)), 0.9, len(confidences))
        
        logger.info(f"Confidence threshold: min={min_confidence:.0f}%, preferred={avg_confidence:.0f}%")
    
    def _learn_timeframe_preference(self, trades: List[Dict]):
        """Learn preferred trading timeframes"""
        # Infer timeframe from hold days
        timeframes = []
        
        for trade in trades:
            if not trade.get('hold_days'):
                continue
            
            days = trade['hold_days']
            
            if days <= 3:
                timeframes.append('day')
            elif days <= 7:
                timeframes.append('swing')
            elif days <= 30:
                timeframes.append('position')
            else:
                timeframes.append('long')
        
        if not timeframes:
            return
        
        timeframe_counts = Counter(timeframes)
        total = len(timeframes)
        
        for timeframe, count in timeframe_counts.items():
            preference_score = count / total
            self._save_preference(
                f'timeframe_{timeframe}',
                str(preference_score),
                preference_score,
                count
            )
            logger.info(f"Timeframe preference: {timeframe} = {preference_score:.2f} ({count} trades)")
    
    def _learn_sector_preferences(self, trades: List[Dict]):
        """Learn preferred sectors"""
        # This would need sector data from trades
        # For now, we'll track tickers
        tickers = [t['ticker'] for t in trades if t['ticker']]
        
        if not tickers:
            return
        
        ticker_counts = Counter(tickers)
        
        # Save top 10 preferred tickers
        for ticker, count in ticker_counts.most_common(10):
            if count >= 2:  # At least 2 trades
                self._save_preference(
                    f'ticker_{ticker}',
                    'preferred',
                    count / len(tickers),
                    count
                )
    
    def _learn_risk_tolerance(self, trades: List[Dict]):
        """Learn risk tolerance from position sizes and stop losses"""
        # Calculate average risk per trade
        risks = []
        
        for trade in trades:
            if trade.get('stop_loss') and trade.get('entry_price'):
                risk_percent = abs((trade['stop_loss'] - trade['entry_price']) / trade['entry_price']) * 100
                risks.append(risk_percent)
        
        if not risks:
            return
        
        avg_risk = np.mean(risks)
        max_risk = np.max(risks)
        
        # Categorize risk tolerance
        if avg_risk < 2:
            risk_tolerance = 'conservative'
        elif avg_risk < 3:
            risk_tolerance = 'moderate'
        else:
            risk_tolerance = 'aggressive'
        
        self._save_preference('risk_tolerance', risk_tolerance, 0.8, len(risks))
        self._save_preference('avg_risk_percent', str(avg_risk), 0.9, len(risks))
        
        logger.info(f"Risk tolerance: {risk_tolerance} (avg risk: {avg_risk:.2f}%)")
    
    def should_send_signal(self, signal: Dict) -> Tuple[bool, str]:
        """
        Determine if signal matches user preferences
        
        Args:
            signal: Signal dictionary
            
        Returns:
            Tuple of (should_send, reason)
        """
        reasons = []
        score = 0
        max_score = 0
        
        # Check confidence threshold
        min_conf = self.get_preference('min_confidence', 80)
        max_score += 1
        if signal.get('confidence', 0) >= int(min_conf):
            score += 1
        else:
            reasons.append(f"Confidence {signal.get('confidence')}% below your threshold {min_conf}%")
        
        # Check strategy preference
        strategy = signal.get('strategy')
        if strategy:
            strategy_pref = self.get_preference(f'strategy_{strategy}')
            if strategy_pref:
                max_score += 1
                pref_score = float(strategy_pref)
                if pref_score > 0.2:  # User takes this strategy at least 20% of the time
                    score += 1
                else:
                    reasons.append(f"You rarely take {strategy} signals")
        
        # Check ticker preference
        ticker = signal.get('ticker')
        if ticker:
            ticker_pref = self.get_preference(f'ticker_{ticker}')
            if ticker_pref:
                max_score += 0.5
                score += 0.5
                reasons.append(f"You've traded {ticker} before")
        
        # Calculate final score
        if max_score > 0:
            final_score = (score / max_score) * 100
        else:
            final_score = 100  # No preferences yet, send everything
        
        should_send = final_score >= 50  # Send if matches at least 50% of preferences
        
        if should_send:
            reason = "Matches your trading preferences"
        else:
            reason = "; ".join(reasons) if reasons else "Doesn't match preferences"
        
        return should_send, reason
    
    def get_preference(self, key: str, default: any = None) -> Optional[str]:
        """
        Get user preference value
        
        Args:
            key: Preference key
            default: Default value if not found
            
        Returns:
            Preference value or default
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT value FROM user_preferences 
            WHERE key = ?
        ''', (key,))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return result[0]
        return default
    
    def get_all_preferences(self) -> Dict:
        """Get all user preferences"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM user_preferences 
            WHERE sample_size >= 3
            ORDER BY confidence DESC
        ''')
        
        preferences = {}
        for row in cursor.fetchall():
            preferences[row['key']] = {
                'value': row['value'],
                'confidence': row['confidence'],
                'sample_size': row['sample_size']
            }
        
        conn.close()
        return preferences
    
    def get_preference_summary(self) -> Dict:
        """Get human-readable preference summary"""
        prefs = self.get_all_preferences()
        
        summary = {
            'strategies': {},
            'timeframes': {},
            'confidence': {},
            'risk': {},
            'tickers': []
        }
        
        for key, data in prefs.items():
            if key.startswith('strategy_'):
                strategy = key.replace('strategy_', '')
                summary['strategies'][strategy] = {
                    'preference': float(data['value']),
                    'trades': data['sample_size']
                }
            elif key.startswith('timeframe_'):
                timeframe = key.replace('timeframe_', '')
                summary['timeframes'][timeframe] = {
                    'preference': float(data['value']),
                    'trades': data['sample_size']
                }
            elif key.startswith('ticker_'):
                ticker = key.replace('ticker_', '')
                summary['tickers'].append({
                    'ticker': ticker,
                    'trades': data['sample_size']
                })
            elif key in ['min_confidence', 'preferred_confidence']:
                summary['confidence'][key] = int(data['value'])
            elif key in ['risk_tolerance', 'avg_risk_percent']:
                summary['risk'][key] = data['value']
        
        return summary
    
    def record_signal_feedback(self, signal: Dict, feedback: str, reason: str = None):
        """
        Record user feedback on a signal
        
        Args:
            signal: Signal dictionary
            feedback: 'taken', 'skipped', 'ignored'
            reason: Optional reason for feedback
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO signal_feedback 
                (signal_id, ticker, strategy, confidence, action, timeframe, sector, feedback, reason)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                signal.get('signal_id'),
                signal.get('ticker'),
                signal.get('strategy'),
                signal.get('confidence'),
                signal.get('action'),
                signal.get('timeframe'),
                signal.get('sector'),
                feedback,
                reason
            ))
            conn.commit()
            logger.info(f"Recorded feedback: {feedback} for {signal.get('ticker')}")
        except Exception as e:
            logger.error(f"Error recording feedback: {e}")
        finally:
            conn.close()
    
    def _save_preference(self, key: str, value: str, confidence: float, sample_size: int):
        """Save preference to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT OR REPLACE INTO user_preferences 
                (key, value, confidence, sample_size, last_updated)
                VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
            ''', (key, value, confidence, sample_size))
            conn.commit()
        except Exception as e:
            logger.error(f"Error saving preference: {e}")
        finally:
            conn.close()
    
    def reset_preferences(self):
        """Reset all learned preferences"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('DELETE FROM user_preferences')
            cursor.execute('DELETE FROM signal_feedback')
            conn.commit()
            logger.info("All preferences reset")
        except Exception as e:
            logger.error(f"Error resetting preferences: {e}")
        finally:
            conn.close()
