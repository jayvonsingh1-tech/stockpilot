"""
Telegram Bot - Interactive Commands Extension
Add these methods to the TelegramBot class
"""

# Add after the existing send_signal method:

async def _send_long_term_signal(self, signal: Dict) -> bool:
    """Send long-term investment signal with detailed instructions"""
    try:
        action_emoji = "🟢" if signal['action'] == 'BUY' else "🔴"
        
        # Get position size info
        position_info = signal.get('position_size', {})
        shares = position_info.get('shares', 0)
        position_value = position_info.get('position_value', 0)
        
        # Get fundamentals
        fundamentals = signal.get('fundamentals', {})
        
        message = f"""
{action_emoji} *LONG-TERM INVESTMENT: {signal['action']} {signal['ticker']}*

━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 *INVESTMENT THESIS*
{signal.get('investment_thesis', 'Value investment opportunity')}

💰 *VALUATION*
• Current Price: ${signal['entry_price']:.2f}
• Fair Value: ${signal.get('fair_value', 0):.2f} (DCF)
• Target Price: ${signal.get('target_price', 0):.2f}
• Discount: {signal.get('discount_to_fair_value', 0):.1f}%

📈 *FUNDAMENTALS*
• P/E Ratio: {fundamentals.get('pe_ratio', 'N/A')}
• P/B Ratio: {fundamentals.get('pb_ratio', 'N/A')}
• Profit Margin: {fundamentals.get('profit_margin', 'N/A')}%
• Revenue Growth: +{fundamentals.get('revenue_growth', 'N/A')}%
• Debt/Equity: {fundamentals.get('debt_to_equity', 'N/A')}

━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎯 *INVESTMENT DETAILS*
• Entry Price: *${signal['entry_price']:.2f}*
• Stop Loss: ${signal['stop_loss']:.2f} (-{abs(((signal['stop_loss'] - signal['entry_price']) / signal['entry_price']) * 100):.1f}%)
• Expected Return: +{signal.get('expected_return', 0):.1f}%
• Timeframe: {signal.get('timeframe', '6-12 months')}
• Position Size: {shares} shares (≈${position_value:.2f})

━━━━━━━━━━━━━━━━━━━━━━━━━━━

⏰ *EXIT STRATEGY*
{signal.get('exit_strategy', {}).get('type', 'Value-based')} approach:

1️⃣ Sell 50% at Fair Value (${signal.get('fair_value', 0):.2f})
2️⃣ Sell remaining 50% at Target (${signal.get('target_price', 0):.2f})
3️⃣ Stop Loss if drops to ${signal['stop_loss']:.2f}
4️⃣ Review every 6 months

━━━━━━━━━━━━━━━━━━━━━━━━━━━

📱 *HOW TO BUY ON TRADING 212 (INVEST MODE):*

*STEP 1:* Open Trading 212 app
↓
*STEP 2:* CHECK YOU'RE IN "INVEST" MODE
        • Look at top of screen
        • Should say "Invest" (NOT "CFD")
        • If it says "CFD", tap it and switch to "Invest"
↓
*STEP 3:* Tap SEARCH icon (🔍) at top
↓
*STEP 4:* Type "{signal['ticker']}" and select it
↓
*STEP 5:* Tap the BIG GREEN "BUY" button
↓
*STEP 6:* Select "Limit Order"
        • Tap "Market Order" dropdown
        • Select "Limit Order"
        • Enter limit price: *${signal['entry_price']:.2f}*
↓
*STEP 7:* Enter number of shares
        • Suggested: {shares} shares
        • Total cost: ${position_value:.2f}
↓
*STEP 8:* Set Stop Loss (IMPORTANT!)
        • Toggle "Stop Loss" switch to ON
        • Enter: *${signal['stop_loss']:.2f}*
↓
*STEP 9:* VERIFY YOUR ORDER:
        ✓ Stock: {signal['ticker']}
        ✓ Action: BUY
        ✓ Type: Limit Order
        ✓ Limit: ${signal['entry_price']:.2f}
        ✓ Shares: {shares}
        ✓ Stop Loss: ${signal['stop_loss']:.2f}
        ✓ Total: ${position_value:.2f}
↓
*STEP 10:* Tap "PLACE ORDER" ✅

━━━━━━━━━━━━━━━━━━━━━━━━━━━

💡 *WHY THIS INVESTMENT?*
{chr(10).join('• ' + r for r in signal.get('reasoning', []))}

━━━━━━━━━━━━━━━━━━━━━━━━━━━

⚠️ *IMPORTANT NOTES:*
• This is a LONG-TERM position ({signal.get('timeframe', '6-12 months')})
• Don't panic on short-term volatility
• Review fundamentals quarterly
• Set calendar reminder for 6-month review
• Consider dollar-cost averaging if price drops

━━━━━━━━━━━━━━━━━━━━━━━━━━━

Strategy: {signal.get('strategy', 'Value Investment')}
Confidence: {signal.get('confidence', 0)}%
Risk/Reward: 1:{signal.get('risk_reward', 0):.1f}
Type: Long-Term Stock Investment

*Reply "✅" or "placed order" when you've executed this trade!*
I'll track it and send you daily updates.
"""
        
        return await self.send_message(message)
        
    except Exception as e:
        logger.error(f"Error sending long-term signal: {e}")
        return False


# Message handler for trade confirmations
async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle user text messages for trade confirmations and queries"""
    try:
        message_text = update.message.text.lower()
        
        # Check for trade confirmation
        if self._is_trade_confirmation(message_text):
            await self._handle_trade_confirmation(update, message_text)
        
        # Check for exit confirmation
        elif self._is_exit_confirmation(message_text):
            await self._handle_exit_confirmation(update, message_text)
        
        # Check for status query
        elif self._is_status_query(message_text):
            await self._handle_status_query(update, message_text)
        
        # Unknown message
        else:
            await update.message.reply_text(
                "I didn't understand that. Try:\n"
                "• '✅' or 'placed order' to confirm a trade\n"
                "• 'closed AAPL 50' to record an exit\n"
                "• 'status AAPL' to check a trade\n"
                "• /help for all commands"
            )
    
    except Exception as e:
        logger.error(f"Error handling message: {e}")


def _is_trade_confirmation(self, text: str) -> bool:
    """Check if message is a trade confirmation"""
    patterns = [
        r'✅',
        r'placed.*order',
        r'bought',
        r'sold',
        r'done',
        r'executed',
        r'filled'
    ]
    return any(re.search(pattern, text, re.IGNORECASE) for pattern in patterns)


def _is_exit_confirmation(self, text: str) -> bool:
    """Check if message is an exit confirmation"""
    patterns = [
        r'closed.*\d+',
        r'sold.*\d+',
        r'exited',
        r'took.*profit'
    ]
    return any(re.search(pattern, text, re.IGNORECASE) for pattern in patterns)


def _is_status_query(self, text: str) -> bool:
    """Check if message is a status query"""
    patterns = [
        r'status.*[A-Z]{1,5}',
        r'how.*is.*[A-Z]{1,5}',
        r'update.*[A-Z]{1,5}'
    ]
    return any(re.search(pattern, text, re.IGNORECASE) for pattern in patterns)


async def _handle_trade_confirmation(self, update: Update, message_text: str):
    """Handle trade confirmation"""
    if not self.last_signal:
        await update.message.reply_text(
            "No recent signal to confirm. Please wait for a signal first."
        )
        return
    
    # Extract shares if mentioned
    shares_match = re.search(r'(\d+)\s*shares?', message_text, re.IGNORECASE)
    shares = int(shares_match.group(1)) if shares_match else self.last_signal.get('position_size', {}).get('shares', 100)
    
    # Create trade in database
    trade_id = self.db.create_trade(self.last_signal, shares)
    
    if trade_id > 0:
        signal = self.last_signal
        await update.message.reply_text(
            f"✅ *Trade Confirmed!*\n\n"
            f"📊 *TRACKING STARTED*\n"
            f"• Ticker: {signal['ticker']}\n"
            f"• Entry: ${signal['entry_price']:.2f}\n"
            f"• Shares: {shares}\n"
            f"• Stop Loss: ${signal['stop_loss']:.2f}\n"
            f"• Target: ${signal.get('target_price', signal.get('take_profit_1', 0)):.2f}\n"
            f"• Type: {signal.get('trading_type', 'CFD')}\n\n"
            f"I'll check on this trade daily and alert you when:\n"
            f"• Price reaches target\n"
            f"• Stop loss is hit\n"
            f"• Important price movements occur\n\n"
            f"Reply 'status {signal['ticker']}' anytime for update",
            parse_mode="Markdown"
        )
        
        # Clear last signal
        self.last_signal = None
    else:
        await update.message.reply_text(
            "❌ Error creating trade record. Please try again."
        )


async def _handle_exit_confirmation(self, update: Update, message_text: str):
    """Handle exit confirmation"""
    # Extract ticker
    ticker_match = re.search(r'([A-Z]{1,5})', message_text)
    if not ticker_match:
        await update.message.reply_text("Please specify the ticker (e.g., 'closed AAPL 50')")
        return
    
    ticker = ticker_match.group(1)
    
    # Extract shares
    shares_match = re.search(r'(\d+)', message_text)
    shares = int(shares_match.group(1)) if shares_match else 0
    
    # Extract price if mentioned
    price_match = re.search(r'\$?(\d+\.?\d*)', message_text)
    exit_price = float(price_match.group(1)) if price_match else None
    
    # Get trade from database
    trade = self.db.get_trade_by_ticker(ticker)
    
    if not trade:
        await update.message.reply_text(f"No open trade found for {ticker}")
        return
    
    # If no exit price provided, fetch current price
    if not exit_price:
        from ..data.fetcher import MarketDataFetcher
        fetcher = MarketDataFetcher()
        exit_price = fetcher.get_current_price(ticker)
    
    # Close trade
    success = self.db.close_trade(trade['id'], exit_price, "Manual exit")
    
    if success:
        # Calculate P&L
        if trade['action'] == 'BUY':
            pnl = (exit_price - trade['entry_price']) * shares
        else:
            pnl = (trade['entry_price'] - exit_price) * shares
        
        pnl_percent = (pnl / (trade['entry_price'] * shares)) * 100
        
        await update.message.reply_text(
            f"✅ *Trade Closed: {ticker}*\n\n"
            f"📊 *FINAL RESULTS*\n"
            f"• Entry: ${trade['entry_price']:.2f}\n"
            f"• Exit: ${exit_price:.2f}\n"
            f"• Shares: {shares}\n"
            f"• P&L: ${pnl:+,.2f} ({pnl_percent:+.1f}%)\n"
            f"• Days Held: {trade.get('days_held', 0)}\n\n"
            f"{'🎉 Excellent trade!' if pnl > 0 else '📚 Learning opportunity'}\n\n"
            f"Added to your trading journal.",
            parse_mode="Markdown"
        )
    else:
        await update.message.reply_text("❌ Error closing trade. Please try again.")


async def _handle_status_query(self, update: Update, message_text: str):
    """Handle status query"""
    # Extract ticker
    ticker_match = re.search(r'([A-Z]{1,5})', message_text)
    if not ticker_match:
        await update.message.reply_text("Please specify the ticker (e.g., 'status AAPL')")
        return
    
    ticker = ticker_match.group(1)
    
    # Get trade from database
    trade = self.db.get_trade_by_ticker(ticker)
    
    if not trade:
        await update.message.reply_text(f"No open trade found for {ticker}")
        return
    
    # Get current price
    from ..data.fetcher import MarketDataFetcher
    fetcher = MarketDataFetcher()
    current_price = fetcher.get_current_price(ticker)
    
    if current_price:
        # Update trade with current price
        self.db.update_trade_price(trade['id'], current_price)
        
        # Calculate P&L
        if trade['action'] == 'BUY':
            pnl = (current_price - trade['entry_price']) * trade['shares']
        else:
            pnl = (trade['entry_price'] - current_price) * trade['shares']
        
        pnl_percent = (pnl / trade['total_investment']) * 100
        
        # Distance to target and stop
        target = trade.get('target_price', 0)
        stop = trade.get('stop_loss', 0)
        
        distance_to_target = ((target - current_price) / current_price) * 100 if target else 0
        distance_to_stop = ((current_price - stop) / current_price) * 100 if stop else 0
        
        await update.message.reply_text(
            f"📊 *Trade Status: {ticker}*\n\n"
            f"💰 *Current Position*\n"
            f"• Entry: ${trade['entry_price']:.2f}\n"
            f"• Current: ${current_price:.2f}\n"
            f"• Shares: {trade['shares']}\n"
            f"• {'🟢' if pnl > 0 else '🔴'} P&L: ${pnl:+,.2f} ({pnl_percent:+.1f}%)\n\n"
            f"🎯 *Targets*\n"
            f"• Target: ${target:.2f} ({distance_to_target:+.1f}% away)\n"
            f"• Stop Loss: ${stop:.2f} ({distance_to_stop:+.1f}% away)\n\n"
            f"⏰ *Time*\n"
            f"• Days Held: {trade.get('days_held', 0)}\n"
            f"• Entry Date: {trade['entry_date'][:10]}\n\n"
            f"📊 Status: {'✅ On track' if pnl > 0 else '⚠️ Below entry'}",
            parse_mode="Markdown"
        )
    else:
        await update.message.reply_text(f"❌ Error fetching current price for {ticker}")


# Command handlers
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
• Profit Factor: {abs(stats.get('avg_profit', 1) / stats.get('avg_loss', 1)):.2f}

📊 *Rating*
{self._get_performance_rating(stats.get('win_rate', 0))}
"""
    
    await update.message.reply_text(message, parse_mode="Markdown")


def _get_performance_rating(self, win_rate: float) -> str:
    """Get performance rating based on win rate"""
    if win_rate >= 70:
        return "🌟 Excellent - Keep it up!"
    elif win_rate >= 60:
        return "✅ Good - Above average"
    elif win_rate >= 50:
        return "📊 Fair - Room for improvement"
    else:
        return "⚠️ Needs work - Review strategy"


async def cmd_research(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /research command - get company research"""
    if not context.args:
        await update.message.reply_text(
            "Please specify a ticker: /research AAPL"
        )
        return
    
    ticker = context.args[0].upper()
    
    await update.message.reply_text(f"🔍 Researching {ticker}... This may take a moment.")
    
    # Generate research report
    from ..analysis.fundamental import FundamentalAnalysis
    fa = FundamentalAnalysis()
    analysis = fa.analyze_company(ticker)
    
    if not analysis:
        await update.message.reply_text(f"❌ Could not analyze {ticker}. Please check the ticker symbol.")
        return
    
    # Format research report
    val = analysis['valuation']
    prof = analysis['profitability']
    growth = analysis['growth']
    health = analysis['financial_health']
    
    message = f"""
🔍 *RESEARCH REPORT: {ticker}*
{analysis['company_name']}

━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 *VALUATION*
• P/E Ratio: {val.get('pe_ratio', 'N/A')}
• P/B Ratio: {val.get('pb_ratio', 'N/A')}
• Assessment: {val.get('valuation', 'N/A')}
• Score: {val.get('score', 0)}/100

💰 *PROFITABILITY*
• Profit Margin: {prof.get('profit_margin', 'N/A')}%
• ROE: {prof.get('roe', 'N/A')}%
• Rating: {prof.get('rating', 'N/A')}
• Score: {prof.get('score', 0)}/100

📈 *GROWTH*
• Revenue Growth: {growth.get('revenue_growth', 'N/A')}%
• Rating: {growth.get('rating', 'N/A')}
• Score: {growth.get('score', 0)}/100

🏥 *FINANCIAL HEALTH*
• Debt/Equity: {health.get('debt_to_equity', 'N/A')}
• Current Ratio: {health.get('current_ratio', 'N/A')}
• Rating: {health.get('rating', 'N/A')}
• Score: {health.get('score', 0)}/100

━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎯 *OVERALL SCORE: {analysis['overall_score']}/100*
📊 *RATING: {analysis['rating']}*

Sector: {analysis['sector']}
Industry: {analysis['industry']}
"""
    
    await update.message.reply_text(message, parse_mode="Markdown")
