"""
Trade Database V2 - Enhanced for Phase 4
Includes user feedback, timeframes, and performance tracking
"""
import sqlite3
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from pathlib import Path
from ..utils.logger import setup_logger


logger = setup_logger(__name__)


class TradeDatabaseV2:
    """
    Enhanced SQLite database for Phase 4 trade tracking
    
    Features:
    - User feedback tracking (taken/skipped)
    - Precise timeframe management
    - Multiple take profit levels
    - Trade reminders
    - Performance analytics
    - Strategy performance tracking
    """
    
    def __init__(self, db_path: str = "data/stockpilot.db"):
        """Initialize database connection"""
        self.db_path = db_path
        
        # Create data directory if needed
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        
        # Initialize database
        self._init_database()
        
        logger.info(f"Trade database V2 initialized: {db_path}")
    
    def _init_database(self):
        """Create enhanced database tables"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Enhanced trades table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS trades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                signal_id INTEGER,
                ticker TEXT NOT NULL,
                action TEXT NOT NULL,
                strategy TEXT,
                timeframe TEXT,
                
                -- Entry
                entry_price REAL,
                entry_date DATETIME,
                stop_loss REAL,
                take_profit_1 REAL,
                take_profit_2 REAL,
                take_profit_3 REAL,
                
                -- Exit
                exit_price REAL,
                exit_date DATETIME,
                exit_reason TEXT,
                hold_days INTEGER,
                
                -- Performance
                confidence INTEGER,
                pnl REAL,
                pnl_percent REAL,
                risk_reward_ratio REAL,
                
                -- Status
                status TEXT DEFAULT 'pending',
                user_taken BOOLEAN DEFAULT 0,
                user_notes TEXT,
                
                -- Timeframe details
                recommended_hold_days INTEGER,
                entry_window_hours INTEGER DEFAULT 24,
                review_date DATE,
                max_hold_date DATE,
                exit_by_date DATE,
                
                -- Metadata
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Trade feedback table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS trade_feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                trade_id INTEGER NOT NULL,
                feedback_type TEXT NOT NULL,
                feedback_value TEXT,
                notes TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (trade_id) REFERENCES trades(id)
            )
        ''')
        
        # Performance metrics table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS performance_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date DATE UNIQUE,
                capital REAL,
                daily_pnl REAL,
                daily_pnl_percent REAL,
                total_pnl REAL,
                total_pnl_percent REAL,
                open_positions INTEGER,
                trades_today INTEGER,
                win_rate REAL,
                sharpe_ratio REAL,
                max_drawdown REAL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Strategy performance table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS strategy_performance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                strategy TEXT NOT NULL,
                period TEXT,
                signals_sent INTEGER DEFAULT 0,
                signals_taken INTEGER DEFAULT 0,
                win_rate REAL DEFAULT 0,
                avg_profit REAL DEFAULT 0,
                avg_loss REAL DEFAULT 0,
                profit_factor REAL DEFAULT 0,
                confidence_accuracy REAL DEFAULT 0,
                total_pnl REAL DEFAULT 0,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # User preferences table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_preferences (
                key TEXT PRIMARY KEY,
                value TEXT,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Trade reminders table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS trade_reminders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                trade_id INTEGER NOT NULL,
                reminder_type TEXT NOT NULL,
                reminder_date DATE NOT NULL,
                message TEXT,
                sent BOOLEAN DEFAULT 0,
                sent_at DATETIME,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (trade_id) REFERENCES trades(id)
            )
        ''')
        
        # Signals table (enhanced)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS signals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ticker TEXT NOT NULL,
                action TEXT NOT NULL,
                strategy TEXT,
                confidence INTEGER,
                entry_price REAL,
                stop_loss REAL,
                take_profit_1 REAL,
                take_profit_2 REAL,
                take_profit_3 REAL,
                timeframe TEXT,
                reasoning TEXT,
                sent_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                user_confirmed BOOLEAN DEFAULT 0,
                trade_id INTEGER,
                FOREIGN KEY (trade_id) REFERENCES trades(id)
            )
        ''')
        
        # Create indexes for performance
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_trades_ticker ON trades(ticker)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_trades_status ON trades(status)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_trades_entry_date ON trades(entry_date)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_trades_strategy ON trades(strategy)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_signals_ticker ON signals(ticker)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_reminders_date ON trade_reminders(reminder_date)')
        
        conn.commit()
        conn.close()
        
        logger.info("Enhanced database tables created/verified")
    
    def _get_connection(self) -> sqlite3.Connection:
        """Get database connection with timeout"""
        conn = sqlite3.connect(self.db_path, timeout=10.0)
        conn.row_factory = sqlite3.Row
        return conn
    
    def save_signal(self, signal: Dict) -> int:
        """
        Save a signal to database
        
        Args:
            signal: Signal dictionary with all details
            
        Returns:
            Signal ID
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO signals (
                    ticker, action, strategy, confidence,
                    entry_price, stop_loss, 
                    take_profit_1, take_profit_2, take_profit_3,
                    timeframe, reasoning
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                signal['ticker'],
                signal['action'],
                signal.get('strategy', 'Unknown'),
                signal.get('confidence', 0),
                signal.get('entry_price'),
                signal.get('stop_loss'),
                signal.get('take_profit_1'),
                signal.get('take_profit_2'),
                signal.get('take_profit_3'),
                signal.get('timeframe', 'swing'),
                str(signal.get('reasoning', ''))
            ))
            
            signal_id = cursor.lastrowid
            conn.commit()
            
            logger.info(f"Signal saved: ID={signal_id}, {signal['action']} {signal['ticker']}")
            return signal_id
            
        except Exception as e:
            logger.error(f"Error saving signal: {e}")
            conn.rollback()
            return -1
        finally:
            conn.close()
    
    def create_trade_from_signal(self, signal_id: int, user_taken: bool = True) -> int:
        """
        Create a trade record from a signal
        
        Args:
            signal_id: ID of the signal
            user_taken: Whether user confirmed taking the trade
            
        Returns:
            Trade ID
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            # Get signal details
            cursor.execute('SELECT * FROM signals WHERE id = ?', (signal_id,))
            signal = dict(cursor.fetchone())
            
            # Calculate timeframe details
            timeframe_details = self._calculate_timeframe_details(signal.get('timeframe', 'swing'))
            
            # Create trade
            cursor.execute('''
                INSERT INTO trades (
                    signal_id, ticker, action, strategy, timeframe,
                    entry_price, entry_date, stop_loss,
                    take_profit_1, take_profit_2, take_profit_3,
                    confidence, status, user_taken,
                    recommended_hold_days, review_date, max_hold_date, exit_by_date
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                signal_id,
                signal['ticker'],
                signal['action'],
                signal['strategy'],
                signal.get('timeframe', 'swing'),
                signal['entry_price'],
                datetime.now(),
                signal.get('stop_loss'),
                signal.get('take_profit_1'),
                signal.get('take_profit_2'),
                signal.get('take_profit_3'),
                signal['confidence'],
                'open' if user_taken else 'skipped',
                user_taken,
                timeframe_details['hold_days'],
                timeframe_details['review_date'],
                timeframe_details['max_hold_date'],
                timeframe_details['exit_by_date']
            ))
            
            trade_id = cursor.lastrowid
            
            # Update signal with trade_id
            cursor.execute('UPDATE signals SET trade_id = ?, user_confirmed = ? WHERE id = ?',
                         (trade_id, user_taken, signal_id))
            
            # Create reminders if user took the trade
            if user_taken:
                self._create_trade_reminders(cursor, trade_id, timeframe_details)
            
            conn.commit()
            
            logger.info(f"Trade created: ID={trade_id}, {signal['action']} {signal['ticker']}")
            return trade_id
            
        except Exception as e:
            logger.error(f"Error creating trade from signal: {e}")
            conn.rollback()
            return -1
        finally:
            conn.close()
    
    def _calculate_timeframe_details(self, timeframe: str) -> Dict:
        """Calculate precise timeframe details based on strategy type"""
        now = datetime.now()
        
        timeframe_map = {
            'day': {'hold_days': 2, 'review_days': 1, 'max_days': 3},
            'swing': {'hold_days': 5, 'review_days': 3, 'max_days': 8},
            'position': {'hold_days': 21, 'review_days': 14, 'max_days': 30},
            'long': {'hold_days': 90, 'review_days': 60, 'max_days': 180}
        }
        
        details = timeframe_map.get(timeframe, timeframe_map['swing'])
        
        return {
            'hold_days': details['hold_days'],
            'review_date': (now + timedelta(days=details['review_days'])).date(),
            'max_hold_date': (now + timedelta(days=details['max_days'])).date(),
            'exit_by_date': (now + timedelta(days=details['max_days'] + 1)).date()
        }
    
    def _create_trade_reminders(self, cursor, trade_id: int, timeframe_details: Dict):
        """Create reminder schedule for a trade"""
        reminders = [
            {
                'type': 'review',
                'date': timeframe_details['review_date'],
                'message': 'Time to review your trade progress'
            },
            {
                'type': 'max_hold',
                'date': timeframe_details['max_hold_date'],
                'message': 'Consider trailing stop or exit'
            },
            {
                'type': 'exit_warning',
                'date': timeframe_details['exit_by_date'],
                'message': 'Exit if no target hit'
            }
        ]
        
        for reminder in reminders:
            cursor.execute('''
                INSERT INTO trade_reminders (trade_id, reminder_type, reminder_date, message)
                VALUES (?, ?, ?, ?)
            ''', (trade_id, reminder['type'], reminder['date'], reminder['message']))
    
    def add_trade_feedback(self, trade_id: int, feedback_type: str, 
                          feedback_value: str = None, notes: str = None) -> bool:
        """
        Add feedback for a trade
        
        Args:
            trade_id: Trade ID
            feedback_type: 'taken', 'skipped', 'tp1_hit', 'tp2_hit', 'tp3_hit', 'stop_loss', 'manual_exit'
            feedback_value: Additional value (e.g., exit price)
            notes: User notes
            
        Returns:
            Success status
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO trade_feedback (trade_id, feedback_type, feedback_value, notes)
                VALUES (?, ?, ?, ?)
            ''', (trade_id, feedback_type, feedback_value, notes))
            
            # Update trade status based on feedback
            if feedback_type == 'skipped':
                cursor.execute('UPDATE trades SET status = ?, user_taken = 0 WHERE id = ?',
                             ('skipped', trade_id))
            elif feedback_type in ['tp1_hit', 'tp2_hit', 'tp3_hit', 'stop_loss', 'manual_exit']:
                cursor.execute('UPDATE trades SET status = ? WHERE id = ?',
                             ('closed', trade_id))
            
            conn.commit()
            return True
            
        except Exception as e:
            logger.error(f"Error adding trade feedback: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()
    
    def close_trade(self, trade_id: int, exit_price: float, exit_reason: str, 
                   pnl: float = None, notes: str = None) -> bool:
        """
        Close a trade with outcome
        
        Args:
            trade_id: Trade ID
            exit_price: Exit price
            exit_reason: Reason for exit
            pnl: Profit/Loss amount
            notes: Additional notes
            
        Returns:
            Success status
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            # Get trade details
            cursor.execute('SELECT * FROM trades WHERE id = ?', (trade_id,))
            trade = dict(cursor.fetchone())
            
            # Calculate P&L if not provided
            if pnl is None and trade['entry_price']:
                if trade['action'] == 'BUY':
                    pnl_percent = ((exit_price - trade['entry_price']) / trade['entry_price']) * 100
                else:
                    pnl_percent = ((trade['entry_price'] - exit_price) / trade['entry_price']) * 100
            else:
                pnl_percent = pnl
            
            # Calculate hold days
            entry_date = datetime.fromisoformat(trade['entry_date'])
            hold_days = (datetime.now() - entry_date).days
            
            # Update trade
            cursor.execute('''
                UPDATE trades
                SET status = 'closed',
                    exit_date = ?,
                    exit_price = ?,
                    exit_reason = ?,
                    pnl_percent = ?,
                    hold_days = ?,
                    user_notes = ?,
                    updated_at = ?
                WHERE id = ?
            ''', (datetime.now(), exit_price, exit_reason, pnl_percent, 
                  hold_days, notes, datetime.now(), trade_id))
            
            # Add feedback
            self.add_trade_feedback(trade_id, exit_reason, str(exit_price), notes)
            
            # Update strategy performance
            self._update_strategy_performance(trade['strategy'], pnl_percent > 0)
            
            conn.commit()
            
            logger.info(f"Trade closed: ID={trade_id}, P&L={pnl_percent:.2f}%")
            return True
            
        except Exception as e:
            logger.error(f"Error closing trade {trade_id}: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()
    
    def _update_strategy_performance(self, strategy: str, is_win: bool):
        """Update strategy performance metrics"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            # Check if strategy exists
            cursor.execute('SELECT * FROM strategy_performance WHERE strategy = ? AND period = ?',
                         (strategy, 'all_time'))
            row = cursor.fetchone()
            
            if row:
                perf = dict(row)
                signals_taken = perf['signals_taken'] + 1
                wins = (perf['win_rate'] * perf['signals_taken'] / 100) + (1 if is_win else 0)
                win_rate = (wins / signals_taken) * 100
                
                cursor.execute('''
                    UPDATE strategy_performance
                    SET signals_taken = ?,
                        win_rate = ?,
                        updated_at = ?
                    WHERE strategy = ? AND period = ?
                ''', (signals_taken, win_rate, datetime.now(), strategy, 'all_time'))
            else:
                cursor.execute('''
                    INSERT INTO strategy_performance (strategy, period, signals_taken, win_rate)
                    VALUES (?, ?, ?, ?)
                ''', (strategy, 'all_time', 1, 100.0 if is_win else 0.0))
            
            conn.commit()
            
        except Exception as e:
            logger.error(f"Error updating strategy performance: {e}")
            conn.rollback()
        finally:
            conn.close()
    
    def get_open_trades(self) -> List[Dict]:
        """Get all open trades"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT * FROM trades
                WHERE status = 'open'
                ORDER BY entry_date DESC
            ''')
            
            trades = [dict(row) for row in cursor.fetchall()]
            return trades
            
        except Exception as e:
            logger.error(f"Error getting open trades: {e}")
            return []
        finally:
            conn.close()
    
    def get_pending_reminders(self) -> List[Dict]:
        """Get reminders that need to be sent today"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            today = datetime.now().date()
            cursor.execute('''
                SELECT r.*, t.ticker, t.action, t.entry_price, t.strategy
                FROM trade_reminders r
                JOIN trades t ON r.trade_id = t.id
                WHERE r.reminder_date <= ? AND r.sent = 0 AND t.status = 'open'
                ORDER BY r.reminder_date
            ''', (today,))
            
            reminders = [dict(row) for row in cursor.fetchall()]
            return reminders
            
        except Exception as e:
            logger.error(f"Error getting pending reminders: {e}")
            return []
        finally:
            conn.close()
    
    def mark_reminder_sent(self, reminder_id: int) -> bool:
        """Mark a reminder as sent"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                UPDATE trade_reminders
                SET sent = 1, sent_at = ?
                WHERE id = ?
            ''', (datetime.now(), reminder_id))
            
            conn.commit()
            return True
            
        except Exception as e:
            logger.error(f"Error marking reminder sent: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()
    
    def get_performance_stats(self, period: str = 'all_time') -> Dict:
        """
        Get performance statistics
        
        Args:
            period: 'all_time', 'month', 'week'
            
        Returns:
            Performance statistics dictionary
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            # Date filter
            date_filter = ""
            if period == 'week':
                date_filter = f"AND entry_date >= date('now', '-7 days')"
            elif period == 'month':
                date_filter = f"AND entry_date >= date('now', '-30 days')"
            
            # Total trades
            cursor.execute(f"SELECT COUNT(*) as total FROM trades WHERE status = 'closed' {date_filter}")
            total_trades = cursor.fetchone()['total']
            
            # Winning trades
            cursor.execute(f"SELECT COUNT(*) as wins FROM trades WHERE status = 'closed' AND pnl_percent > 0 {date_filter}")
            winning_trades = cursor.fetchone()['wins']
            
            # Losing trades
            cursor.execute(f"SELECT COUNT(*) as losses FROM trades WHERE status = 'closed' AND pnl_percent < 0 {date_filter}")
            losing_trades = cursor.fetchone()['losses']
            
            # Total P&L
            cursor.execute(f"SELECT SUM(pnl_percent) as total_pnl FROM trades WHERE status = 'closed' {date_filter}")
            total_pnl = cursor.fetchone()['total_pnl'] or 0
            
            # Average profit
            cursor.execute(f"SELECT AVG(pnl_percent) as avg_profit FROM trades WHERE status = 'closed' AND pnl_percent > 0 {date_filter}")
            avg_profit = cursor.fetchone()['avg_profit'] or 0
            
            # Average loss
            cursor.execute(f"SELECT AVG(pnl_percent) as avg_loss FROM trades WHERE status = 'closed' AND pnl_percent < 0 {date_filter}")
            avg_loss = cursor.fetchone()['avg_loss'] or 0
            
            # Win rate
            win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
            
            # Profit factor
            total_wins = winning_trades * abs(avg_profit) if avg_profit else 0
            total_losses = losing_trades * abs(avg_loss) if avg_loss else 0
            profit_factor = (total_wins / total_losses) if total_losses > 0 else 0
            
            # Open trades
            cursor.execute("SELECT COUNT(*) as open FROM trades WHERE status = 'open'")
            open_trades = cursor.fetchone()['open']
            
            return {
                'total_trades': total_trades,
                'winning_trades': winning_trades,
                'losing_trades': losing_trades,
                'open_trades': open_trades,
                'win_rate': round(win_rate, 1),
                'total_pnl': round(total_pnl, 2),
                'avg_profit': round(avg_profit, 2),
                'avg_loss': round(avg_loss, 2),
                'profit_factor': round(profit_factor, 2)
            }
            
        except Exception as e:
            logger.error(f"Error getting performance stats: {e}")
            return {}
        finally:
            conn.close()
    
    def get_strategy_performance(self) -> List[Dict]:
        """Get performance breakdown by strategy"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT 
                    strategy,
                    COUNT(*) as total_trades,
                    SUM(CASE WHEN pnl_percent > 0 THEN 1 ELSE 0 END) as wins,
                    SUM(CASE WHEN pnl_percent < 0 THEN 1 ELSE 0 END) as losses,
                    AVG(pnl_percent) as avg_pnl,
                    SUM(pnl_percent) as total_pnl
                FROM trades
                WHERE status = 'closed'
                GROUP BY strategy
                ORDER BY total_pnl DESC
            ''')
            
            strategies = []
            for row in cursor.fetchall():
                row_dict = dict(row)
                win_rate = (row_dict['wins'] / row_dict['total_trades'] * 100) if row_dict['total_trades'] > 0 else 0
                strategies.append({
                    'strategy': row_dict['strategy'],
                    'total_trades': row_dict['total_trades'],
                    'win_rate': round(win_rate, 1),
                    'avg_pnl': round(row_dict['avg_pnl'], 2),
                    'total_pnl': round(row_dict['total_pnl'], 2)
                })
            
            return strategies
            
        except Exception as e:
            logger.error(f"Error getting strategy performance: {e}")
            return []
        finally:
            conn.close()
    
    def get_trade_by_id(self, trade_id: int) -> Optional[Dict]:
        """Get trade details by ID"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('SELECT * FROM trades WHERE id = ?', (trade_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
            
        except Exception as e:
            logger.error(f"Error getting trade {trade_id}: {e}")
            return None
        finally:
            conn.close()
