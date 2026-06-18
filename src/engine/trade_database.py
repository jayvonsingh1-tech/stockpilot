"""
Trade Tracking Database - SQLite database for tracking trades
Optimized for performance and reliability
"""
import sqlite3
from typing import Dict, List, Optional
from datetime import datetime
from pathlib import Path
from ..utils.logger import setup_logger


logger = setup_logger(__name__)


class TradeDatabase:
    """
    SQLite database for trade tracking
    
    Features:
    - Track all trades (entry, exit, P&L)
    - Daily price updates
    - Position management
    - Performance analytics
    - Trading journal
    """
    
    def __init__(self, db_path: str = "data/trades.db"):
        """Initialize database connection"""
        self.db_path = db_path
        
        # Create data directory if needed
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        
        # Initialize database
        self._init_database()
        
        logger.info(f"Trade database initialized: {db_path}")
    
    def _init_database(self):
        """Create database tables if they don't exist"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Trades table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS trades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                signal_id TEXT,
                ticker TEXT NOT NULL,
                action TEXT NOT NULL,
                strategy TEXT,
                trading_type TEXT DEFAULT 'CFD',
                
                -- Entry
                entry_date DATETIME NOT NULL,
                entry_price REAL NOT NULL,
                shares INTEGER NOT NULL,
                total_investment REAL NOT NULL,
                
                -- Risk Management
                stop_loss REAL,
                target_price REAL,
                fair_value REAL,
                
                -- Status
                status TEXT DEFAULT 'OPEN',
                current_price REAL,
                unrealized_pnl REAL DEFAULT 0,
                realized_pnl REAL DEFAULT 0,
                
                -- Tracking
                last_checked DATETIME,
                days_held INTEGER DEFAULT 0,
                
                -- Exit
                exit_date DATETIME,
                exit_price REAL,
                exit_reason TEXT,
                
                -- Metadata
                notes TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Daily updates table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS trade_updates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                trade_id INTEGER NOT NULL,
                date DATE NOT NULL,
                price REAL NOT NULL,
                pnl REAL NOT NULL,
                pnl_percent REAL NOT NULL,
                message_sent BOOLEAN DEFAULT 0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (trade_id) REFERENCES trades(id)
            )
        ''')
        
        # Signals table (for reference)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS signals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ticker TEXT NOT NULL,
                action TEXT NOT NULL,
                strategy TEXT,
                confidence INTEGER,
                entry_price REAL,
                stop_loss REAL,
                target_price REAL,
                reasoning TEXT,
                sent_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                user_confirmed BOOLEAN DEFAULT 0
            )
        ''')
        
        # Performance metrics table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS performance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date DATE NOT NULL UNIQUE,
                total_trades INTEGER DEFAULT 0,
                winning_trades INTEGER DEFAULT 0,
                losing_trades INTEGER DEFAULT 0,
                total_pnl REAL DEFAULT 0,
                win_rate REAL DEFAULT 0,
                avg_profit REAL DEFAULT 0,
                avg_loss REAL DEFAULT 0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
        
        logger.info("Database tables created/verified")
    
    def _get_connection(self) -> sqlite3.Connection:
        """Get database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Return rows as dictionaries
        return conn
    
    def create_trade(self, signal: Dict, shares: int) -> int:
        """
        Create a new trade record
        
        Args:
            signal: Signal dictionary
            shares: Number of shares
            
        Returns:
            Trade ID
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO trades (
                    ticker, action, strategy, trading_type,
                    entry_date, entry_price, shares, total_investment,
                    stop_loss, target_price, fair_value,
                    status, current_price
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                signal['ticker'],
                signal['action'],
                signal.get('strategy', 'Unknown'),
                signal.get('trading_type', 'CFD'),
                datetime.now(),
                signal['entry_price'],
                shares,
                signal['entry_price'] * shares,
                signal.get('stop_loss'),
                signal.get('target_price', signal.get('take_profit_1')),
                signal.get('fair_value'),
                'OPEN',
                signal['entry_price']
            ))
            
            trade_id = cursor.lastrowid
            conn.commit()
            
            logger.info(f"Trade created: ID={trade_id}, {signal['action']} {shares} {signal['ticker']}")
            return trade_id
            
        except Exception as e:
            logger.error(f"Error creating trade: {e}")
            conn.rollback()
            return -1
        finally:
            conn.close()
    
    def get_open_trades(self) -> List[Dict]:
        """Get all open trades"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT * FROM trades
                WHERE status = 'OPEN'
                ORDER BY entry_date DESC
            ''')
            
            trades = [dict(row) for row in cursor.fetchall()]
            return trades
            
        except Exception as e:
            logger.error(f"Error getting open trades: {e}")
            return []
        finally:
            conn.close()
    
    def update_trade_price(self, trade_id: int, current_price: float) -> bool:
        """Update trade with current price and P&L"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            # Get trade details
            cursor.execute('SELECT * FROM trades WHERE id = ?', (trade_id,))
            trade = dict(cursor.fetchone())
            
            # Calculate P&L
            if trade['action'] == 'BUY':
                pnl = (current_price - trade['entry_price']) * trade['shares']
            else:
                pnl = (trade['entry_price'] - current_price) * trade['shares']
            
            pnl_percent = (pnl / trade['total_investment']) * 100
            
            # Calculate days held
            entry_date = datetime.fromisoformat(trade['entry_date'])
            days_held = (datetime.now() - entry_date).days
            
            # Update trade
            cursor.execute('''
                UPDATE trades
                SET current_price = ?,
                    unrealized_pnl = ?,
                    last_checked = ?,
                    days_held = ?,
                    updated_at = ?
                WHERE id = ?
            ''', (current_price, pnl, datetime.now(), days_held, datetime.now(), trade_id))
            
            # Add daily update record
            cursor.execute('''
                INSERT INTO trade_updates (trade_id, date, price, pnl, pnl_percent)
                VALUES (?, ?, ?, ?, ?)
            ''', (trade_id, datetime.now().date(), current_price, pnl, pnl_percent))
            
            conn.commit()
            return True
            
        except Exception as e:
            logger.error(f"Error updating trade {trade_id}: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()
    
    def close_trade(self, trade_id: int, exit_price: float, exit_reason: str = "Manual") -> bool:
        """Close a trade"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            # Get trade details
            cursor.execute('SELECT * FROM trades WHERE id = ?', (trade_id,))
            trade = dict(cursor.fetchone())
            
            # Calculate final P&L
            if trade['action'] == 'BUY':
                pnl = (exit_price - trade['entry_price']) * trade['shares']
            else:
                pnl = (trade['entry_price'] - exit_price) * trade['shares']
            
            # Update trade
            cursor.execute('''
                UPDATE trades
                SET status = 'CLOSED',
                    exit_date = ?,
                    exit_price = ?,
                    exit_reason = ?,
                    realized_pnl = ?,
                    updated_at = ?
                WHERE id = ?
            ''', (datetime.now(), exit_price, exit_reason, pnl, datetime.now(), trade_id))
            
            conn.commit()
            
            logger.info(f"Trade closed: ID={trade_id}, P&L=${pnl:.2f}")
            return True
            
        except Exception as e:
            logger.error(f"Error closing trade {trade_id}: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()
    
    def get_trade_by_ticker(self, ticker: str) -> Optional[Dict]:
        """Get most recent open trade for a ticker"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT * FROM trades
                WHERE ticker = ? AND status = 'OPEN'
                ORDER BY entry_date DESC
                LIMIT 1
            ''', (ticker,))
            
            row = cursor.fetchone()
            return dict(row) if row else None
            
        except Exception as e:
            logger.error(f"Error getting trade for {ticker}: {e}")
            return None
        finally:
            conn.close()
    
    def get_performance_stats(self) -> Dict:
        """Get overall performance statistics"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            # Total trades
            cursor.execute("SELECT COUNT(*) as total FROM trades WHERE status = 'CLOSED'")
            total_trades = cursor.fetchone()['total']
            
            # Winning trades
            cursor.execute("SELECT COUNT(*) as wins FROM trades WHERE status = 'CLOSED' AND realized_pnl > 0")
            winning_trades = cursor.fetchone()['wins']
            
            # Losing trades
            cursor.execute("SELECT COUNT(*) as losses FROM trades WHERE status = 'CLOSED' AND realized_pnl < 0")
            losing_trades = cursor.fetchone()['losses']
            
            # Total P&L
            cursor.execute("SELECT SUM(realized_pnl) as total_pnl FROM trades WHERE status = 'CLOSED'")
            total_pnl = cursor.fetchone()['total_pnl'] or 0
            
            # Average profit
            cursor.execute("SELECT AVG(realized_pnl) as avg_profit FROM trades WHERE status = 'CLOSED' AND realized_pnl > 0")
            avg_profit = cursor.fetchone()['avg_profit'] or 0
            
            # Average loss
            cursor.execute("SELECT AVG(realized_pnl) as avg_loss FROM trades WHERE status = 'CLOSED' AND realized_pnl < 0")
            avg_loss = cursor.fetchone()['avg_loss'] or 0
            
            # Win rate
            win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
            
            return {
                'total_trades': total_trades,
                'winning_trades': winning_trades,
                'losing_trades': losing_trades,
                'win_rate': round(win_rate, 1),
                'total_pnl': round(total_pnl, 2),
                'avg_profit': round(avg_profit, 2),
                'avg_loss': round(avg_loss, 2)
            }
            
        except Exception as e:
            logger.error(f"Error getting performance stats: {e}")
            return {}
        finally:
            conn.close()
    
    def save_signal(self, signal: Dict) -> int:
        """Save a signal to database"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO signals (
                    ticker, action, strategy, confidence,
                    entry_price, stop_loss, target_price, reasoning
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                signal['ticker'],
                signal['action'],
                signal.get('strategy', 'Unknown'),
                signal.get('confidence', 0),
                signal.get('entry_price'),
                signal.get('stop_loss'),
                signal.get('target_price', signal.get('take_profit_1')),
                str(signal.get('reasoning', ''))
            ))
            
            signal_id = cursor.lastrowid
            conn.commit()
            
            return signal_id
            
        except Exception as e:
            logger.error(f"Error saving signal: {e}")
            conn.rollback()
            return -1
        finally:
            conn.close()
