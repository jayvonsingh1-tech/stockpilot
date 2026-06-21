# 🤖 StockPilot Bot Commands Reference

**Last Updated:** 2026-06-21  
**Version:** Phase 4A  
**Status:** Active

---

## 📋 Quick Reference

| Command | Description | Example |
|---------|-------------|---------|
| `/start` | Start the bot | `/start` |
| `/help` | Show all commands | `/help` |
| `/status` | Check bot status | `/status` |
| `/trades` | List open trades with P&L | `/trades` |
| `/trade` | View specific trade details | `/trade 42` |
| `/close` | Close a trade manually | `/close 42 156.00` |
| `/portfolio` | Portfolio summary | `/portfolio` |
| `/performance` | Performance statistics | `/performance week` |
| `/dashboard` | Comprehensive overview | `/dashboard` |
| `/research` | Company analysis | `/research AAPL` |

---

## 🆕 Phase 4A New Features

### Interactive Buttons
- **Trade Confirmation:** Click buttons on signals to confirm/skip trades
- **Outcome Reporting:** Click buttons to report trade results (TP1, TP2, TP3, Stop Loss)
- **No typing needed:** Just click the buttons!

### Enhanced Signals
- **Precise Timeframes:** Know exactly when to enter and exit
- **Multiple Take Profits:** TP1, TP2, TP3 with expected timing
- **Exit Strategies:** Step-by-step profit-taking instructions
- **Review Dates:** Specific dates to check your trades

### Automatic Reminders
- **Daily at 9 AM UK:** Bot checks for pending reminders
- **Trade Reviews:** Reminds you to check progress
- **Exit Warnings:** Alerts when max hold period approaching
- **Current P&L:** Shows your profit/loss in reminders

---

## 📱 Telegram Commands

### Basic Commands

#### `/start`
**Description:** Start the bot and get welcome message  
**Usage:** `/start`  
**Response:**
```
🤖 StockPilot Bot Started - Phase 4A

I'll send you high-confidence trading signals with:
• Precise timeframes and exit strategies
• Interactive buttons for easy tracking
• Automatic trade reminders
• Real-time performance analytics

Use /help to see all commands.
```

---

#### `/help`
**Description:** Show all available commands  
**Usage:** `/help`  
**Response:** Complete list of commands with Phase 4A features

---

#### `/status`
**Description:** Check if bot is running  
**Usage:** `/status`  
**Response:**
```
🤖 STOCKPILOT STATUS

Mode: signal_only
Status: ✅ Running
Version: Phase 4A
Time: 14:43:06

Features:
✅ Enhanced signals with timeframes
✅ Interactive feedback buttons
✅ Automatic trade reminders
✅ Performance tracking

All systems operational ✅
```

---

### 🆕 Trade Management Commands (Phase 4A)

#### `/trades`
**Description:** List all your open trades with real-time P&L  
**Usage:** `/trades`  
**Response:**
```
📊 OPEN TRADES

📈 Trade #42 - AAPL
• Action: BUY
• Entry: $150.00
• Current: $154.50
• P&L: +3.0%
• Days: 3
• Strategy: Trend Following

📉 Trade #43 - TSLA
• Action: BUY
• Entry: $250.00
• Current: $245.00
• P&L: -2.0%
• Days: 1
• Strategy: Breakout

Use /trade <id> to see detailed info for a specific trade.
```

**If no trades:**
```
📊 No open trades at the moment.

Use /status to see bot status or wait for new signals!
```

---

#### `/trade <id>` 🆕
**Description:** View detailed information for a specific trade  
**Usage:** `/trade 42`  
**Response:**
```
✅ TRADE STATUS - AAPL

Action: BUY
Entry: $150.00 (Jun 18, 2026)
Current: $154.50
Days Held: 3

📈 P&L: +3.0%

Targets:
• Stop Loss: $145.00
• TP1: $156.00
• TP2: $160.00
• TP3: $165.00

Strategy: Trend Following
Confidence: 90%

[🎯 Hit TP1] [🎯 Hit TP2] [🎯 Hit TP3]
[🛑 Hit Stop Loss] [⏰ Time Exit] [📝 Manual Exit]
```

---

#### `/close <id> <price> [reason]` 🆕
**Description:** Close a trade manually  
**Usage:** `/close 42 156.00 Hit TP1`  
**Response:**
```
🎉 Trade #42 Closed

Ticker: AAPL
Entry: $150.00
Exit: $156.00
P&L: +4.0%
Reason: Hit TP1

Great job tracking your trade! 📊
```

**Examples:**
- `/close 42 156.00` - Close at $156.00
- `/close 42 156.00 Hit TP1` - Close with reason
- `/close 42 145.00 Stop loss` - Close at stop loss

---

#### `/dashboard` 🆕
**Description:** View comprehensive performance dashboard  
**Usage:** `/dashboard`  
**Response:**
```
📊 STOCKPILOT DASHBOARD
━━━━━━━━━━━━━━━━━━━━━━

📈 PERFORMANCE
• Win Rate: 75.0%
• Total P&L: +12.5%
• Profit Factor: 2.8

🎯 TRADES
• Total: 20
• Open: 2
• Wins: 15 (75.0%)
• Losses: 3

📊 BEST STRATEGY
• Trend Following: 80% win rate

💡 QUICK COMMANDS
• /trades - View open trades
• /performance - Detailed stats
• /help - All commands
```

---

#### `/performance [period]` 🆕
**Description:** View detailed performance statistics  
**Usage:** `/performance` or `/performance week` or `/performance month`  
**Response:**
```
📊 PERFORMANCE SUMMARY

💰 TRADING STATS:
• Total Trades: 20
• Open Trades: 2
• Win Rate: 75.0%

📈 RESULTS:
• Winning Trades: 15
• Losing Trades: 3
• Total P&L: +12.5%

💡 AVERAGES:
• Avg Profit: +5.2%
• Avg Loss: -2.1%
• Profit Factor: 2.48

📊 STRATEGY BREAKDOWN:

Trend Following
• Trades: 10
• Win Rate: 80.0%
• Avg P&L: +6.1%
• Total P&L: +61.0%

Breakout
• Trades: 6
• Win Rate: 66.7%
• Avg P&L: +4.2%
• Total P&L: +25.2%

Period: All Time

Use /performance [week|month|all_time] to change period.
```

---

#### `/portfolio`
**Description:** Show portfolio summary with total P&L  
**Usage:** `/portfolio`  
**Response:**
```
📊 PORTFOLIO SUMMARY

💰 Current Positions
• Open Trades: 2
• Total Value: $30,900
• Unrealized P&L: +$900 (+3.0%)

📈 All-Time Performance
• Total Trades: 20
• Win Rate: 75.0%
• Total P&L: +$6,250 (+12.5%)
• Best Trade: AAPL +$1,200
• Worst Trade: TSLA -$320
```

---

### Research Commands

#### `/research <TICKER>`
**Description:** Get comprehensive company analysis  
**Usage:** `/research AAPL`  
**Response:**
```
🔍 RESEARCH REPORT: AAPL
Apple Inc.

━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 VALUATION
• P/E Ratio: 29.5
• P/B Ratio: 42.5
• Assessment: Fair Value
• Score: 75/100

💰 PROFITABILITY
• Profit Margin: 25.3%
• ROE: 147.2%
• Rating: Excellent
• Score: 95/100

📈 GROWTH
• Revenue Growth: +2.1%
• Rating: Slow Growth
• Score: 60/100

🏥 FINANCIAL HEALTH
• Debt/Equity: 1.98
• Current Ratio: 0.98
• Rating: Good
• Score: 70/100

━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎯 OVERALL SCORE: 75/100
📊 RATING: BUY

Sector: Technology
Industry: Consumer Electronics
```

---

## 🔘 Interactive Buttons (Phase 4A)

### Signal Confirmation Buttons
**When:** You receive a trading signal  
**Buttons:**
- `✅ I'm Taking This Trade` - Click if you enter the trade
- `❌ Skip This Trade` - Click if you skip it

**What happens:**
- Trade is tracked in database
- You'll get reminders at key dates
- Performance is calculated automatically

---

### Trade Outcome Buttons
**When:** You view a trade with `/trade <id>`  
**Buttons:**
- `🎯 Hit TP1` - First target reached
- `🎯 Hit TP2` - Second target reached
- `🎯 Hit TP3` - Third target reached
- `🛑 Hit Stop Loss` - Stop loss triggered
- `⏰ Time Exit` - Exited due to time
- `📝 Manual Exit` - Manual exit (will ask for price)

**What happens:**
- Trade is closed automatically
- P&L is calculated
- Performance stats updated
- Strategy performance tracked

---

## 🔔 Automatic Messages

### 1. Enhanced Trading Signals (Phase 4A)
**When:** High-confidence opportunity found (75%+)  
**Format:**
```
🚀 TRADING SIGNAL #42

📈 BUY AAPL
💰 Entry: $150.00
🛑 Stop Loss: $145.00 (-3.3%)

✅ Take Profit Targets:
• TP1: $156.00 (+4.0%) - Expected: 2-3 days
• TP2: $160.00 (+6.7%) - Expected: 4-5 days
• TP3: $165.00 (+10.0%) - Expected: 6-7 days

⏰ TIMEFRAME DETAILS:
• Strategy: Trend Following (Swing Trade)
• Recommended Hold: 3-7 days
• Entry Window: Next 24 hours
• Review Date: June 24, 2026 (3 days)
• Max Hold: June 27, 2026 (8 days)
• Exit if no TP hit by: June 28, 2026

📊 SIGNAL DETAILS:
• Confidence: 90%
• Risk/Reward: 3.0:1
• Strategy: Trend Following

💡 EXIT STRATEGY:
1. If TP1 hit in 2 days → Take 50% profit, move SL to breakeven
2. If TP2 hit in 5 days → Take 30% profit, trail SL
3. Let 20% run to TP3 or trailing stop
4. If no TP hit by day 8 → Exit at market

📅 REMINDERS:
• Day 3: Check if TP1 hit
• Day 5: Check if TP2 hit
• Day 7: Consider trailing stop
• Day 8: Exit if still open

Did you take this trade?
[✅ I'm Taking This Trade] [❌ Skip This Trade]
```

---

### 2. Trade Reminders (Phase 4A) 🆕
**When:** 9:00 AM UK daily (for open trades)  
**Format:**
```
🔔 TRADE REMINDER - AAPL

Day 3 - Time to review your trade!

Entry: $150.00
Current: $154.50
TP1 Target: $156.00

📈 Current P&L: +3.0%

Action: Check if TP1 hit. If yes, take 50% profit 
and move stop to breakeven.

[Update Trade Status] [Close Trade]
```

**Types of reminders:**
- **Review Reminder:** Mid-point check (e.g., Day 3 of 7)
- **Max Hold Warning:** Approaching max hold period
- **Exit Warning:** Time to exit if no targets hit

---

### 3. Daily Stock Screening
**When:** 7:00 AM UK (before markets open)
```
🔍 Starting daily stock screening...
Screening 180+ stocks...

📊 TOP 20 OPPORTUNITIES
[List of top candidates]

🎯 ACTIVE TOP 10 TRACKING
[Currently tracked stocks]

📈 Detailed reports for top 5 coming...
```

---

### 4. Market Open
**When:** 9:30 AM ET / 2:30 PM UK
```
🔔 Markets are now open. Starting signal scan...
```

---

### 5. Market Close
**When:** 4:00 PM ET / 9:00 PM UK
```
🔔 Markets are now closed. Final scan complete.
```

---

### 6. Daily Summary
**When:** 4:30 PM ET / 9:30 PM UK
```
📊 DAILY SUMMARY

Signals Sent: 2
Trades Taken: 1
Open Positions: 3
Today's P&L: +$320 (+0.6%)
```

---

### 7. Weekly Report
**When:** Sunday 6:00 PM ET / 11:00 PM UK
```
📈 WEEKLY REPORT

Performance: +$1,250 (+2.5%)
Win Rate: 75%
Best Trade: AAPL +$850
Signals Sent: 8
Trades Taken: 6
```

---

## 🎯 Command Cheat Sheet

**Quick Actions:**
```
/trades              → See all open trades
/trade 42            → View trade #42 details
/close 42 156.00     → Close trade #42
/dashboard           → Quick overview
/performance         → Detailed stats
```

**Research:**
```
/research AAPL       → Research Apple
/research TSLA       → Research Tesla
```

**Information:**
```
/help                → All commands
/status              → Bot status
```

**Interactive (No commands needed):**
```
Click ✅ on signal   → Confirm trade
Click 🎯 on trade    → Report outcome
```

---

## 📝 Phase 4A Features Summary

### What's New:
✅ **Enhanced Signals** - Precise timeframes, multiple TPs, exit strategies  
✅ **Interactive Buttons** - One-click trade confirmation and outcome reporting  
✅ **Automatic Reminders** - Daily checks at 9 AM UK for open trades  
✅ **Performance Tracking** - Real-time P&L, win rate, strategy comparison  
✅ **New Commands** - `/trade`, `/close`, `/dashboard`, `/performance`  
✅ **Lower Confidence** - 75% threshold (more signals!)  

### How It Works:
1. **Get Signal** → Read enhanced details with timeframes
2. **Click Button** → Confirm if you take the trade
3. **Get Reminders** → Bot reminds you at key dates
4. **Report Outcome** → Click button when trade closes
5. **Track Performance** → See your real results

---

## 🔄 Version History

**Phase 4A (Current - June 21, 2026):**
- ✅ Enhanced signals with precise timeframes
- ✅ Interactive feedback buttons
- ✅ Automatic trade reminders
- ✅ New commands: `/trade`, `/close`, `/dashboard`
- ✅ Enhanced `/performance` with periods
- ✅ Confidence lowered to 75%
- ✅ Real-time P&L tracking

**Phase 3 (June 18, 2026):**
- Added `/trades`, `/portfolio`, `/performance`, `/research`
- Added trade tracking database
- Added daily screening (180+ stocks)
- Expanded to 150 watchlist stocks

**Phase 2:**
- Added `/start`, `/help`, `/status`
- Basic signal sending

**Phase 1:**
- Initial bot setup

---

## 🚀 Coming in Phase 4B

- Learning from your trading patterns
- Confidence calibration based on results
- Personalized signal filtering
- Strategy optimization
- Advanced analytics

---

## 📞 Need Help?

- Type `/help` in Telegram for quick reference
- Type `/status` to check if bot is running
- Click buttons instead of typing when possible
- All commands are case-insensitive

---

**Version:** Phase 4A  
**Last Updated:** June 21, 2026  
**Status:** ✅ Active & Ready
