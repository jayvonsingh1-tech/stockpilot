"""
Scheduler - Manages scheduled tasks for signal scanning
"""
import asyncio
from datetime import datetime, time
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
import pytz
from .engine.signals import SignalGenerator
from .notifications.telegram_bot import TelegramBot
from .analysis.screener import StockScreener
from .analysis.research import ResearchReportGenerator
from .utils.logger import setup_logger
from .utils.config import get_config


logger = setup_logger(__name__)


class SignalScheduler:
    """Manages scheduled signal scanning"""
    
    def __init__(self, signal_generator: SignalGenerator, telegram_bot: TelegramBot, watchlist: list):
        """
        Initialize scheduler
        
        Args:
            signal_generator: SignalGenerator instance
            telegram_bot: TelegramBot instance
            watchlist: List of stocks to monitor
        """
        self.signal_generator = signal_generator
        self.telegram_bot = telegram_bot
        self.watchlist = watchlist
        self.config = get_config()
        # Set timezone to US Eastern Time for market hours
        self.timezone = pytz.timezone('America/New_York')
        self.scheduler = AsyncIOScheduler(timezone=self.timezone)
        self.stock_screener = StockScreener()
        self.research_generator = ResearchReportGenerator()
        
        # Market hours (adjust for your timezone)
        self.market_open = time(9, 30)  # 9:30 AM ET
        self.market_close = time(16, 0)  # 4:00 PM ET
        
    def start(self):
        """Start the scheduler"""
        logger.info("Starting signal scheduler...")
        logger.info(f"Scheduler timezone: {self.timezone}")
        
        # UK timezone for LSE
        uk_tz = pytz.timezone('Europe/London')
        
        # LSE Market Hours (8:00 AM - 4:30 PM UK)
        # Scan every 15 minutes during LSE hours
        self.scheduler.add_job(
            self._periodic_scan,
            CronTrigger(hour='8-16', minute='0,15,30,45', day_of_week='mon-fri', timezone=uk_tz),
            id='lse_scan',
            name='LSE 15-Minute Scan'
        )
        
        # US Market Hours (9:30 AM - 4:00 PM ET = 2:30 PM - 9:00 PM UK)
        # Schedule market open scan (9:30 AM ET)
        self.scheduler.add_job(
            self._market_open_scan,
            CronTrigger(hour=9, minute=30, day_of_week='mon-fri', timezone=self.timezone),
            id='us_market_open',
            name='US Market Open Scan'
        )
        
        # Schedule 15-minute scans during US market hours (9:30 AM - 4:00 PM ET)
        self.scheduler.add_job(
            self._periodic_scan,
            CronTrigger(hour='9-15', minute='0,15,30,45', day_of_week='mon-fri', timezone=self.timezone),
            id='us_periodic_scan',
            name='US 15-Minute Scan'
        )
        
        # US market close scan (4:00 PM ET)
        self.scheduler.add_job(
            self._market_close_scan,
            CronTrigger(hour=16, minute=0, day_of_week='mon-fri', timezone=self.timezone),
            id='us_market_close',
            name='US Market Close Scan'
        )
        
        # Schedule daily summary after all markets closed (4:30 PM ET)
        self.scheduler.add_job(
            self._send_daily_summary,
            CronTrigger(hour=16, minute=30, day_of_week='mon-fri', timezone=self.timezone),
            id='daily_summary',
            name='Daily Summary'
        )
        
        # Schedule weekly report (Sunday evening 6PM ET)
        self.scheduler.add_job(
            self._send_weekly_report,
            CronTrigger(day_of_week='sun', hour=18, minute=0, timezone=self.timezone),
            id='weekly_report',
            name='Weekly Report'
        )
        
        # Schedule daily stock screening (7:00 AM UK / 2:00 AM ET - before markets open)
        self.scheduler.add_job(
            self._run_daily_screening,
            CronTrigger(hour=7, minute=0, day_of_week='mon-fri', timezone=uk_tz),
            id='daily_screening',
            name='Daily Stock Screening'
        )
        
        self.scheduler.start()
        logger.info("Scheduler started successfully")
        logger.info("Scanning every 15 minutes during market hours")
        logger.info("Daily stock screening at 7:00 AM UK (before markets open)")
        logger.info("Daily summary at 9:30 PM UK (after all markets close)")
        logger.info(f"Next scan: {self._get_next_scan_time()}")
    
    def stop(self):
        """Stop the scheduler"""
        logger.info("Stopping scheduler...")
        self.scheduler.shutdown()
        logger.info("Scheduler stopped")
    
    async def _market_open_scan(self):
        """Scan at market open"""
        logger.info("=" * 60)
        logger.info("MARKET OPEN SCAN")
        logger.info("=" * 60)
        
        await self.telegram_bot.send_alert(
            "Market Open",
            "🔔 Markets are now open. Starting signal scan...",
            "INFO"
        )
        
        await self._scan_and_send_signals("Market Open")
    
    async def _periodic_scan(self):
        """15-minute scan during market hours"""
        logger.info("=" * 60)
        logger.info("15-MINUTE SCAN")
        logger.info("=" * 60)
        
        await self._scan_and_send_signals("15-Minute")
    
    async def _market_close_scan(self):
        """Scan at market close"""
        logger.info("=" * 60)
        logger.info("MARKET CLOSE SCAN")
        logger.info("=" * 60)
        
        await self._scan_and_send_signals("Market Close")
        
        await self.telegram_bot.send_alert(
            "Market Close",
            "🔔 Markets are now closed. Final scan complete.",
            "INFO"
        )
    
    async def _scan_and_send_signals(self, scan_type: str):
        """
        Scan watchlist and send signals
        
        Args:
            scan_type: Type of scan (e.g., "Market Open", "Hourly")
        """
        try:
            logger.info(f"Starting {scan_type} scan of {len(self.watchlist)} stocks...")
            
            # Get tickers
            tickers = [stock['ticker'] for stock in self.watchlist]
            
            # Scan for signals
            signals = self.signal_generator.scan_for_signals(tickers)
            
            if signals:
                logger.info(f"Found {len(signals)} signal(s) in {scan_type} scan")
                
                for signal in signals:
                    # Send via Telegram
                    await self.telegram_bot.send_signal(signal)
                    logger.info(f"Signal sent: {signal['action']} {signal['ticker']}")
                    
                    # Small delay between signals
                    await asyncio.sleep(1)
            else:
                logger.info(f"No signals found in {scan_type} scan")
                
        except Exception as e:
            logger.error(f"Error in {scan_type} scan: {e}", exc_info=True)
            await self.telegram_bot.send_alert(
                "Scan Error",
                f"Error during {scan_type} scan: {str(e)}",
                "ERROR"
            )
    
    async def _send_daily_summary(self):
        """Send daily summary"""
        logger.info("Sending daily summary...")
        
        try:
            # Get portfolio summary
            portfolio = self.signal_generator.risk_manager.get_portfolio_summary()
            
            summary = f"""
📊 **Daily Summary** - {datetime.now().strftime('%Y-%m-%d')}

💰 **Portfolio**
• Capital: ${portfolio['current_capital']:,.2f}
• Daily P&L: ${portfolio['daily_pnl']:,.2f} ({portfolio['daily_pnl_percent']:.2f}%)
• Total P&L: ${portfolio['total_pnl']:,.2f} ({portfolio['total_pnl_percent']:.2f}%)

📈 **Positions**
• Open: {portfolio['open_positions']}
• Available Slots: {portfolio['available_slots']}

⚙️ **Settings**
• Min Confidence: {self.config.get('signals.min_confidence', 80)}%
• Risk per Trade: {portfolio['risk_per_trade_percent']:.1f}%
"""
            
            await self.telegram_bot.send_message(summary)
            logger.info("Daily summary sent")
            
        except Exception as e:
            logger.error(f"Error sending daily summary: {e}", exc_info=True)
    
    async def _send_weekly_report(self):
        """Send weekly performance report"""
        logger.info("Sending weekly report...")
        
        try:
            portfolio = self.signal_generator.risk_manager.get_portfolio_summary()
            
            report = f"""
📈 **Weekly Report** - Week of {datetime.now().strftime('%Y-%m-%d')}

💰 **Performance**
• Starting Capital: ${self.signal_generator.risk_manager.initial_capital:,.2f}
• Current Capital: ${portfolio['current_capital']:,.2f}
• Weekly Return: {portfolio['total_pnl_percent']:.2f}%

📊 **Trading Activity**
• Signals Generated: TBD
• Trades Taken: TBD
• Win Rate: TBD

🎯 **Next Week Goals**
• Continue monitoring watchlist
• Target: 5% weekly return
• Maintain 80%+ confidence threshold

Have a great week! 🚀
"""
            
            await self.telegram_bot.send_message(report)
            logger.info("Weekly report sent")
            
        except Exception as e:
            logger.error(f"Error sending weekly report: {e}", exc_info=True)
    
    def _get_next_scan_time(self) -> str:
        """Get next scheduled scan time"""
        jobs = self.scheduler.get_jobs()
        if jobs:
            next_job = min(jobs, key=lambda j: j.next_run_time)
            return next_job.next_run_time.strftime('%Y-%m-%d %H:%M:%S')
        return "No scans scheduled"
    
    async def manual_scan(self):
        """Trigger a manual scan"""
        logger.info("Manual scan triggered")
        await self._scan_and_send_signals("Manual")
    
    async def _run_daily_screening(self):
        """Run enhanced daily stock screening with persistent tracking"""
        logger.info("=" * 60)
        logger.info("DAILY STOCK SCREENING - ENHANCED")
        logger.info("=" * 60)
        
        try:
            await self.telegram_bot.send_alert(
                "Daily Screening",
                "🔍 Starting enhanced daily stock screening (180+ stocks)...\n"
                "This will take a few minutes.",
                "INFO"
            )
            
            # Run enhanced screening (screens 180+ stocks, researches top 5)
            screening_results = self.stock_screener.screen_daily(max_results=20, research_top=5)
            
            if screening_results['new_opportunities']:
                logger.info(f"Found {screening_results['total_screened']} candidates")
                logger.info(f"Researching top {len(screening_results['new_opportunities'])} stocks")
                
                # Send overview of top 20
                await self.telegram_bot.send_screening_results(screening_results['top_20'])
                
                await asyncio.sleep(2)
                
                # Send tracking summary
                tracking_msg = f"""
📊 **Tracking Summary**

🎯 **Active Top 10** (Continuously Monitored):
{self._format_tracked_stocks(screening_results['active_top_10'])}

👀 **Monitoring List** (Recently Dropped):
{self._format_tracked_stocks(screening_results['monitoring'][:5])}

📈 **Statistics**:
• Total stocks screened today: {screening_results['total_screened']}
• Unique stocks tracked: {screening_results['statistics']['total_stocks_screened']}
• Days of screening data: {screening_results['statistics']['total_screening_days']}
"""
                await self.telegram_bot.send_message(tracking_msg)
                
                await asyncio.sleep(2)
                
                # Generate detailed research reports for top 5 new opportunities
                for i, stock in enumerate(screening_results['new_opportunities'], 1):
                    if stock['total_score'] >= 70:  # Only research high-scoring stocks
                        ticker = stock['ticker']
                        logger.info(f"Generating detailed report {i}/5 for: {ticker}")
                        
                        try:
                            report = self.research_generator.generate_report(ticker)
                            if report:
                                # Save report to tracking database
                                self.stock_screener.tracker.save_research_report(ticker, report)
                                
                                await asyncio.sleep(3)  # Delay between reports
                                await self.telegram_bot.send_research_report(report)
                        except Exception as e:
                            logger.error(f"Error generating report for {ticker}: {e}")
                            continue
                
                logger.info("Daily screening and research complete")
                
            else:
                logger.info("No candidates found meeting criteria")
                await self.telegram_bot.send_screening_results([])
                
        except Exception as e:
            logger.error(f"Error in daily screening: {e}", exc_info=True)
            await self.telegram_bot.send_alert(
                "Screening Error",
                f"Error during daily screening: {str(e)}",
                "ERROR"
            )
    
    def _format_tracked_stocks(self, stocks: list) -> str:
        """Format tracked stocks for display"""
        if not stocks:
            return "None"
        
        lines = []
        for stock in stocks[:5]:  # Show top 5
            ticker = stock.get('ticker', 'N/A')
            score = stock.get('best_score', 0)
            days = stock.get('days_in_top10', 0)
            lines.append(f"• {ticker}: Score {score:.1f} ({days} days tracked)")
        
        return '\n'.join(lines)
