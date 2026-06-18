"""
StockPilot - Main Entry Point
"""
import asyncio
import sys
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.utils.logger import setup_logger
from src.utils.config import get_config
from src.data.fetcher import MarketDataFetcher
from src.analysis.technical import TechnicalAnalysis
from src.notifications.telegram_bot import create_bot
from src.engine.signals import SignalGenerator
from src.scheduler import SignalScheduler


logger = setup_logger("stockpilot")


class StockPilot:
    """Main StockPilot application"""
    
    def __init__(self):
        """Initialize StockPilot"""
        logger.info("=" * 60)
        logger.info("STOCKPILOT - Automated Stock Trading Signal Bot")
        logger.info("=" * 60)
        
        # Load configuration
        try:
            self.config = get_config("stockpilot/config")
        except FileNotFoundError:
            # Try alternative path
            self.config = get_config("config")
        
        # Initialize components
        self.data_fetcher = MarketDataFetcher()
        self.technical_analysis = TechnicalAnalysis()
        self.telegram_bot = None
        self.signal_generator = SignalGenerator()
        self.scheduler = None
        
        # Load watchlist
        self.watchlist = self.config.load_watchlist()
        logger.info(f"Loaded {len(self.watchlist)} stocks in watchlist")
        
    async def initialize_telegram(self):
        """Initialize Telegram bot"""
        try:
            telegram_config = self.config.get_telegram_config()
            
            if not telegram_config.get('enabled', False):
                logger.warning("Telegram bot is disabled in config")
                return
            
            bot_token = telegram_config.get('bot_token')
            chat_id = telegram_config.get('chat_id')
            
            if not bot_token or not chat_id:
                logger.warning("Telegram bot token or chat_id not configured")
                logger.info("Please add your Telegram bot token and chat_id to config/settings.yaml")
                return
            
            self.telegram_bot = create_bot(bot_token, chat_id)
            await self.telegram_bot.initialize()
            
            # Start polling for commands
            await self.telegram_bot.start_polling()
            
            
            logger.info("Telegram bot initialized and ready")
            
        except Exception as e:
            logger.error(f"Failed to initialize Telegram bot: {e}")
            logger.info("Bot will continue without Telegram notifications")
    
    async def test_data_fetch(self):
        """Test data fetching for watchlist stocks"""
        logger.info("\nTesting data fetch for watchlist stocks...")
        logger.info("-" * 60)
        
        for stock in self.watchlist[:3]:  # Test first 3 stocks
            ticker = stock['ticker']
            logger.info(f"\nFetching data for {ticker} ({stock['name']})...")
            
            # Get current price
            price = self.data_fetcher.get_current_price(ticker)
            if price:
                logger.info(f"  Current price: ${price:.2f}")
            
            # Get OHLCV data
            df = self.data_fetcher.fetch_ohlcv(ticker, period='5d', interval='1h')
            if df is not None and not df.empty:
                logger.info(f"  Fetched {len(df)} candles")
                logger.info(f"  Latest close: ${df['Close'].iloc[-1]:.2f}")
                
                # Calculate indicators
                indicators = self.technical_analysis.calculate_all_indicators(df)
                latest = self.technical_analysis.get_latest_values(indicators)
                
                logger.info(f"  RSI: {latest.get('RSI', 0):.2f}")
                logger.info(f"  MACD: {latest.get('MACD', 0):.4f}")
                logger.info(f"  EMA 20: ${latest.get('EMA_20', 0):.2f}")
            else:
                logger.warning(f"  Failed to fetch data for {ticker}")
        
        logger.info("\n" + "-" * 60)
        logger.info("Data fetch test completed")
    
    async def scan_and_send_signals(self):
        """Scan watchlist for trading signals and send via Telegram"""
        logger.info("\nInitial scan of watchlist...")
        logger.info("-" * 60)
        
        # Get watchlist tickers
        tickers = [stock['ticker'] for stock in self.watchlist]
        
        # Scan for signals
        signals = self.signal_generator.scan_for_signals(tickers)
        
        if signals:
            logger.info(f"Found {len(signals)} signal(s)!")
            
            for signal in signals:
                logger.info(f"\nSignal: {signal['action']} {signal['ticker']} at {signal['confidence']}%")
                
                # Send via Telegram if available
                if self.telegram_bot:
                    await self.telegram_bot.send_signal(signal)
                    logger.info("Signal sent to Telegram")
        else:
            logger.info(f"No signals found meeting {self.config.get('signals.min_confidence', 85)}% confidence threshold")
        
        logger.info("-" * 60)
    
    async def run(self):
        """Run the bot"""
        try:
            # Initialize Telegram
            await self.initialize_telegram()
            
            # Test data fetching
            await self.test_data_fetch()
            
            # Initial scan for signals
            await self.scan_and_send_signals()
            
            logger.info("\n" + "=" * 60)
            logger.info("Initial Scan Complete - Starting Scheduler")
            logger.info("=" * 60)
            
            # Initialize and start scheduler
            if self.telegram_bot:
                self.scheduler = SignalScheduler(
                    self.signal_generator,
                    self.telegram_bot,
                    self.watchlist
                )
                self.scheduler.start()
                
                logger.info("\n" + "=" * 60)
                logger.info("✅ StockPilot is now running!")
                logger.info("=" * 60)
                logger.info(f"\n🎯 Min Confidence: {self.config.get('signals.min_confidence', 85)}%")
                logger.info(f"📊 Monitoring: {len(self.watchlist)} stocks")
                logger.info(f"⏰ Scanning: Every 15 minutes (market hours)")
                logger.info(f"📱 Telegram: Active")
                logger.info("\nPress Ctrl+C to stop")
                logger.info("=" * 60)
                
                # Keep running forever
                while True:
                    await asyncio.sleep(60)
            else:
                logger.warning("Telegram bot not initialized - scheduler not started")
                logger.info("Please configure Telegram credentials in config/settings.yaml")
                
        except KeyboardInterrupt:
            logger.info("\nShutting down StockPilot...")
            if self.scheduler:
                self.scheduler.stop()
            if self.telegram_bot:
                await self.telegram_bot.stop_polling()
        except Exception as e:
            logger.error(f"Error in main loop: {e}", exc_info=True)
            if self.scheduler:
                self.scheduler.stop()
            if self.telegram_bot:
                await self.telegram_bot.stop_polling()
        finally:
            logger.info("StockPilot stopped")


def main():
    """Main entry point"""
    try:
        bot = StockPilot()
        asyncio.run(bot.run())
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
