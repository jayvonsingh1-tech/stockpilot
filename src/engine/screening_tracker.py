"""
Screening Tracker - Persistent tracking of screened companies
Maintains history of top performers and ensures continuous monitoring
"""
import sqlite3
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from pathlib import Path
from ..utils.logger import setup_logger


logger = setup_logger(__name__)


class ScreeningTracker:
    """Track screening results and maintain historical top performers"""
    
    def __init__(self, db_path: str = "data/screening_history.db"):
        """
        Initialize screening tracker
        
        Args:
            db_path: Path to SQLite database
        """
        self.db_path = db_path
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self._init_database()
    
    def _init_database(self):
        """Initialize database tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Table for daily screening results
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS screening_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ticker TEXT NOT NULL,
                company_name TEXT,
                score REAL NOT NULL,
                rank INTEGER,
                screening_date DATE NOT NULL,
                sector TEXT,
                market TEXT,
                technical_score REAL,
                fundamental_score REAL,
                momentum_score REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(ticker, screening_date)
            )
        ''')
        
        # Table for top 10 tracking (persistent watchlist)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS top_performers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ticker TEXT NOT NULL UNIQUE,
                company_name TEXT,
                first_ranked_date DATE NOT NULL,
                last_seen_date DATE NOT NULL,
                best_score REAL,
                best_rank INTEGER,
                days_in_top10 INTEGER DEFAULT 1,
                current_status TEXT DEFAULT 'active',
                notes TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Table for research reports
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS research_reports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ticker TEXT NOT NULL,
                report_date DATE NOT NULL,
                overall_score REAL,
                recommendation TEXT,
                report_summary TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(ticker, report_date)
            )
        ''')
        
        # Table for user actions on screening results
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_screening_actions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ticker TEXT NOT NULL,
                action TEXT NOT NULL,
                action_date DATE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
        logger.info(f"Screening tracker database initialized: {self.db_path}")
    
    def save_screening_results(self, results: List[Dict], screening_date: Optional[str] = None):
        """
        Save daily screening results
        
        Args:
            results: List of screening results with scores
            screening_date: Date of screening (defaults to today)
        """
        if not screening_date:
            screening_date = datetime.now().strftime('%Y-%m-%d')
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for rank, result in enumerate(results, 1):
            try:
                cursor.execute('''
                    INSERT OR REPLACE INTO screening_results 
                    (ticker, company_name, score, rank, screening_date, sector, market,
                     technical_score, fundamental_score, momentum_score)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    result['ticker'],
                    result.get('name', ''),
                    result.get('total_score', 0),
                    rank,
                    screening_date,
                    result.get('sector', ''),
                    result.get('market', ''),
                    result.get('technical_score', 0),
                    result.get('fundamental_score', 0),
                    result.get('momentum_score', 0)
                ))
            except Exception as e:
                logger.error(f"Error saving screening result for {result.get('ticker')}: {e}")
        
        conn.commit()
        conn.close()
        logger.info(f"Saved {len(results)} screening results for {screening_date}")
    
    def update_top_performers(self, top_results: List[Dict]):
        """
        Update top 10 performers tracking
        
        Args:
            top_results: Top 10 screening results
        """
        today = datetime.now().strftime('%Y-%m-%d')
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for rank, result in enumerate(top_results[:10], 1):
            ticker = result['ticker']
            score = result.get('total_score', 0)
            
            # Check if ticker already exists
            cursor.execute('SELECT * FROM top_performers WHERE ticker = ?', (ticker,))
            existing = cursor.fetchone()
            
            if existing:
                # Update existing record
                cursor.execute('''
                    UPDATE top_performers 
                    SET last_seen_date = ?,
                        best_score = MAX(best_score, ?),
                        best_rank = MIN(best_rank, ?),
                        days_in_top10 = days_in_top10 + 1,
                        current_status = 'active',
                        updated_at = CURRENT_TIMESTAMP
                    WHERE ticker = ?
                ''', (today, score, rank, ticker))
            else:
                # Insert new record
                cursor.execute('''
                    INSERT INTO top_performers 
                    (ticker, company_name, first_ranked_date, last_seen_date, 
                     best_score, best_rank, current_status)
                    VALUES (?, ?, ?, ?, ?, ?, 'active')
                ''', (
                    ticker,
                    result.get('name', ''),
                    today,
                    today,
                    score,
                    rank
                ))
        
        # Mark stocks that dropped out of top 10 as 'monitoring'
        top_tickers = [r['ticker'] for r in top_results[:10]]
        placeholders = ','.join('?' * len(top_tickers))
        cursor.execute(f'''
            UPDATE top_performers 
            SET current_status = 'monitoring'
            WHERE ticker NOT IN ({placeholders})
            AND current_status = 'active'
            AND last_seen_date < ?
        ''', (*top_tickers, today))
        
        conn.commit()
        conn.close()
        logger.info(f"Updated top performers tracking for {len(top_results)} stocks")
    
    def get_active_top_performers(self) -> List[Dict]:
        """
        Get currently active top 10 performers
        
        Returns:
            List of active top performers
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM top_performers 
            WHERE current_status = 'active'
            ORDER BY best_rank ASC, best_score DESC
            LIMIT 10
        ''')
        
        results = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return results
    
    def get_monitoring_list(self, days: int = 30) -> List[Dict]:
        """
        Get stocks being monitored (dropped from top 10 but still tracked)
        
        Args:
            days: Number of days to look back
            
        Returns:
            List of stocks being monitored
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cutoff_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
        
        cursor.execute('''
            SELECT * FROM top_performers 
            WHERE current_status = 'monitoring'
            AND last_seen_date >= ?
            ORDER BY last_seen_date DESC, best_score DESC
        ''', (cutoff_date,))
        
        results = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return results
    
    def get_combined_watchlist(self) -> List[str]:
        """
        Get combined list of tickers to monitor (active + monitoring)
        
        Returns:
            List of ticker symbols
        """
        active = self.get_active_top_performers()
        monitoring = self.get_monitoring_list()
        
        tickers = [stock['ticker'] for stock in active]
        tickers.extend([stock['ticker'] for stock in monitoring])
        
        return list(set(tickers))  # Remove duplicates
    
    def save_research_report(self, ticker: str, report: Dict):
        """
        Save research report for a stock
        
        Args:
            ticker: Stock ticker
            report: Research report data
        """
        today = datetime.now().strftime('%Y-%m-%d')
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT OR REPLACE INTO research_reports 
                (ticker, report_date, overall_score, recommendation, report_summary)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                ticker,
                today,
                report.get('overall_score', 0),
                report.get('bot_recommendation', ''),
                report.get('summary', '')
            ))
            conn.commit()
            logger.info(f"Saved research report for {ticker}")
        except Exception as e:
            logger.error(f"Error saving research report for {ticker}: {e}")
        finally:
            conn.close()
    
    def get_screening_history(self, ticker: str, days: int = 30) -> List[Dict]:
        """
        Get screening history for a specific ticker
        
        Args:
            ticker: Stock ticker
            days: Number of days to look back
            
        Returns:
            List of historical screening results
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cutoff_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
        
        cursor.execute('''
            SELECT * FROM screening_results 
            WHERE ticker = ? AND screening_date >= ?
            ORDER BY screening_date DESC
        ''', (ticker, cutoff_date))
        
        results = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return results
    
    def get_statistics(self) -> Dict:
        """
        Get screening statistics
        
        Returns:
            Dictionary with statistics
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Total unique stocks screened
        cursor.execute('SELECT COUNT(DISTINCT ticker) FROM screening_results')
        total_stocks = cursor.fetchone()[0]
        
        # Active top performers
        cursor.execute('SELECT COUNT(*) FROM top_performers WHERE current_status = "active"')
        active_count = cursor.fetchone()[0]
        
        # Monitoring list
        cursor.execute('SELECT COUNT(*) FROM top_performers WHERE current_status = "monitoring"')
        monitoring_count = cursor.fetchone()[0]
        
        # Total screening days
        cursor.execute('SELECT COUNT(DISTINCT screening_date) FROM screening_results')
        screening_days = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            'total_stocks_screened': total_stocks,
            'active_top_performers': active_count,
            'monitoring_list_size': monitoring_count,
            'total_screening_days': screening_days
        }
    
    def save_user_action(self, ticker: str, action: str):
        """
        Save user action on a screening result
        
        Args:
            ticker: Stock ticker
            action: Action taken (watchlist, bought, skipped)
        """
        today = datetime.now().strftime('%Y-%m-%d')
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO user_screening_actions
                (ticker, action, action_date)
                VALUES (?, ?, ?)
            ''', (ticker, action, today))
            conn.commit()
            logger.info(f"Saved user action: {action} for {ticker}")
        except Exception as e:
            logger.error(f"Error saving user action for {ticker}: {e}")
        finally:
            conn.close()
    
    def get_user_actions(self, ticker: Optional[str] = None, days: int = 30) -> List[Dict]:
        """
        Get user actions on screening results
        
        Args:
            ticker: Optional ticker to filter by
            days: Number of days to look back
            
        Returns:
            List of user actions
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cutoff_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
        
        if ticker:
            cursor.execute('''
                SELECT * FROM user_screening_actions
                WHERE ticker = ? AND action_date >= ?
                ORDER BY action_date DESC
            ''', (ticker, cutoff_date))
        else:
            cursor.execute('''
                SELECT * FROM user_screening_actions
                WHERE action_date >= ?
                ORDER BY action_date DESC
            ''', (cutoff_date,))
        
        results = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return results
    
    def get_watchlist_stocks(self) -> List[str]:
        """
        Get stocks user added to watchlist
        
        Returns:
            List of ticker symbols
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT DISTINCT ticker FROM user_screening_actions
            WHERE action = 'watchlist'
            ORDER BY action_date DESC
        ''')
        
        results = [row[0] for row in cursor.fetchall()]
        conn.close()
        
        return results
    
    def get_bought_stocks(self) -> List[str]:
        """
        Get stocks user bought
        
        Returns:
            List of ticker symbols
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT DISTINCT ticker FROM user_screening_actions
            WHERE action = 'bought'
            ORDER BY action_date DESC
        ''')
        
        results = [row[0] for row in cursor.fetchall()]
        conn.close()
        
        return results
