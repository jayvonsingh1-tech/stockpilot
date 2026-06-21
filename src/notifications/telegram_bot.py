"""
Telegram bot for sending signals and notifications
Enhanced with interactive commands and trade tracking
Phase 4A: Interactive feedback and enhanced signals
"""
import asyncio
import re
from telegram import Bot, Update, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
from typing import Dict, Optional, List
from datetime import datetime
from ..utils.logger import setup_logger
from ..utils.config import get_config
from ..engine.trade_database import TradeDatabase
from ..engine.trade_database_v2 import TradeDatabaseV2
from .signal_formatter import SignalFormatter
from .trade_commands import TradeBotCommands


logger = setup_logger(__name__)


class TelegramBot:
    """Telegram bot for StockPilot with interactive features"""
    
    def __init__(self, token: str, chat_id: str):
        """
        Initialize Telegram bot
        
        Args:
            token: Telegram bot token
            chat_id: Chat ID to send messages to
        """
        self.token = token
        self.chat_id = chat_id
        self.bot = None
        self.application = None
        self.db = TradeDatabase()
        self.db_v2 = TradeDatabaseV2()  # Phase 4A enhanced database
        self.formatter = SignalFormatter()  # Phase 4A signal formatter
        self.trade_commands = TradeBotCommands()  # Phase 4A commands
        self.last_signal = None  # Store last signal for confirmation
        
    async def initialize(self):
        """Initialize the bot"""
        try:
            self.bot = Bot(token=self.token)
            self.application = Application.builder().token(self.token).build()
            
            # Add command handlers (existing)
            self.application.add_handler(CommandHandler("start", self.cmd_start))
            self.application.add_handler(CommandHandler("status", self.cmd_status))
            self.application.add_handler(CommandHandler("help", self.cmd_help))
            self.application.add_handler(CommandHandler("portfolio", self.cmd_portfolio))
            self.application.add_handler(CommandHandler("research", self.cmd_research))
            
            # Add Phase 4A command handlers
            self.application.add_handler(CommandHandler("trades", self.trade_commands.cmd_trades))
            self.application.add_handler(CommandHandler("trade", self.trade_commands.cmd_trade))
            self.application.add_handler(CommandHandler("close", self.trade_commands.cmd_close))
            self.application.add_handler(CommandHandler("performance", self.trade_commands.cmd_performance))
            self.application.add_handler(CommandHandler("dashboard", self.trade_commands.cmd_dashboard))
            
            # Add callback handler for interactive buttons (Phase 4A)
            self.application.add_handler(CallbackQueryHandler(self.trade_commands.handle_callback))
            
            # Add message handler for text messages (trade confirmations, etc.)
            self.application.add_handler(
                MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message)
            )
            
            # Initialize the application (but don't start polling yet)
            await self.application.initialize()
            
            logger.info("Telegram bot initialized successfully with Phase 4A features")
        except Exception as e:
            logger.error(f"Error initializing Telegram bot: {e}")
            raise
    
    async def start_polling(self):
        """Start the bot in polling mode to receive commands"""
        try:
            if not self.application:
                await self.initialize()
            
            logger.info("Starting Telegram bot polling...")
            await self.application.start()
            await self.application.updater.start_polling(drop_pending_updates=True)
            logger.info("Telegram bot polling started")
        except Exception as e:
            logger.error(f"Error starting bot polling: {e}")
            raise
    
    async def stop_polling(self):
        """Stop the bot polling"""
        try:
            if self.application and self.application.updater:
                await self.application.updater.stop()
                await self.application.stop()
                await self.application.shutdown()
                logger.info("Telegram bot polling stopped")
        except Exception as e:
            logger.error(f"Error stopping bot polling: {e}")
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle text messages from users"""
        try:
            message_text = update.message.text.strip().upper()
            
            # Check if it's a ticker symbol (simple check)
            if len(message_text) <= 5 and message_text.isalpha():
                # User sent a ticker, get quick info
                ticker = message_text
                await update.message.reply_text(f"🔍 Looking up {ticker}...")
                
                from ..data.fetcher import MarketDataFetcher
                fetcher = MarketDataFetcher()
                price = fetcher.get_current_price(ticker)
                
                if price:
                    await update.message.reply_text(
                        f"📊 *{ticker}*\nCurrent Price: ${price:.2f}\n\n"
                        f"Use /research {ticker} for detailed analysis",
                        parse_mode="Markdown"
                    )
                else:
                    await update.message.reply_text(f"❌ Could not find data for {ticker}")
            else:
                # Generic response
                await update.message.reply_text(
                    "Send me a ticker symbol (e.g., AAPL) or use /help for commands"
                )
        except Exception as e:
            logger.error(f"Error handling message: {e}")
            await update.message.reply_text("Sorry, I encountered an error processing your message.")
    
    async def send_message(self, text: str, parse_mode: str = None) -> bool:
        """
        Send a message to the configured chat
        
        Args:
            text: Message text
            parse_mode: Parse mode (Markdown or HTML or None)
            
        Returns:
            True if sent successfully, False otherwise
        """
        try:
            if not self.bot:
                await self.initialize()
            
            await self.bot.send_message(
                chat_id=self.chat_id,
                text=text,
                parse_mode=parse_mode
            )
            logger.info("Message sent successfully")
            return True
        except Exception as e:
            logger.error(f"Error sending message: {e}")
            return False
    
    async def send_signal(self, signal: Dict) -> bool:
        """
        Send a trading signal with Phase 4A enhanced format
        
        Args:
            signal: Signal dictionary with trade details
            
        Returns:
            True if sent successfully
        """
        try:
            # Store signal for potential confirmation
            self.last_signal = signal
            
            # Save signal to Phase 4A database
            signal_id = self.db_v2.save_signal(signal)
            signal['signal_id'] = signal_id
            
            # Also save to old database for backward compatibility
            self.db.save_signal(signal)
            
            # Check if it's a long-term investment or CFD trade
            is_long_term = signal.get('trading_type') == 'LONG_TERM_INVESTMENT'
            
            # Use Phase 4A enhanced format
            if is_long_term:
                return await self._send_enhanced_signal(signal, is_long_term=True)
            else:
                return await self._send_enhanced_signal(signal, is_long_term=False)
            
        except Exception as e:
            logger.error(f"Error sending signal: {e}")
            # Fallback to old format if Phase 4A fails
            try:
                if signal.get('trading_type') == 'LONG_TERM_INVESTMENT':
                    return await self._send_long_term_signal(signal)
                else:
                    return await self._send_cfd_signal(signal)
            except:
                return False
    
    async def _send_enhanced_signal(self, signal: Dict, is_long_term: bool = False) -> bool:
        """Send signal with Phase 4A enhanced format and interactive buttons"""
        try:
            signal_id = signal.get('signal_id')
            
            # Format signal with enhanced details
            message = self.formatter.format_signal(signal, signal_id)
            
            # Add trading type specific note
            if is_long_term:
                message += "\n\n💼 <b>LONG-TERM INVESTMENT</b>\n"
                message += "• Use Invest account (not CFD)\n"
                message += "• Hold for fundamental value\n"
            else:
                message += "\n\n⚡ <b>CFD TRADE</b>\n"
                message += "• Use CFD account\n"
                message += "• Follow stop loss strictly\n"
            
            # Get feedback buttons
            buttons = self.formatter.get_feedback_buttons(signal_id)
            reply_markup = InlineKeyboardMarkup(buttons)
            
            # Send message with buttons
            await self.bot.send_message(
                chat_id=self.chat_id,
                text=message,
                parse_mode='HTML',
                reply_markup=reply_markup
            )
            
            logger.info(f"Enhanced signal sent for {signal['ticker']} (ID: {signal_id})")
            return True
            
        except Exception as e:
            logger.error(f"Error sending enhanced signal: {e}")
            return False
    
    async def _send_cfd_signal(self, signal: Dict) -> bool:
        """Send CFD trading signal (existing format)"""
        try:
            action_emoji = "🟢" if signal['action'] == 'BUY' else "🔴"
            action_word = "BUY" if signal['action'] == 'BUY' else "SELL"
            
            # Calculate position size info
            position_info = signal.get('position_size', {})
            shares = position_info.get('shares', 0)
            position_value = position_info.get('position_value', 0)
            
            message = f"""
{action_emoji} *TRADING SIGNAL: {action_word} {signal['ticker']}*

━━━━━━━━━━━━━━━━━━━━━━━━━━━

📈 *STOCK DETAILS*
• Ticker: *{signal['ticker']}*
• Name: {signal.get('name', signal['ticker'])}
• Market: {signal.get('market', 'Unknown')}
• Current Price: ${signal['entry_price']}

━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎯 *TRADE SETUP*
• Action: *{action_word}*
• Entry Price: *${signal['entry_price']}*
• Stop Loss: ${signal['stop_loss']} ({signal.get('stop_loss_percent', 0):.1f}%)
• Take Profit 1: ${signal['take_profit_1']} (+{signal.get('tp1_percent', 0):.1f}%)
• Take Profit 2: ${signal.get('take_profit_2', 'N/A')} (+{signal.get('tp2_percent', 0):.1f}%)
• Take Profit 3: ${signal.get('take_profit_3', 'N/A')} (+{signal.get('tp3_percent', 0):.1f}%)

📊 Confidence: *{signal['confidence']}%*
⚖️ Risk/Reward Ratio: *1:{signal.get('risk_reward', 0):.1f}*
⏰ Timeframe: {signal.get('timeframe', 'Unknown')}

━━━━━━━━━━━━━━━━━━━━━━━━━━━

📱 *HOW TO PLACE THIS ORDER ON TRADING 212:*

*STEP 1:* Open Trading 212 app
↓
*STEP 2:* Tap the search icon 🔍 at the top
↓
*STEP 3:* Type "{signal['ticker']}" and select it
↓
*STEP 4:* Tap the big *"{action_word}"* button
↓
*STEP 5:* Choose order type:
   • Select *"Limit Order"*
   • Set limit price to: *${signal['entry_price']}*
↓
*STEP 6:* Enter amount:
   • Suggested: {shares} shares (≈ ${position_value:.2f})
   • Or use 1-2% of your portfolio
↓
*STEP 7:* Set Stop Loss:
   • Toggle "Stop Loss" ON
   • Enter: *${signal['stop_loss']}*
↓
*STEP 8:* Set Take Profit:
   • Toggle "Take Profit" ON
   • Enter: *${signal['take_profit_1']}*
↓
*STEP 9:* Review your order:
   • {action_word} {signal['ticker']}
   • Limit: ${signal['entry_price']}
   • Stop: ${signal['stop_loss']}
   • Target: ${signal['take_profit_1']}
↓
*STEP 10:* Tap *"Place Order"* to confirm ✅

━━━━━━━━━━━━━━━━━━━━━━━━━━━

⚠️ *IMPORTANT NOTES:*

• If current price is already at ${signal['entry_price']} or better, use *"Market Order"* instead of Limit
• Your order will execute when price reaches ${signal['entry_price']}
• Stop loss protects you if price moves against you
• Take profit automatically closes at target price

━━━━━━━━━━━━━━━━━━━━━━━━━━━

💡 *WHY THIS TRADE?*
{signal.get('reasoning', 'No reasoning provided')}

━━━━━━━━━━━━━━━━━━━━━━━━━━━

📋 *TRADE MANAGEMENT:*

When TP1 (${signal['take_profit_1']}) hits:
→ Close 50% of position
→ Move stop loss to breakeven (${signal['entry_price']})

When TP2 (${signal.get('take_profit_2', 'N/A')}) hits:
→ Close another 25%
→ Trail stop loss behind price

Let TP3 (${signal.get('take_profit_3', 'N/A')}) run with trailing stop

━━━━━━━━━━━━━━━━━━━━━━━━━━━

Strategy: {signal.get('strategy', 'Unknown')}
Confidence: {signal['confidence']}%
Risk/Reward: 1:{signal.get('risk_reward', 0):.1f}

Reply ✅ when you've placed the order!
"""
            
            return await self.send_message(message)
        except Exception as e:
            logger.error(f"Error sending signal: {e}")
            return False
    
    async def send_daily_summary(self, summary: Dict) -> bool:
        """
        Send daily summary
        
        Args:
            summary: Summary dictionary
            
        Returns:
            True if sent successfully
        """
        try:
            message = f"""
📊 *STOCKPILOT — DAILY SUMMARY*
{datetime.now().strftime('%A, %d %B %Y')}

💰 Signals Sent: {summary.get('signals_sent', 0)}
📈 Paper P&L: {summary.get('paper_pnl', 0):+.2f}%
✅ Win Rate: {summary.get('win_rate', 0):.1f}%
📊 Confidence Avg: {summary.get('avg_confidence', 0):.0f}%

🎯 *Active Positions:* {summary.get('active_positions', 0)}

Have a great evening! 🌙
"""
            
            return await self.send_message(message)
        except Exception as e:
            logger.error(f"Error sending daily summary: {e}")
            return False
    
    async def send_weekly_report(self, report: Dict) -> bool:
        """
        Send weekly performance report
        
        Args:
            report: Report dictionary
            
        Returns:
            True if sent successfully
        """
        try:
            message = f"""
📋 *STOCKPILOT — WEEKLY REPORT*
Week of {report.get('week_start', '')} - {report.get('week_end', '')}

💰 Weekly Return: *{report.get('weekly_return', 0):+.2f}%*
📊 Signals Sent: {report.get('signals_sent', 0)}
✅ Winners: {report.get('winners', 0)} ({report.get('win_rate', 0):.1f}% win rate)
❌ Losers: {report.get('losers', 0)}
📈 Best Trade: {report.get('best_trade', 'N/A')} {report.get('best_trade_return', 0):+.1f}%
📉 Worst Trade: {report.get('worst_trade', 'N/A')} {report.get('worst_trade_return', 0):+.1f}%

🏆 *Best Strategy This Week:* {report.get('best_strategy', 'Unknown')}
📊 Avg Confidence: {report.get('avg_confidence', 0):.0f}%
⚖️ Avg Risk/Reward: 1:{report.get('avg_risk_reward', 0):.1f}

🔍 *Learning Notes:*
{report.get('learning_notes', 'No notes this week')}

📅 *Next Week Watchlist:*
{report.get('next_week_watchlist', 'No specific stocks highlighted')}

Have a great weekend! 🚀
"""
            
            return await self.send_message(message)
        except Exception as e:
            logger.error(f"Error sending weekly report: {e}")
            return False
    
    async def send_alert(self, title: str, message: str, level: str = "INFO") -> bool:
        """
        Send an alert message
        
        Args:
            title: Alert title
            message: Alert message
            level: Alert level (INFO, WARNING, ERROR)
            
        Returns:
            True if sent successfully
        """
        try:
            emoji = {
                "INFO": "ℹ️",
                "WARNING": "⚠️",
                "ERROR": "🚨"
            }.get(level, "ℹ️")
            
            text = f"{emoji} {title}\n\n{message}"
            return await self.send_message(text, parse_mode=None)
        except Exception as e:
            logger.error(f"Error sending alert: {e}")
            return False
    
    # Command handlers
    async def cmd_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        await update.message.reply_text(
            "🤖 *StockPilot Bot Started*\n\n"
            "I'll send you high-confidence trading signals with step-by-step Trading 212 instructions.\n\n"
            "Use /help to see available commands.",
            parse_mode="Markdown"
        )
    
    async def cmd_status(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /status command"""
        config = get_config()
        mode = config.get('mode', 'unknown')
        
        await update.message.reply_text(
            f"🤖 *STOCKPILOT STATUS*\n\n"
            f"Mode: {mode}\n"
            f"Status: ✅ Running\n"
            f"Time: {datetime.now().strftime('%H:%M:%S')}\n\n"
            f"All systems operational ✅",
            parse_mode="Markdown"
        )
    
    async def cmd_help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command - Phase 4A Enhanced"""
        help_text = (
            "🤖 *STOCKPILOT COMMANDS - Phase 4A*\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "📱 *BASIC COMMANDS*\n"
            "/start - Start the bot\n"
            "/status - Check bot status\n"
            "/help - Show this help message\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "📊 *TRADE MANAGEMENT* 🆕\n"
            "/trades - List all open trades with P&L\n"
            "/trade [id] - View specific trade details\n"
            "/close [id] [price] - Close a trade manually\n"
            "/dashboard - Comprehensive overview\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "📈 *PERFORMANCE & ANALYSIS*\n"
            "/portfolio - Portfolio summary\n"
            "/performance [period] - Detailed stats\n"
            "  • week - Last 7 days\n"
            "  • month - Last 30 days\n"
            "  • all_time - All trades (default)\n"
            "/research [TICKER] - Company analysis\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "🔘 *INTERACTIVE FEATURES* 🆕\n"
            "• Click ✅ on signals to confirm trades\n"
            "• Click 🎯 buttons to report outcomes\n"
            "• Get automatic reminders at 9 AM UK\n"
            "• Real-time P&L tracking\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "💡 *QUICK TIPS*\n"
            "• Send ticker symbols for quick price lookup\n"
            "• All commands work in lowercase too\n"
            "• Use buttons instead of typing when possible\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "🆕 *PHASE 4A FEATURES*\n"
            "✅ Enhanced signals with precise timeframes\n"
            "✅ Multiple take profit levels (TP1, TP2, TP3)\n"
            "✅ Interactive feedback buttons\n"
            "✅ Automatic trade reminders\n"
            "✅ Real-time performance tracking\n"
            "✅ Strategy-level analytics\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "📚 *EXAMPLES*\n"
            "`/trade 42` - View trade #42\n"
            "`/close 42 156.00` - Close trade at $156\n"
            "`/performance week` - Weekly stats\n"
            "`/research AAPL` - Research Apple\n\n"
            "Need more help? Check the documentation or just start trading! 🚀"
        )
        await update.message.reply_text(help_text, parse_mode="Markdown")
    
    async def cmd_trades(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /trades command - show all open trades"""
        trades = self.db.get_open_trades()
        
        if not trades:
            await update.message.reply_text(
                "📊 *Open Trades*\n\nNo open trades at the moment.\n\n"
                "Wait for signals or use /help for commands.",
                parse_mode="Markdown"
            )
            return
        
        message = "📊 *OPEN TRADES*\n\n"
        
        for trade in trades:
            # Get current price
            from ..data.fetcher import MarketDataFetcher
            fetcher = MarketDataFetcher()
            current_price = fetcher.get_current_price(trade['ticker'])
            
            if current_price:
                # Calculate P&L
                if trade['action'] == 'BUY':
                    pnl = (current_price - trade['entry_price']) * trade['shares']
                else:
                    pnl = (trade['entry_price'] - current_price) * trade['shares']
                
                pnl_percent = (pnl / trade['total_investment']) * 100
                
                message += f"{'🟢' if pnl > 0 else '🔴'} *{trade['ticker']}*\n"
                message += f"• Entry: ${trade['entry_price']:.2f} → ${current_price:.2f}\n"
                message += f"• P&L: ${pnl:+,.2f} ({pnl_percent:+.1f}%)\n"
                message += f"• Days: {trade.get('days_held', 0)}\n\n"
        
        message += f"Total: {len(trades)} open position(s)\n"
        message += f"\nReply 'status TICKER' for details"
        
        await update.message.reply_text(message, parse_mode="Markdown")
    
    async def cmd_portfolio(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /portfolio command - show portfolio summary"""
        trades = self.db.get_open_trades()
        stats = self.db.get_performance_stats()
        
        total_value = 0
        total_pnl = 0
        
        # Calculate current portfolio value
        from ..data.fetcher import MarketDataFetcher
        fetcher = MarketDataFetcher()
        
        for trade in trades:
            current_price = fetcher.get_current_price(trade['ticker'])
            if current_price:
                if trade['action'] == 'BUY':
                    pnl = (current_price - trade['entry_price']) * trade['shares']
                else:
                    pnl = (trade['entry_price'] - current_price) * trade['shares']
                
                total_value += current_price * trade['shares']
                total_pnl += pnl
        
        message = f"""
📊 *PORTFOLIO SUMMARY*

💰 *Current Positions*
• Open Trades: {len(trades)}
• Total Value: ${total_value:,.2f}
• Unrealized P&L: ${total_pnl:+,.2f}

📈 *All-Time Performance*
• Total Trades: {stats.get('total_trades', 0)}
• Win Rate: {stats.get('win_rate', 0):.1f}%
• Total P&L: ${stats.get('total_pnl', 0):+,.2f}
• Avg Profit: ${stats.get('avg_profit', 0):.2f}
• Avg Loss: ${stats.get('avg_loss', 0):.2f}

Use /trades to see open positions
Use /performance for detailed stats
"""
        
        await update.message.reply_text(message, parse_mode="Markdown")
    
    async def cmd_performance(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /performance command - show detailed performance stats"""
        stats = self.db.get_performance_stats()
        
        message = f"""
📈 *PERFORMANCE ANALYTICS*

🎯 *Trading Statistics*
• Total Trades: {stats.get('total_trades', 0)}
• Winning Trades: {stats.get('winning_trades', 0)}
• Losing Trades: {stats.get('losing_trades', 0)}
• Win Rate: {stats.get('win_rate', 0):.1f}%

💰 *Profit & Loss*
• Total P&L: ${stats.get('total_pnl', 0):+,.2f}
• Average Profit: ${stats.get('avg_profit', 0):.2f}
• Average Loss: ${stats.get('avg_loss', 0):.2f}
• Best Trade: ${stats.get('best_trade', 0):+,.2f}
• Worst Trade: ${stats.get('worst_trade', 0):+,.2f}

📊 *Risk Metrics*
• Profit Factor: {stats.get('profit_factor', 0):.2f}
• Average Hold Time: {stats.get('avg_hold_days', 0):.1f} days

Use /portfolio for current positions
"""
        
        await update.message.reply_text(message, parse_mode="Markdown")
    
    async def cmd_research(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /research command - get company research"""
        if not context.args:
            await update.message.reply_text(
                "📊 *Company Research*\n\n"
                "Usage: /research TICKER\n"
                "Example: /research AAPL\n\n"
                "Get detailed fundamental analysis and AI-powered insights.",
                parse_mode="Markdown"
            )
            return
        
        ticker = context.args[0].upper()
        await update.message.reply_text(f"🔍 Researching {ticker}... This may take a moment.")
        
        try:
            from ..analysis.research import ResearchAnalyst
            analyst = ResearchAnalyst()
            report = analyst.generate_report(ticker)
            
            if report:
                # Send condensed version via Telegram
                message = f"""
📊 *{report['company_name']}* ({ticker})

💼 *Sector:* {report.get('sector', 'N/A')}

📈 *Financial Health:* {report.get('financial_health_score', 0)}/100
{report.get('financial_health_summary', '')}

💰 *Valuation:* {report.get('valuation_summary', 'N/A')}

🎯 *Bot Assessment:* {report.get('bot_recommendation', 'N/A')}
*Overall Score:* {report.get('overall_score', 0)}/100

{report.get('action_recommendation', '')}
"""
                await update.message.reply_text(message, parse_mode="Markdown")
            else:
                await update.message.reply_text(f"❌ Could not generate research report for {ticker}")
        except Exception as e:
            logger.error(f"Error in research command: {e}")
            await update.message.reply_text(f"❌ Error researching {ticker}: {str(e)}")
    
    async def send_screening_results(self, candidates: list) -> bool:
        """
        Send daily screening results with stock recommendations
        
        Args:
            candidates: List of candidate stocks with scores
            
        Returns:
            True if sent successfully
        """
        try:
            if not candidates:
                message = "📊 *DAILY STOCK SCREENING*\n\nNo new opportunities found today meeting our criteria (70+ score)."
                return await self.send_message(message)
            
            message = f"""
📊 *DAILY STOCK SCREENING RESULTS*
{datetime.now().strftime('%A, %d %B %Y')}

Found *{len(candidates)}* high-quality investment opportunities:

━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
            
            for i, stock in enumerate(candidates, 1):
                score_emoji = "🟢" if stock['total_score'] >= 85 else "🟡" if stock['total_score'] >= 75 else "⚪"
                
                message += f"""
{score_emoji} *#{i}. {stock['ticker']}* - {stock['name']}
📊 Overall Score: *{stock['total_score']}/100*
🏢 Sector: {stock['sector']}
💰 Price: ${stock['current_price']:.2f}

📈 Scores:
• Technical: {stock['technical_score']}/100
• Fundamental: {stock['fundamental_score']}/100
• Momentum: {stock['momentum_score']}/100
• Value: {stock['value_score']}/100

✅ *{stock['recommendation']}*

Reasons: {', '.join(stock['reasons'])}

━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
            
            message += f"""

💡 *RECOMMENDATION:*
Add the top {min(3, len(candidates))} stocks to your watchlist for monitoring.

These stocks scored 70+ across technical, fundamental, momentum, and value metrics.
"""
            
            return await self.send_message(message)
            
        except Exception as e:
            logger.error(f"Error sending screening results: {e}")
            return False
    
    async def send_research_report(self, report: Dict) -> bool:
        """
        Send detailed research report for a stock
        
        Args:
            report: Research report dictionary
            
        Returns:
            True if sent successfully
        """
        try:
            overview = report['overview']
            financial = report['financial_health']
            valuation = report['valuation']
            growth = report['growth']
            technical = report['technical_setup']
            assessment = report['bot_assessment']
            
            message = f"""
📋 *RESEARCH REPORT: {report['ticker']}*
{overview['name']}

━━━━━━━━━━━━━━━━━━━━━━━━━━━

📈 *COMPANY OVERVIEW*
• Sector: {overview['sector']}
• Industry: {overview['industry']}
• Market Cap: ${overview['market_cap']/1e9:.2f}B
• Employees: {overview['employees']:,}
• Country: {overview['country']}

━━━━━━━━━━━━━━━━━━━━━━━━━━━

💰 *FINANCIAL HEALTH*
• Health Score: *{financial['health_score']}/100* ({financial['health_rating']})
• Profit Margin: {financial['profit_margin']*100:.1f}%
• Debt/Equity: {financial['debt_to_equity']:.1f}
• Current Ratio: {financial['current_ratio']:.2f}

━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 *VALUATION*
• P/E Ratio: {valuation['pe_ratio']:.1f}
• P/B Ratio: {valuation['pb_ratio']:.2f}
• Assessment: *{valuation['valuation']}*
• Valuation Score: {valuation['valuation_score']}/100

━━━━━━━━━━━━━━━━━━━━━━━━━━━

📈 *GROWTH*
• Revenue Growth: {growth['revenue_growth']*100:.1f}%
• Earnings Growth: {growth['earnings_growth']*100:.1f}%
• Rating: *{growth['growth_rating']}*
• Trend: {growth['trend']}

━━━━━━━━━━━━━━━━━━━━━━━━━━━

📉 *TECHNICAL SETUP*
• Current Price: ${technical.get('current_price', 0):.2f}
• Trend: *{technical.get('trend', 'Unknown')}*
• RSI: {technical.get('rsi', 50):.1f}
• Support: ${technical.get('support', 0):.2f}
• Resistance: ${technical.get('resistance', 0):.2f}
• Position: {technical.get('position', 'N/A')}

━━━━━━━━━━━━━━━━━━━━━━━━━━━

⚠️ *RISK FACTORS*
{chr(10).join('• ' + risk for risk in report['risk_factors'])}

━━━━━━━━━━━━━━━━━━━━━━━━━━━

🤖 *BOT ASSESSMENT*
• Overall Score: *{assessment['overall_score']}/100*
• Recommendation: *{assessment['recommendation']}*
• Confidence: {assessment['confidence']}%

💡 *Action:* {assessment['action']}

━━━━━━━━━━━━━━━━━━━━━━━━━━━

Generated: {report['generated_at']}
"""
            
            return await self.send_message(message)
            
        except Exception as e:
            logger.error(f"Error sending research report: {e}")
            return False


def create_bot(token: Optional[str] = None, chat_id: Optional[str] = None) -> TelegramBot:
    """
    Create a Telegram bot instance
    
    Args:
        token: Bot token (if None, loads from config)
        chat_id: Chat ID (if None, loads from config)
        
    Returns:
        TelegramBot instance
    """
    if token is None or chat_id is None:
        config = get_config()
        telegram_config = config.get_telegram_config()
        token = token or telegram_config.get('bot_token')
        chat_id = chat_id or telegram_config.get('chat_id')
    
    if not token or not chat_id:
        raise ValueError("Telegram bot token and chat_id must be provided")
    
    return TelegramBot(token, chat_id)
