"""
Reminder Scheduler for Phase 4A
Checks for pending trade reminders and sends them
"""
import asyncio
from datetime import datetime
from ..engine.trade_database_v2 import TradeDatabaseV2
from ..notifications.signal_formatter import SignalFormatter
from ..data.fetcher import MarketDataFetcher
from ..utils.logger import setup_logger


logger = setup_logger(__name__)


class ReminderScheduler:
    """
    Scheduler for trade reminders
    
    Checks daily for pending reminders and sends them via Telegram
    """
    
    def __init__(self, telegram_bot):
        """
        Initialize reminder scheduler
        
        Args:
            telegram_bot: TelegramBot instance for sending messages
        """
        self.db = TradeDatabaseV2()
        self.formatter = SignalFormatter()
        self.fetcher = MarketDataFetcher()
        self.telegram_bot = telegram_bot
    
    async def check_and_send_reminders(self):
        """Check for pending reminders and send them"""
        try:
            # Get pending reminders
            reminders = self.db.get_pending_reminders()
            
            if not reminders:
                logger.info("No pending reminders to send")
                return
            
            logger.info(f"Found {len(reminders)} pending reminders")
            
            for reminder in reminders:
                try:
                    await self._send_reminder(reminder)
                    
                    # Mark as sent
                    self.db.mark_reminder_sent(reminder['id'])
                    
                    # Small delay between reminders
                    await asyncio.sleep(1)
                    
                except Exception as e:
                    logger.error(f"Error sending reminder {reminder['id']}: {e}")
                    continue
            
            logger.info(f"Successfully sent {len(reminders)} reminders")
            
        except Exception as e:
            logger.error(f"Error checking reminders: {e}")
    
    async def _send_reminder(self, reminder: dict):
        """Send a single reminder"""
        try:
            ticker = reminder['ticker']
            trade_id = reminder['trade_id']
            reminder_type = reminder['reminder_type']
            
            # Get current price
            try:
                df = self.fetcher.fetch_ohlcv(ticker, period='1d', interval='1d')
                current_price = float(df['Close'].iloc[-1]) if df is not None and len(df) > 0 else None
            except:
                current_price = None
            
            # Get trade details
            trade = self.db.get_trade_by_id(trade_id)
            
            if not trade:
                logger.warning(f"Trade {trade_id} not found for reminder")
                return
            
            # Skip if trade is closed
            if trade['status'] != 'open':
                logger.info(f"Trade {trade_id} is closed, skipping reminder")
                return
            
            # Format reminder message
            message = self.formatter.format_reminder(trade, reminder_type, current_price)
            
            # Send via Telegram
            await self.telegram_bot.send_message(message, parse_mode='HTML')
            
            logger.info(f"Sent {reminder_type} reminder for trade #{trade_id} ({ticker})")
            
        except Exception as e:
            logger.error(f"Error sending reminder: {e}")
            raise
