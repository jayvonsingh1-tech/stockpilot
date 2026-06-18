# 🧪 StockPilot Phase 3 - Testing Guide

**Date:** 2026-06-18  
**Version:** Phase 3  
**Status:** Ready for Testing

---

## 🎯 Testing Objectives

1. Verify all new features work correctly
2. Test database operations
3. Validate Telegram bot commands
4. Check signal generation
5. Ensure no errors or crashes

---

## ✅ Pre-Test Checklist

Before testing, ensure:
- [ ] All files committed to Git
- [ ] Railway deployment successful
- [ ] Bot is running (check Railway logs)
- [ ] Telegram bot responding to `/start`
- [ ] Database file created (`data/trades.db`)

---

## 🧪 Test Plan

### Test 1: Basic Bot Functionality

**Commands to test:**
```
/start
/help
/status
```

**Expected Results:**
- `/start` → Welcome message
- `/help` → List of commands
- `/status` → Bot status with timestamp

**Pass Criteria:** All commands respond within 2 seconds

---

### Test 2: Value Investment Strategy

**Test:** Wait for a value investment signal OR manually trigger screening

**Expected Signal Format:**
```
🟢 LONG-TERM INVESTMENT: BUY [TICKER]

Investment Thesis: [Description]
Current: $X → Fair Value: $Y → Target: $Z

Fundamentals:
• P/E: X
• Profit Margin: X%
• Revenue Growth: +X%

[Full instructions]
```

**Pass Criteria:** 
- Signal includes fair value
- DCF calculation shown
- Exit strategy included
- Trading 212 instructions clear

---

### Test 3: Trade Confirmation

**Steps:**
1. Receive a signal
2. Reply with `✅` or `placed order`

**Expected Response:**
```
✅ Trade Confirmed!

📊 TRACKING STARTED
• Ticker: [TICKER]
• Entry: $X
• Shares: X
• Stop Loss: $X
• Target: $X

I'll check on this trade daily!
```

**Pass Criteria:**
- Trade created in database
- Confirmation message received
- Trade appears in `/trades`

---

### Test 4: Trade Tracking Commands

**Commands to test:**
```
/trades
/portfolio
/performance
```

**Expected Results:**

**`/trades`:**
```
📊 OPEN TRADES

🟢 AAPL
• Entry: $150 → $155
• P&L: +$500 (+3.3%)
• Days: 1

Total: 1 open position(s)
```

**`/portfolio`:**
```
📊 PORTFOLIO SUMMARY

💰 Current Positions
• Open Trades: 1
• Total Value: $15,500
• Unrealized P&L: +$500
```

**`/performance`:**
```
📈 PERFORMANCE ANALYTICS

🎯 Trading Statistics
• Total Trades: 0
• Win Rate: 0%
```

**Pass Criteria:** All commands show correct data

---

### Test 5: Status Query

**Steps:**
1. Have an open trade
2. Send: `status AAPL` (replace with your ticker)

**Expected Response:**
```
📊 Trade Status: AAPL

💰 Current Position
• Entry: $150.00
• Current: $155.00
• P&L: +$500 (+3.3%)

🎯 Targets
• Target: $180 (+16.1% away)
• Stop Loss: $135 (+12.9% away)

⏰ Time
• Days Held: 1
```

**Pass Criteria:** Shows current price and P&L

---

### Test 6: Exit Confirmation

**Steps:**
1. Have an open trade
2. Send: `closed AAPL 100` (replace with your ticker and shares)

**Expected Response:**
```
✅ Trade Closed: AAPL

📊 FINAL RESULTS
• Entry: $150.00
• Exit: $155.00
• Shares: 100
• P&L: +$500 (+3.3%)
• Days Held: 1

🎉 Excellent trade!
```

**Pass Criteria:**
- Trade marked as closed in database
- P&L calculated correctly
- Trade removed from `/trades`

---

### Test 7: Company Research

**Command:**
```
/research AAPL
```

**Expected Response:**
```
🔍 RESEARCH REPORT: AAPL
Apple Inc.

📊 VALUATION
• P/E Ratio: X
• Score: X/100

💰 PROFITABILITY
• Profit Margin: X%
• Score: X/100

🎯 OVERALL SCORE: X/100
📊 RATING: [BUY/SELL/HOLD]
```

**Pass Criteria:**
- Report generated within 10 seconds
- All metrics populated
- Overall score calculated

---

### Test 8: Database Persistence

**Steps:**
1. Create a trade (reply `✅` to signal)
2. Restart the bot (or wait for Railway restart)
3. Check `/trades`

**Expected Result:** Trade still appears in `/trades`

**Pass Criteria:** Data persists across restarts

---

### Test 9: Daily Updates (Scheduled)

**Note:** This test requires waiting until next day

**Expected:** At 9:00 AM UK, receive:
```
📊 Daily Update: AAPL
• Current: $155.00 (+3.3%)
• Days held: 2
• Status: ✅ On track
```

**Pass Criteria:** Update received automatically

---

### Test 10: Error Handling

**Test invalid commands:**
```
/trades INVALID
/research
status
closed AAPL
```

**Expected:** Helpful error messages, no crashes

**Pass Criteria:** Bot handles errors gracefully

---

## 📊 Test Results Template

```
Test 1: Basic Bot Functionality
Status: [ ] Pass [ ] Fail
Notes: ___________________________

Test 2: Value Investment Strategy
Status: [ ] Pass [ ] Fail
Notes: ___________________________

Test 3: Trade Confirmation
Status: [ ] Pass [ ] Fail
Notes: ___________________________

Test 4: Trade Tracking Commands
Status: [ ] Pass [ ] Fail
Notes: ___________________________

Test 5: Status Query
Status: [ ] Pass [ ] Fail
Notes: ___________________________

Test 6: Exit Confirmation
Status: [ ] Pass [ ] Fail
Notes: ___________________________

Test 7: Company Research
Status: [ ] Pass [ ] Fail
Notes: ___________________________

Test 8: Database Persistence
Status: [ ] Pass [ ] Fail
Notes: ___________________________

Test 9: Daily Updates
Status: [ ] Pass [ ] Fail [ ] Pending
Notes: ___________________________

Test 10: Error Handling
Status: [ ] Pass [ ] Fail
Notes: ___________________________
```

---

## 🐛 Common Issues & Fixes

### Issue: Bot not responding
**Fix:** Check Railway logs, restart service

### Issue: Database error
**Fix:** Check if `data/` directory exists, check permissions

### Issue: Commands not recognized
**Fix:** Ensure bot handlers are registered in `initialize()`

### Issue: Trade not tracking
**Fix:** Check database connection, verify `create_trade()` called

### Issue: Wrong P&L calculation
**Fix:** Verify BUY/SELL logic in `update_trade_price()`

---

## 📝 Testing Notes

**Important:**
- Test with **small amounts** first
- Use **paper trading** mode if available
- Don't test with real money until fully verified
- Keep Railway logs open during testing
- Document any bugs found

**Performance Benchmarks:**
- Command response: < 2 seconds
- Research report: < 10 seconds
- Signal generation: < 30 seconds
- Database operations: < 1 second

---

## ✅ Sign-Off

Once all tests pass:
- [ ] All 10 tests completed
- [ ] No critical bugs found
- [ ] Performance acceptable
- [ ] Ready for production use

**Tested by:** _______________  
**Date:** _______________  
**Status:** [ ] Approved [ ] Needs work

---

## 🚀 Next Steps After Testing

1. Document any bugs found
2. Fix critical issues
3. Deploy fixes to Railway
4. Re-test failed tests
5. Mark as production-ready
6. Start using with real signals!

---

**Happy Testing!** 🧪
