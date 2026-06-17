# StockPilot - Quick Start Guide

## 🚀 Getting Started

### 1. Install Dependencies
```bash
cd stockpilot
pip install -r requirements.txt
```

**Note**: TA-Lib requires the C library to be installed first. See [SETUP.md](SETUP.md) for details.

### 2. Configure Settings

Edit `config/settings.yaml`:
- Set your Telegram bot token and chat ID
- Adjust confidence threshold (default: 85%)
- Configure risk parameters

### 3. Set Up Watchlist

Edit `config/watchlist.yaml`:
- Add stocks you want to monitor
- Include both US (AAPL, MSFT) and UK (VOD.L, BP.L) stocks

### 4. Run the Bot

```bash
python main.py
```

The bot will:
- Connect to Telegram
- Load your watchlist
- Scan for trading signals
- Send signals that meet 85% confidence threshold

---

## 📱 Telegram Commands (Coming in Phase 3)

Future commands will include:
- `/watchlist` - View your watchlist
- `/add TICKER` - Add stock to watchlist
- `/remove TICKER` - Remove from watchlist
- `/research TICKER` - Get research report
- `/performance` - View performance stats
- `/pause` - Pause the bot
- `/resume` - Resume the bot

---

## 🎯 Current Features (Phase 2 Complete)

✅ **Signal Generation**
- 3 trading strategies (Trend, Mean Reversion, Breakout)
- 85% minimum confidence threshold
- 10-point mandatory criteria validation

✅ **Risk Management**
- 2% max risk per trade
- 3% daily loss limit
- Position sizing based on confidence
- Max 5 concurrent positions

✅ **Telegram Delivery**
- Clear buy/sell signals
- Entry, stop loss, take profit levels
- Trading 212 step-by-step instructions
- Confidence score and reasoning

✅ **Scheduled Scanning**
- Market open scan (9:30 AM ET)
- 15-minute scans (9:30 AM - 4:00 PM ET)
- Market close scan (4:00 PM ET)
- Daily summary (9:30 PM UK, after all markets close)
- Weekly report (Sunday 6:00 PM)

---

## 📊 Signal Example

When the bot finds a high-confidence setup, you'll receive:

```
🚀 TRADING SIGNAL

📈 BUY AAPL (Apple Inc.)
💰 Entry: $150.00
🛑 Stop Loss: $145.00 (-3.3%)
✅ TP1: $156.00 (+4.0%) | TP2: $160.00 | TP3: $165.00

📊 Strategy: Trend Following
⏰ Timeframe: Swing Trade (3-7 days)
🎯 Confidence: 90%
💼 Risk/Reward: 3.0:1

💡 Reasoning:
• Strong uptrend confirmed
• Price pulled back to EMA20 support
• ADX shows strong trend strength
```

---

## 🔧 Adjusting Settings

### Lower Confidence Threshold (More Signals)
In `config/settings.yaml`:
```yaml
signals:
  min_confidence: 80  # Lower = more signals (but lower quality)
```

### Increase Risk per Trade
```yaml
risk:
  max_risk_per_trade_percent: 3.0  # Higher = larger positions
```

### Change Scan Frequency
Edit `src/scheduler.py` to adjust scan times.

---

## 📈 What's Next?

**Phase 3** will add:
- Fundamental analysis (P/E, revenue, debt)
- News scraping and sentiment analysis
- Company research reports
- Watchlist monitoring with alerts
- Interactive Telegram commands

**Phase 4** will add:
- Paper trading simulator
- Performance tracking and analytics
- Machine learning pattern recognition
- Backtesting framework
- Weekly return optimization

---

## 🐛 Troubleshooting

### No Signals Generated
- Check if confidence threshold is too high (try 80%)
- Verify watchlist has valid tickers
- Check logs: `logs/stockpilot.log`

### Telegram Not Working
- Verify bot token and chat ID in `config/settings.yaml`
- Test bot with `/start` command in Telegram
- Check internet connection

### Data Fetch Errors
- yfinance may be rate-limited (wait a few minutes)
- Some tickers may not have enough historical data
- Check ticker format (US: AAPL, UK: VOD.L)

---

## 📞 Support

For issues or questions:
1. Check `logs/stockpilot.log` for error messages
2. Review [PHASE2_COMPLETE.md](PHASE2_COMPLETE.md) for detailed documentation
3. Verify all configuration files are properly set up

---

**Happy Trading! 🚀**

*Remember: This bot generates signals for you to execute manually on Trading 212. Always review signals before trading.*
