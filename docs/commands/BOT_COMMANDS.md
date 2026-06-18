# 🤖 StockPilot Bot Commands Reference

**Last Updated:** 2026-06-18  
**Version:** Phase 3  
**Status:** Active

---

## 📋 Quick Reference

| Command | Description | Example |
|---------|-------------|---------|
| `/start` | Start the bot | `/start` |
| `/help` | Show all commands | `/help` |
| `/status` | Check bot status | `/status` |
| `/trades` | Show open trades | `/trades` |
| `/portfolio` | Portfolio summary | `/portfolio` |
| `/performance` | Performance stats | `/performance` |
| `/research` | Company analysis | `/research AAPL` |

---

## 📱 Telegram Commands

### Basic Commands

#### `/start`
**Description:** Start the bot and get welcome message  
**Usage:** `/start`  
**Response:**
```
🤖 StockPilot Bot Started

I'll send you high-confidence trading signals with 
step-by-step Trading 212 instructions.

Use /help to see available commands.
```

---

#### `/help`
**Description:** Show all available commands  
**Usage:** `/help`  
**Response:** List of all commands with descriptions

---

#### `/status`
**Description:** Check if bot is running  
**Usage:** `/status`  
**Response:**
```
🤖 STOCKPILOT STATUS

Mode: signal_only
Status: ✅ Running
Time: 21:43:06

All systems operational ✅
```

---

### Trading Commands

#### `/trades`
**Description:** Show all your open trades  
**Usage:** `/trades`  
**Response:**
```
📊 OPEN TRADES

🟢 AAPL
• Entry: $150.00 → $155.00
• P&L: +$500 (+3.3%)
• Days: 5

🔴 TSLA
• Entry: $250.00 → $245.00
• P&L: -$250 (-2.0%)
• Days: 2

Total: 2 open position(s)
```

**If no trades:**
```
📊 Open Trades

No open trades at the moment.
```

---

#### `/portfolio`
**Description:** Show portfolio summary with total P&L  
**Usage:** `/portfolio`  
**Response:**
```
📊 PORTFOLIO SUMMARY

💰 Current Positions
• Open Trades: 3
• Total Value: $45,000
• Unrealized P&L: +$2,500

📈 All-Time Performance
• Total Trades: 15
• Win Rate: 73.3%
• Total P&L: +$8,450
• Avg Profit: $850
• Avg Loss: -$320
```

---

#### `/performance`
**Description:** Detailed performance statistics  
**Usage:** `/performance`  
**Response:**
```
📈 PERFORMANCE ANALYTICS

🎯 Trading Statistics
• Total Trades: 15
• Winning Trades: 11
• Losing Trades: 4
• Win Rate: 73.3%

💰 Profit & Loss
• Total P&L: +$8,450
• Average Profit: $850
• Average Loss: -$320
• Profit Factor: 2.66

📊 Rating
🌟 Excellent - Keep it up!
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

## 💬 Message Patterns (No / needed)

### Trade Confirmation

**What to say:** Any of these phrases  
**When:** After you place an order on Trading 212

**Accepted phrases:**
- `✅`
- `placed order`
- `done`
- `bought`
- `executed`
- `filled`

**Example:**
```
You: ✅

Bot: ✅ Trade Confirmed!

📊 TRACKING STARTED
• Ticker: AAPL
• Entry: $150.00
• Shares: 100
• Stop Loss: $135.00
• Target: $180.00

I'll check on this trade daily!
```

---

### Exit Confirmation

**What to say:** `closed <TICKER> <SHARES>`  
**When:** After you close a position

**Examples:**
- `closed AAPL 50`
- `sold TSLA 100`
- `exited NVDA 25`

**Response:**
```
You: closed AAPL 50

Bot: ✅ Trade Closed: AAPL

📊 FINAL RESULTS
• Entry: $150.00
• Exit: $181.00
• Shares: 50
• P&L: +$1,550 (+20.7%)
• Days Held: 45

🎉 Excellent trade!

Added to your trading journal.
```

---

### Status Query

**What to say:** `status <TICKER>`  
**When:** You want to check a specific trade

**Examples:**
- `status AAPL`
- `how is TSLA`
- `update NVDA`

**Response:**
```
You: status AAPL

Bot: 📊 Trade Status: AAPL

💰 Current Position
• Entry: $150.00
• Current: $165.00
• Shares: 100
• 🟢 P&L: +$1,500 (+10.0%)

🎯 Targets
• Target: $180.00 (+9.1% away)
• Stop Loss: $135.00 (+18.2% away)

⏰ Time
• Days Held: 30
• Entry Date: 2026-05-19

📊 Status: ✅ On track
```

---

## 🚫 What the Bot CANNOT Understand (Yet)

The bot **does NOT** respond to:
- ❌ "What do you think about Tesla?"
- ❌ "Should I buy Apple?"
- ❌ "Why is the market down?"
- ❌ "Explain this signal"
- ❌ General conversation

**Why:** Natural language AI chat is a Phase 5 feature.

**For now, use:**
- Commands (with `/`)
- Specific patterns (like "✅" or "status AAPL")

---

## 📊 Automatic Messages

The bot will send you messages automatically:

### 1. Startup Message
**When:** Bot starts or restarts
```
🚀 Bot is now running in signal_only mode.
📊 Monitoring 75 stocks.
🎯 Min Confidence: 85%
⏰ Scanning every 15 minutes during market hours.
```

### 2. Trading Signals
**When:** High-confidence opportunity found (85%+)
```
🟢 TRADING SIGNAL: BUY AAPL
[Full signal with instructions]
```

### 3. Daily Stock Screening
**When:** 7:00 AM UK (before markets open)
```
🔍 Starting daily stock screening...
[Results with top candidates]
```

### 4. Market Open
**When:** 9:30 AM ET / 2:30 PM UK
```
🔔 Markets are now open. Starting signal scan...
```

### 5. Market Close
**When:** 4:00 PM ET / 9:00 PM UK
```
🔔 Markets are now closed. Final scan complete.
```

### 6. Daily Summary
**When:** 4:30 PM ET / 9:30 PM UK
```
📊 DAILY SUMMARY
[Portfolio stats and signals sent]
```

### 7. Weekly Report
**When:** Sunday 6:00 PM ET / 11:00 PM UK
```
📈 WEEKLY REPORT
[Performance summary for the week]
```

### 8. Daily Trade Updates
**When:** 9:00 AM UK (for tracked trades)
```
📊 Daily Update: AAPL
• Current: $165.00 (+10%)
• Days held: 30
• Status: ✅ On track
```

### 9. Target Alerts
**When:** Your trade reaches target price
```
🎯 TARGET REACHED: AAPL
• Current: $181.00
• Target: $180.00 ✅
• Profit: +$3,100 (+20.7%)

📱 ACTION: Sell 50% now
Reply "closed AAPL 50" when done
```

### 10. Stop Loss Alerts
**When:** Your trade hits stop loss
```
🛑 STOP LOSS HIT: AAPL
• Current: $134.00
• Stop Loss: $135.00 ⚠️
• Loss: -$1,600 (-10.7%)

Verify position is closed in Trading 212.
```

---

## 🎯 Command Cheat Sheet

**Quick Actions:**
```
✅              → Confirm last signal
status AAPL     → Check AAPL trade
closed AAPL 50  → Record exit
/trades         → See all positions
/portfolio      → Portfolio summary
/research TSLA  → Research Tesla
```

**Information:**
```
/help           → All commands
/status         → Bot status
/performance    → Your stats
```

---

## 📝 Notes

- Commands are **case-insensitive** (`/TRADES` = `/trades`)
- Ticker symbols must be **UPPERCASE** (`AAPL` not `aapl`)
- Bot responds within **1-2 seconds**
- All data stored in **database** (persistent)
- Commands work **24/7** (even when markets closed)

---

## 🔄 Version History

**Phase 3 (Current):**
- Added `/trades`, `/portfolio`, `/performance`, `/research`
- Added message recognition (✅, closed, status)
- Added trade tracking
- Added daily updates

**Phase 2:**
- Added `/start`, `/help`, `/status`
- Basic signal sending

**Phase 1:**
- Initial bot setup

---

## 🚀 Coming Soon (Phase 5)

- Natural language chat
- "Ask me anything" about stocks
- Conversational AI assistant
- Voice commands (maybe!)

---

**Need help?** Reply `/help` in Telegram!
