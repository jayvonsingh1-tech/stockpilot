# StockPilot 🤖📈

**Automated Stock Trading Signal Bot with AI-Powered Analysis**

StockPilot is a reliable, high-confidence stock trading signal generator that analyzes UK (LSE) and US (NYSE/NASDAQ) markets using proven trading strategies, strict criteria, and machine learning. It sends actionable signals via Telegram with step-by-step Trading 212 instructions.

---

## Features

✅ **Phase 1 (Current):**
- Market data fetching for US + UK stocks (yfinance)
- Basic technical analysis (RSI, MACD, Bollinger Bands, EMAs, ATR, Stochastic)
- Telegram bot integration for notifications
- Configurable watchlist (includes Videndum and other stocks)
- Comprehensive logging system

🚧 **Coming in Phase 2:**
- Full technical indicator suite (15+ indicators)
- 4 proven trading strategies (Trend Following, Mean Reversion, Breakout, Value + Catalyst)
- 10-point mandatory criteria checklist
- 85% minimum confidence scoring
- Trading 212 step-by-step instructions in signals

🔮 **Future Phases:**
- Fundamental analysis & company research reports
- News sentiment analysis
- Machine learning pattern recognition
- Trade journal & performance tracking
- Weekly return optimization
- AI chat assistant (ask questions, make changes)
- Web dashboard (Streamlit)
- Live broker integration (optional)

---

## Installation

### Prerequisites

- Python 3.11 or higher
- Windows 11 (or Windows 10, macOS, Linux)

### Step 1: Clone or Download

Download the `stockpilot` folder to your Desktop (or preferred location).

### Step 2: Install Python Dependencies

Open Command Prompt in the `stockpilot` directory and run:

```bash
pip install -r requirements.txt
```

**Note:** If you encounter issues with `ta-lib`, you may need to install the TA-Lib C library first:
- Windows: Download from https://github.com/cgohlke/talib-build/releases
- macOS: `brew install ta-lib`
- Linux: `sudo apt-get install ta-lib`

For now, the bot works without TA-Lib (Phase 1 uses pandas-based indicators).

---

## Configuration

### 1. Telegram Bot Setup (Optional but Recommended)

To receive signals on Telegram:

1. **Create a Telegram bot:**
   - Open Telegram and search for `@BotFather`
   - Send `/newbot` and follow instructions
   - Copy the bot token (looks like `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`)

2. **Get your Chat ID:**
   - Start a chat with your new bot
   - Send any message to it
   - Visit: `https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates`
   - Find your `chat_id` in the response (a number like `123456789`)

3. **Add to config:**
   - Open `stockpilot/config/settings.yaml`
   - Find the `telegram` section
   - Add your `bot_token` and `chat_id`

```yaml
telegram:
  enabled: true
  bot_token: "YOUR_BOT_TOKEN_HERE"
  chat_id: "YOUR_CHAT_ID_HERE"
```

### 2. Customize Watchlist

Edit `stockpilot/config/watchlist.yaml` to add or remove stocks you want to monitor.

### 3. Adjust Settings

Edit `stockpilot/config/settings.yaml` to customize:
- Confidence thresholds (default: 85% minimum)
- Risk management parameters
- Trading strategies
- And more...

---

## Usage

### Run the Bot

From the `stockpilot` directory:

```bash
python main.py
```

The bot will:
1. Load configuration and watchlist
2. Initialize Telegram bot (if configured)
3. Test data fetching for your watchlist stocks
4. Display technical indicators for the first 3 stocks
5. Keep running (press Ctrl+C to stop)

### What to Expect (Phase 1)

Phase 1 is a **foundation build**. The bot will:
- ✅ Fetch real-time market data
- ✅ Calculate technical indicators
- ✅ Send test notifications to Telegram
- ❌ Not yet generate trading signals (coming in Phase 2)

---

## Project Structure

```
stockpilot/
├── config/
│   ├── settings.yaml          # Main configuration
│   ├── watchlist.yaml         # Stocks to monitor
│   ├── strategies.yaml        # Strategy parameters
│   └── criteria.yaml          # Signal criteria
├── src/
│   ├── data/
│   │   └── fetcher.py        # Market data fetching
│   ├── analysis/
│   │   └── technical.py      # Technical indicators
│   ├── notifications/
│   │   └── telegram_bot.py   # Telegram integration
│   └── utils/
│       ├── logger.py         # Logging system
│       ├── config.py         # Configuration loader
│       └── helpers.py        # Utility functions
├── logs/                      # Log files (created automatically)
├── main.py                    # Entry point
├── requirements.txt           # Python dependencies
└── README.md                  # This file
```

---

## Roadmap

### Phase 1: Foundation ✅ (Current)
- [x] Project structure
- [x] Configuration system
- [x] Market data fetcher
- [x] Basic technical analysis
- [x] Telegram bot setup
- [x] Main entry point

### Phase 2: Signal Generation (Next)
- [ ] Full technical indicator suite
- [ ] Chart pattern recognition
- [ ] 4 trading strategies implementation
- [ ] Mandatory criteria checklist
- [ ] Confidence scoring (85% minimum)
- [ ] Trading 212 instruction formatter
- [ ] Paper trading simulator

### Phase 3: Research & Fundamentals
- [ ] Fundamental analysis
- [ ] News scraping & sentiment
- [ ] Company research reports
- [ ] Watchlist monitoring & alerts
- [ ] Stock screening

### Phase 4: Intelligence & Learning
- [ ] ML pattern recognition
- [ ] Risk management system
- [ ] Backtesting framework
- [ ] Trade journal
- [ ] Weekly return tracker
- [ ] Model retraining pipeline

### Phase 5: AI Chat + Dashboard
- [ ] AI chat assistant (Ollama)
- [ ] Web dashboard (Streamlit)
- [ ] Interactive commands
- [ ] Performance visualization

### Phase 6: Live Broker Integration (Optional)
- [ ] Alpaca API (US stocks)
- [ ] IG Markets API (UK stocks)
- [ ] Auto-execution toggle
- [ ] Order management

---

## FAQ

### Q: Will this make me money?
**A:** No guarantees. All trading involves risk. This is a tool to help you make informed decisions, not financial advice. Start with paper trading and only risk money you can afford to lose.

### Q: Do I need to pay for anything?
**A:** No. All APIs used are free (yfinance, Telegram, etc.). If you later want to use premium AI models (Claude/GPT) for the chat assistant, that's optional.

### Q: Can I use this with Trading 212?
**A:** Yes! Signals will include step-by-step Trading 212 instructions. However, you execute trades manually (Phase 1-5). Auto-execution via broker APIs is optional in Phase 6.

### Q: How often will I get signals?
**A:** With an 85% confidence threshold, expect 1-3 high-quality signals per week. Quality over quantity.

### Q: Can I change the confidence threshold?
**A:** Yes, edit `config/settings.yaml` and change `signals.min_confidence`. Lower = more signals but less reliable.

### Q: What if I don't have Telegram?
**A:** The bot will still work and log everything to the console and log files. But Telegram is highly recommended for real-time alerts on your phone.

---

## Troubleshooting

### "ModuleNotFoundError: No module named 'yfinance'"
Run: `pip install -r requirements.txt`

### "Telegram bot token not configured"
Add your bot token and chat_id to `config/settings.yaml` (see Configuration section above)

### "No data returned for ticker"
- Check if the ticker symbol is correct
- UK stocks need `.L` suffix (e.g., `VID.L`)
- Some stocks may not be available on yfinance

### "Error calculating indicators"
This is normal if there's insufficient data. The bot needs at least 200 candles for some indicators (like SMA 200).

---

## Contributing

This is a personal project for Jayvon. Future phases will be built iteratively.

---

## Disclaimer

**This software is for educational and informational purposes only. It is not financial advice.**

- All trading involves risk of loss
- Past performance does not guarantee future results
- Never risk more than you can afford to lose
- The bot's signals are suggestions, not recommendations
- Always do your own research before trading
- The developers are not responsible for any financial losses

---

## License

Private project - All rights reserved.

---

## Support

For issues or questions during development, refer to the architecture plan at `plans/trading-bot-architecture.md`.

---

**Built with ❤️ for reliable, high-confidence trading signals.**
