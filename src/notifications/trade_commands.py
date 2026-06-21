"""
Enhanced Telegram Bot Commands for Phase 4
Includes interactive feedback, trade management, and performance tracking
"""
from typing import Dict, Optional
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
from ..engine.trade_database_v2 import TradeDatabaseV2
from ..notifications.signal_formatter import SignalFormatter
from ..data.fetcher import MarketDataFetcher
from ..utils.logger import setup_logger


logger = setup_logger(__name__)


class TradeBotCommands:
    """
    Enhanced Telegram bot commands for Phase 4
    
    Features:
    - Interactive trade confirmation
    - Trade outcome reporting
    - Performance analytics
    - Trade management
    """
    
    def __init__(self):
        """Initialize command handler"""
        self.db = TradeDatabaseV2()
        self.formatter = SignalFormatter()
        self.data_fetcher = MarketDataFetcher()
    
    async def cmd_trades(self, update: Update, context: CallbackContext):
        """List all open trades with current P&L"""
        try:
            trades = self.db.get_open_trades()
            
            if not trades:
                await update.message.reply_text(
                    "📊 No open trades at the moment.\n\n"
                    "Use /status to see bot status or wait for new signals!"
                )
                return
            
            message = "📊 <b>OPEN TRADES</b>\n\n"
            
            for trade in trades:
                ticker = trade['ticker']
                
                # Get current price
                try:
                    df = self.data_fetcher.fetch_ohlcv(ticker, period='1d', interval='1d')
                    current_price = float(df['Close'].iloc[-1]) if df is not None else None
                except:
                    current_price = None
                
                # Calculate P&L
                if current_price and trade['entry_price']:
                    if trade['action'] == 'BUY':
                        pnl = ((current_price - trade['entry_price']) / trade['entry_price']) * 100
                    else:
                        pnl = ((trade['entry_price'] - current_price) / trade['entry_price']) * 100
                    
                    pnl_emoji = "📈" if pnl > 0 else "📉"
                    pnl_text = f"{pnl:+.2f}%"
                else:
                    pnl_emoji = "📊"
                    pnl_text = "N/A"
                
                message += f"""
{pnl_emoji} <b>Trade #{trade['id']} - {ticker}</b>
• Action: {trade['action']}
• Entry: ${trade['entry_price']:.2f}
• Current: ${current_price:.2f if current_price else 'N/A'}
• P&L: {pnl_text}
• Days: {trade.get('hold_days', 0)}
• Strategy: {trade['strategy']}

"""
            
            message += "\nUse /trade <id> to see detailed info for a specific trade."
            
            await update.message.reply_text(message, parse_mode='HTML')
            
        except Exception as e:
            logger.error(f"Error in cmd_trades: {e}")
            await update.message.reply_text("❌ Error fetching trades. Please try again.")
    
    async def cmd_trade(self, update: Update, context: CallbackContext):
        """View detailed information for a specific trade"""
        try:
            if not context.args:
                await update.message.reply_text(
                    "Please provide a trade ID.\n"
                    "Usage: /trade <id>\n"
                    "Example: /trade 42"
                )
                return
            
            trade_id = int(context.args[0])
            trade = self.db.get_trade_by_id(trade_id)
            
            if not trade:
                await update.message.reply_text(f"❌ Trade #{trade_id} not found.")
                return
            
            # Get current price
            ticker = trade['ticker']
            try:
                df = self.data_fetcher.fetch_ohlcv(ticker, period='1d', interval='1d')
                current_price = float(df['Close'].iloc[-1]) if df is not None else None
            except:
                current_price = None
            
            # Format trade status
            message = self.formatter.format_trade_status(trade, current_price)
            
            # Add outcome buttons if trade is open
            if trade['status'] == 'open':
                keyboard = self.formatter.get_trade_outcome_buttons(trade_id)
                reply_markup = InlineKeyboardMarkup(keyboard)
                await update.message.reply_text(message, parse_mode='HTML', reply_markup=reply_markup)
            else:
                await update.message.reply_text(message, parse_mode='HTML')
            
        except ValueError:
            await update.message.reply_text("❌ Invalid trade ID. Please provide a number.")
        except Exception as e:
            logger.error(f"Error in cmd_trade: {e}")
            await update.message.reply_text("❌ Error fetching trade details. Please try again.")
    
    async def cmd_close(self, update: Update, context: CallbackContext):
        """Close a trade manually"""
        try:
            if len(context.args) < 2:
                await update.message.reply_text(
                    "Usage: /close <trade_id> <exit_price> [reason]\n"
                    "Example: /close 42 155.50 Manual exit"
                )
                return
            
            trade_id = int(context.args[0])
            exit_price = float(context.args[1])
            reason = ' '.join(context.args[2:]) if len(context.args) > 2 else "Manual exit"
            
            # Close the trade
            success = self.db.close_trade(trade_id, exit_price, reason)
            
            if success:
                trade = self.db.get_trade_by_id(trade_id)
                pnl = trade.get('pnl_percent', 0)
                pnl_emoji = "🎉" if pnl > 0 else "😔"
                
                await update.message.reply_text(
                    f"{pnl_emoji} <b>Trade #{trade_id} Closed</b>\n\n"
                    f"Ticker: {trade['ticker']}\n"
                    f"Entry: ${trade['entry_price']:.2f}\n"
                    f"Exit: ${exit_price:.2f}\n"
                    f"P&L: {pnl:+.2f}%\n"
                    f"Reason: {reason}",
                    parse_mode='HTML'
                )
            else:
                await update.message.reply_text("❌ Error closing trade. Please check the trade ID.")
            
        except ValueError:
            await update.message.reply_text("❌ Invalid input. Please check your command format.")
        except Exception as e:
            logger.error(f"Error in cmd_close: {e}")
            await update.message.reply_text("❌ Error closing trade. Please try again.")
    
    async def cmd_performance(self, update: Update, context: CallbackContext):
        """View performance statistics"""
        try:
            # Get period from args (default: all_time)
            period = context.args[0] if context.args else 'all_time'
            
            if period not in ['all_time', 'month', 'week']:
                period = 'all_time'
            
            # Get stats
            stats = self.db.get_performance_stats(period)
            
            if not stats or stats.get('total_trades', 0) == 0:
                await update.message.reply_text(
                    "📊 No trading data available yet.\n\n"
                    "Start taking trades to see your performance!"
                )
                return
            
            # Format performance summary
            message = self.formatter.format_performance_summary(stats)
            
            # Add strategy breakdown
            strategies = self.db.get_strategy_performance()
            if strategies:
                message += "\n" + self.formatter.format_strategy_breakdown(strategies)
            
            message += f"\n<i>Period: {period.replace('_', ' ').title()}</i>"
            message += "\n\nUse /performance [week|month|all_time] to change period."
            
            await update.message.reply_text(message, parse_mode='HTML')
            
        except Exception as e:
            logger.error(f"Error in cmd_performance: {e}")
            await update.message.reply_text("❌ Error fetching performance data. Please try again.")
    
    async def cmd_dashboard(self, update: Update, context: CallbackContext):
        """View comprehensive dashboard"""
        try:
            stats = self.db.get_performance_stats('all_time')
            
            message = "📊 <b>STOCKPILOT DASHBOARD</b>\n"
            message += "━━━━━━━━━━━━━━━━━━━━━━\n\n"
            
            # Performance section
            if stats and stats.get('total_trades', 0) > 0:
                message += "📈 <b>PERFORMANCE</b>\n"
                message += f"• Win Rate: {stats['win_rate']:.1f}%\n"
                message += f"• Total P&L: {stats['total_pnl']:+.2f}%\n"
                message += f"• Profit Factor: {stats['profit_factor']:.2f}\n\n"
                
                message += "🎯 <b>TRADES</b>\n"
                message += f"• Total: {stats['total_trades']}\n"
                message += f"• Open: {stats['open_trades']}\n"
                message += f"• Wins: {stats['winning_trades']} ({stats['win_rate']:.1f}%)\n"
                message += f"• Losses: {stats['losing_trades']}\n\n"
                
                # Strategy breakdown
                strategies = self.db.get_strategy_performance()
                if strategies:
                    message += "📊 <b>BEST STRATEGY</b>\n"
                    best = max(strategies, key=lambda x: x['win_rate'])
                    message += f"• {best['strategy']}: {best['win_rate']:.1f}% win rate\n\n"
            else:
                message += "📊 No trading data yet.\n"
                message += "Start taking trades to see your dashboard!\n\n"
            
            message += "💡 <b>QUICK COMMANDS</b>\n"
            message += "• /trades - View open trades\n"
            message += "• /performance - Detailed stats\n"
            message += "• /help - All commands\n"
            
            await update.message.reply_text(message, parse_mode='HTML')
            
        except Exception as e:
            logger.error(f"Error in cmd_dashboard: {e}")
            await update.message.reply_text("❌ Error loading dashboard. Please try again.")
    
    async def handle_callback(self, update: Update, context: CallbackContext):
        """Handle button callbacks for trade feedback"""
        query = update.callback_query
        await query.answer()
        
        try:
            callback_data = query.data
            
            # Parse callback data
            if callback_data.startswith('trade_taken_'):
                signal_id = int(callback_data.split('_')[2])
                await self._handle_trade_taken(query, signal_id)
            
            elif callback_data.startswith('trade_skip_'):
                signal_id = int(callback_data.split('_')[2])
                await self._handle_trade_skipped(query, signal_id)
            
            elif callback_data.startswith('outcome_'):
                parts = callback_data.split('_')
                outcome_type = parts[1]
                trade_id = int(parts[2])
                await self._handle_trade_outcome(query, trade_id, outcome_type)
            
        except Exception as e:
            logger.error(f"Error handling callback: {e}")
            await query.edit_message_text("❌ Error processing your response. Please try again.")
    
    async def _handle_trade_taken(self, query, signal_id: int):
        """Handle user confirming they took the trade"""
        try:
            # Create trade from signal
            trade_id = self.db.create_trade_from_signal(signal_id, user_taken=True)
            
            if trade_id > 0:
                trade = self.db.get_trade_by_id(trade_id)
                
                message = f"""
✅ <b>Trade Confirmed!</b>

Trade #{trade_id} has been added to your portfolio.

<b>Ticker:</b> {trade['ticker']}
<b>Action:</b> {trade['action']}
<b>Entry:</b> ${trade['entry_price']:.2f}

You'll receive reminders on:
• Day {trade['recommended_hold_days']//2}: Review progress
• Day {trade['recommended_hold_days']}: Consider exit

Use /trade {trade_id} to view details anytime.
Good luck! 🚀
"""
                await query.edit_message_text(message, parse_mode='HTML')
            else:
                await query.edit_message_text("❌ Error creating trade. Please try /trades to see your positions.")
            
        except Exception as e:
            logger.error(f"Error in _handle_trade_taken: {e}")
            await query.edit_message_text("❌ Error confirming trade. Please try again.")
    
    async def _handle_trade_skipped(self, query, signal_id: int):
        """Handle user skipping the trade"""
        try:
            # Create trade record but mark as skipped
            trade_id = self.db.create_trade_from_signal(signal_id, user_taken=False)
            
            if trade_id > 0:
                message = """
📝 <b>Trade Skipped</b>

This signal has been marked as skipped.

We'll learn from your preferences to improve future signals!
"""
                await query.edit_message_text(message, parse_mode='HTML')
            else:
                await query.edit_message_text("✅ Signal marked as skipped.")
            
        except Exception as e:
            logger.error(f"Error in _handle_trade_skipped: {e}")
            await query.edit_message_text("❌ Error processing skip. Please try again.")
    
    async def _handle_trade_outcome(self, query, trade_id: int, outcome_type: str):
        """Handle trade outcome reporting"""
        try:
            trade = self.db.get_trade_by_id(trade_id)
            
            if not trade:
                await query.edit_message_text("❌ Trade not found.")
                return
            
            # Map outcome to exit price and reason
            outcome_map = {
                'tp1': (trade['take_profit_1'], 'TP1 Hit'),
                'tp2': (trade['take_profit_2'], 'TP2 Hit'),
                'tp3': (trade['take_profit_3'], 'TP3 Hit'),
                'sl': (trade['stop_loss'], 'Stop Loss'),
                'time': (None, 'Time Exit'),
                'manual': (None, 'Manual Exit')
            }
            
            exit_price, exit_reason = outcome_map.get(outcome_type, (None, 'Unknown'))
            
            # If no exit price, ask user to provide it
            if exit_price is None:
                await query.edit_message_text(
                    f"Please provide exit price using:\n"
                    f"/close {trade_id} <price> {exit_reason}\n\n"
                    f"Example: /close {trade_id} 155.50 {exit_reason}"
                )
                return
            
            # Close the trade
            success = self.db.close_trade(trade_id, exit_price, exit_reason)
            
            if success:
                trade = self.db.get_trade_by_id(trade_id)
                pnl = trade.get('pnl_percent', 0)
                pnl_emoji = "🎉" if pnl > 0 else "😔"
                
                message = f"""
{pnl_emoji} <b>Trade Closed - {exit_reason}</b>

<b>Ticker:</b> {trade['ticker']}
<b>Entry:</b> ${trade['entry_price']:.2f}
<b>Exit:</b> ${exit_price:.2f}
<b>P&L:</b> {pnl:+.2f}%
<b>Days Held:</b> {trade.get('hold_days', 0)}

Great job tracking your trade! 📊
"""
                await query.edit_message_text(message, parse_mode='HTML')
            else:
                await query.edit_message_text("❌ Error closing trade. Please try again.")
            
        except Exception as e:
            logger.error(f"Error in _handle_trade_outcome: {e}")
            await query.edit_message_text("❌ Error processing outcome. Please try again.")
    
    async def cmd_help_phase4(self, update: Update, context: CallbackContext):
        """Show Phase 4 commands help"""
        message = """
📚 <b>PHASE 4 COMMANDS</b>

<b>📊 Trade Management:</b>
/trades - List all open trades with P&L
/trade <id> - View detailed trade info
/close <id> <price> [reason] - Close a trade
/dashboard - View comprehensive dashboard

<b>📈 Performance:</b>
/performance [period] - View statistics
  • week - Last 7 days
  • month - Last 30 days  
  • all_time - All trades (default)

<b>💡 Interactive Features:</b>
• Click buttons on signals to confirm/skip
• Click buttons on trades to report outcomes
• Automatic reminders for open trades

<b>📋 Examples:</b>
/trade 42 - View trade #42 details
/close 42 155.50 Manual exit
/performance week - This week's stats

<b>🎯 Tips:</b>
• Always confirm trades you take
• Report outcomes for better learning
• Check /dashboard regularly
"""
        await update.message.reply_text(message, parse_mode='HTML')
