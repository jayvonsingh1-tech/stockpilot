# Trade Tracking & Daily Check-In Feature

**Date:** 2026-06-18  
**Status:** Feature Request - Phase 4  
**Priority:** High

---

## 🎯 Feature Overview

**Interactive Trade Management System**

Bot should:
1. Recognize when you've placed a trade (via message confirmation)
2. Store trade details in database
3. Track trade status daily
4. Send daily updates until trade closes
5. Alert when exit conditions are met

---

## 💬 User Interaction Flow

### Step 1: Signal Sent
```
Bot: 🟢 TRADING SIGNAL: BUY AAPL at $150
     Stop Loss: $135
     Target: $180
     [Full instructions...]
```

### Step 2: User Confirms Trade
```
You: "✅ Placed order for AAPL"
or
You: "Done, bought 100 shares of AAPL at $150"
or
You: "Order placed"
```

### Step 3: Bot Recognizes & Confirms
```
Bot: ✅ Trade Confirmed!
     
     📊 TRACKING STARTED
     • Ticker: AAPL
     • Entry: $150.00
     • Shares: 100
     • Stop Loss: $135.00
     • Target: $180.00
     • Type: Long-Term Investment
     
     I'll check on this trade daily and alert you when:
     • Price reaches target ($180)
     • Stop loss is hit ($135)
     • Important price movements occur
     
     Reply "status AAPL" anytime for update
```

### Step 4: Daily Check-Ins
```
Day 1 (Next Morning):
Bot: 📊 Daily Update: AAPL
     • Current: $152.00 (+1.3%)
     • Distance to target: $28 (15.5%)
     • Status: ✅ Holding
     • Days held: 1

Day 5:
Bot: 📊 Daily Update: AAPL
     • Current: $165.00 (+10%)
     • Distance to target: $15 (8.3%)
     • Status: ✅ Strong move!
     • Days held: 5

Day 30:
Bot: 🎯 TARGET ALERT: AAPL
     • Current: $181.00
     • Target reached: $180 ✅
     
     💰 PROFIT: +$3,100 (+20.7%)
     
     📱 ACTION REQUIRED:
     Exit Strategy: Sell 50% (50 shares)
     
     Reply "closed AAPL 50" when done
```

### Step 5: Partial Exit Confirmation
```
You: "Closed AAPL 50 shares at $181"

Bot: ✅ Partial Exit Recorded
     
     📊 UPDATED POSITION
     • Remaining: 50 shares
     • Avg Entry: $150.00
     • Current: $181.00
     • Unrealized P&L: +$1,550
     • New Target: $216.00
     
     Continuing to track remaining position...
```

### Step 6: Final Exit
```
Bot: 🎯 FINAL TARGET: AAPL
     • Current: $217.00
     • Target: $216 ✅
     
     Time to close remaining position!

You: "Closed all AAPL at $217"

Bot: ✅ TRADE CLOSED
     
     📊 FINAL RESULTS
     • Entry: $150.00
     • Exit 1: $181.00 (50 shares) = +$1,550
     • Exit 2: $217.00 (50 shares) = +$3,350
     • Total Profit: +$4,900 (+32.7%)
     • Days held: 45
     • Strategy: Long-Term Investment
     
     🎉 Excellent trade!
     
     Added to your trading journal.
```

---

## 🗄️ Database Schema

### Trades Table
```sql
CREATE TABLE trades (
    id INTEGER PRIMARY KEY,
    signal_id INTEGER,  -- Links to original signal
    ticker VARCHAR(10),
    action VARCHAR(4),  -- BUY/SELL
    strategy VARCHAR(50),
    trading_type VARCHAR(20),  -- CFD/STOCK
    
    -- Entry
    entry_date DATETIME,
    entry_price DECIMAL(10,2),
    shares INTEGER,
    total_investment DECIMAL(10,2),
    
    -- Risk Management
    stop_loss DECIMAL(10,2),
    target_price DECIMAL(10,2),
    
    -- Status
    status VARCHAR(20),  -- OPEN, PARTIAL_CLOSED, CLOSED
    current_price DECIMAL(10,2),
    unrealized_pnl DECIMAL(10,2),
    realized_pnl DECIMAL(10,2),
    
    -- Tracking
    last_checked DATETIME,
    days_held INTEGER,
    
    -- Exit
    exit_date DATETIME,
    exit_price DECIMAL(10,2),
    
    -- Metadata
    created_at DATETIME,
    updated_at DATETIME
);
```

### Daily Updates Table
```sql
CREATE TABLE trade_updates (
    id INTEGER PRIMARY KEY,
    trade_id INTEGER,
    date DATE,
    price DECIMAL(10,2),
    pnl DECIMAL(10,2),
    pnl_percent DECIMAL(5,2),
    message_sent BOOLEAN,
    created_at DATETIME
);
```

---

## 🤖 Message Recognition System

### Pattern Matching
```python
# Recognize trade confirmation
CONFIRMATION_PATTERNS = [
    r"placed.*order",
    r"bought.*(\d+).*shares",
    r"order.*placed",
    r"done",
    r"✅",
    r"executed",
    r"filled",
]

# Recognize exit confirmation
EXIT_PATTERNS = [
    r"closed.*(\d+).*shares",
    r"sold.*(\d+)",
    r"exited.*position",
    r"took.*profit",
]

# Recognize status request
STATUS_PATTERNS = [
    r"status.*([A-Z]{1,5})",
    r"how.*is.*([A-Z]{1,5})",
    r"update.*([A-Z]{1,5})",
]
```

### Smart Parsing
```python
async def handle_user_message(self, message: str):
    """Parse user message and take action"""
    
    # Check for trade confirmation
    if self._is_trade_confirmation(message):
        # Extract ticker from recent signal
        ticker = self._get_last_signal_ticker()
        # Parse shares if mentioned
        shares = self._extract_shares(message)
        # Create trade record
        await self._create_trade(ticker, shares)
        await self._send_tracking_confirmation(ticker)
    
    # Check for exit confirmation
    elif self._is_exit_confirmation(message):
        ticker = self._extract_ticker(message)
        shares = self._extract_shares(message)
        price = self._extract_price(message)
        await self._record_exit(ticker, shares, price)
        await self._send_exit_confirmation(ticker)
    
    # Check for status request
    elif self._is_status_request(message):
        ticker = self._extract_ticker(message)
        await self._send_trade_status(ticker)
```

---

## 📅 Daily Check-In System

### Scheduler Job
```python
# Add to scheduler.py
self.scheduler.add_job(
    self._check_open_trades,
    CronTrigger(hour=9, minute=0, day_of_week='mon-fri', timezone=uk_tz),
    id='daily_trade_check',
    name='Daily Trade Check-In'
)
```

### Check Logic
```python
async def _check_open_trades(self):
    """Check all open trades and send updates"""
    
    open_trades = self.db.get_open_trades()
    
    for trade in open_trades:
        # Get current price
        current_price = self.data_fetcher.get_current_price(trade['ticker'])
        
        # Calculate P&L
        pnl = (current_price - trade['entry_price']) * trade['shares']
        pnl_percent = (pnl / trade['total_investment']) * 100
        
        # Check if target reached
        if current_price >= trade['target_price']:
            await self._send_target_alert(trade, current_price)
        
        # Check if stop loss hit
        elif current_price <= trade['stop_loss']:
            await self._send_stop_loss_alert(trade, current_price)
        
        # Regular daily update
        else:
            await self._send_daily_update(trade, current_price, pnl, pnl_percent)
        
        # Update database
        self.db.update_trade(trade['id'], current_price, pnl)
```

---

## 📱 Message Templates

### Daily Update (Normal)
```python
message = f"""
📊 Daily Update: {ticker}

💰 Current Price: ${current_price:.2f}
📈 Entry Price: ${entry_price:.2f}
{'🟢' if pnl > 0 else '🔴'} P&L: ${pnl:+,.2f} ({pnl_percent:+.1f}%)

🎯 Target: ${target_price:.2f} ({distance_to_target:.1f}% away)
🛡️ Stop Loss: ${stop_loss:.2f} ({distance_to_stop:.1f}% away)

⏰ Days Held: {days_held}
📊 Status: {'✅ On track' if pnl > 0 else '⚠️ Below entry'}

Reply "status {ticker}" for detailed view
"""
```

### Target Alert
```python
message = f"""
🎯 TARGET REACHED: {ticker}

💰 Current: ${current_price:.2f}
🎯 Target: ${target_price:.2f} ✅

📊 PROFIT: ${pnl:+,.2f} ({pnl_percent:+.1f}%)

📱 ACTION REQUIRED:
{exit_strategy}

Reply "closed {ticker} [shares]" when done
"""
```

### Stop Loss Alert
```python
message = f"""
🛑 STOP LOSS HIT: {ticker}

💰 Current: ${current_price:.2f}
🛡️ Stop Loss: ${stop_loss:.2f} ⚠️

📊 LOSS: ${pnl:,.2f} ({pnl_percent:.1f}%)

Your stop loss should have triggered automatically.
Verify in Trading 212 that position is closed.

Reply "confirmed closed {ticker}" when verified
"""
```

---

## 🎯 Implementation Phases

### Phase 1: Basic Tracking (Week 1-2)
- [ ] Database schema
- [ ] Message recognition
- [ ] Trade creation
- [ ] Manual status command

### Phase 2: Daily Check-Ins (Week 3)
- [ ] Scheduler integration
- [ ] Price fetching
- [ ] Daily update messages
- [ ] Alert system

### Phase 3: Exit Management (Week 4)
- [ ] Exit confirmation parsing
- [ ] Partial exit tracking
- [ ] Final P&L calculation
- [ ] Trading journal

### Phase 4: Advanced Features (Week 5-6)
- [ ] Portfolio view
- [ ] Performance analytics
- [ ] Trade history
- [ ] Export to CSV

---

## 💡 User Commands

```
Available Commands:

/trades - Show all open trades
/history - Show closed trades
/status AAPL - Get update on specific trade
/portfolio - Show portfolio summary
/journal - Export trading journal

Message Shortcuts:
"✅" or "done" - Confirm last signal
"closed AAPL 50" - Record exit
"status AAPL" - Get trade update
```

---

## 🔔 Notification Settings

```yaml
# config/settings.yaml
trade_tracking:
  enabled: true
  daily_updates: true
  update_time: "09:00"  # UK time
  alert_on_target: true
  alert_on_stop_loss: true
  alert_on_milestone: true  # Every 10% gain
  quiet_hours:
    start: "22:00"
    end: "07:00"
```

---

## 📊 Example Full Journey

```
Day 0 (Signal):
Bot: "🟢 BUY AAPL at $150"
You: "✅ placed order"
Bot: "✅ Tracking started"

Day 1-29:
Bot: "📊 Daily Update: AAPL +5.2%"

Day 30:
Bot: "🎯 TARGET REACHED: AAPL"
You: "closed 50 shares at $181"
Bot: "✅ Partial exit recorded"

Day 31-44:
Bot: "📊 Daily Update: AAPL (50 shares)"

Day 45:
Bot: "🎯 FINAL TARGET: AAPL"
You: "closed all at $217"
Bot: "✅ TRADE CLOSED. Profit: $4,900 (+32.7%)"
```

---

## ✅ Benefits

1. **Peace of Mind** - Bot monitors trades 24/7
2. **Never Miss Exits** - Alerts when targets hit
3. **Track Performance** - Automatic journal
4. **Learn from Trades** - Review history
5. **Stay Disciplined** - Follow exit strategy

---

**Status:** Documented for Phase 4 implementation  
**Estimated Time:** 4-6 weeks  
**Dependencies:** Database setup, message handlers, scheduler
