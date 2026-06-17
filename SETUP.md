# StockPilot - Setup Guide

## Phase 1 Setup Instructions

### Step 1: Install Python

1. Download Python 3.11 or higher from https://www.python.org/downloads/
2. **IMPORTANT:** During installation, check "Add Python to PATH"
3. Verify installation by opening Command Prompt and typing:
   ```
   python --version
   ```
   You should see: `Python 3.11.x` or higher

### Step 2: Install Dependencies

1. Open Command Prompt
2. Navigate to the stockpilot directory:
   ```
   cd C:\Users\jayvo\Desktop\stockpilot
   ```
3. Install required packages:
   ```
   pip install -r requirements.txt
   ```

**Note:** If you get an error about `ta-lib`, you can skip it for now. Phase 1 works without it.

### Step 3: Configure Telegram Bot (Optional)

1. **Create a Telegram Bot:**
   - Open Telegram app
   - Search for `@BotFather`
   - Send `/newbot` command
   - Follow the instructions to create your bot
   - Copy the bot token (looks like: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`)

2. **Get Your Chat ID:**
   - Start a chat with your new bot
   - Send any message to it
   - Open this URL in your browser (replace YOUR_BOT_TOKEN):
     ```
     https://api.telegram.org/botYOUR_BOT_TOKEN/getUpdates
     ```
   - Look for `"chat":{"id":123456789}` in the response
   - Copy that number (your chat_id)

3. **Update Configuration:**
   - Open `stockpilot/config/settings.yaml`
   - Find the `telegram` section
   - Replace the empty strings:
     ```yaml
     telegram:
       enabled: true
       bot_token: "123456789:ABCdefGHIjklMNOpqrsTUVwxyz"  # Your bot token
       chat_id: "123456789"  # Your chat ID
     ```

### Step 4: Run StockPilot

1. In Command Prompt (in the stockpilot directory):
   ```
   python main.py
   ```

2. You should see:
   - Configuration loading
   - Watchlist loaded (8 stocks)
   - Telegram bot initialized (if configured)
   - Data fetching test for first 3 stocks
   - Technical indicators calculated
   - "Phase 1 Setup Complete!" message

3. Press `Ctrl+C` to stop the bot

### Step 5: Verify Everything Works

Check that you see:
- ✅ No errors in the console
- ✅ Log file created in `stockpilot/logs/stockpilot.log`
- ✅ Stock data fetched successfully (prices, indicators)
- ✅ Telegram message received (if configured)

---

## Troubleshooting

### "python is not recognized"
- Python is not installed or not in PATH
- Reinstall Python and check "Add Python to PATH"

### "pip is not recognized"
- Try `python -m pip install -r requirements.txt` instead

### "No module named 'yfinance'"
- Run: `pip install yfinance pandas numpy pyyaml python-telegram-bot pytz`

### "Telegram bot token not configured"
- This is OK for testing
- The bot will work without Telegram, just no notifications
- Add your token later when ready

### "No data returned for ticker"
- Check internet connection
- Some tickers may not be available on yfinance
- UK stocks need `.L` suffix (e.g., `VID.L`)

### "Error calculating indicators"
- This can happen if there's not enough historical data
- It's normal for some indicators (like SMA 200)
- The bot will still work with available indicators

---

## What's Next?

Phase 1 is complete! You now have:
- ✅ Working project structure
- ✅ Configuration system
- ✅ Market data fetching
- ✅ Technical analysis
- ✅ Telegram bot integration
- ✅ Logging system

**Phase 2 will add:**
- Signal generation with 85% confidence threshold
- 4 trading strategies
- 10-point mandatory criteria
- Trading 212 step-by-step instructions
- Paper trading simulator

---

## Testing Checklist

Before moving to Phase 2, verify:

- [ ] Python 3.11+ installed
- [ ] All dependencies installed (`pip install -r requirements.txt`)
- [ ] Bot runs without errors (`python main.py`)
- [ ] Data fetched for watchlist stocks
- [ ] Technical indicators calculated
- [ ] Telegram bot connected (optional)
- [ ] Logs created in `logs/` directory

---

## Need Help?

- Check the README.md for detailed documentation
- Review the architecture plan in `plans/trading-bot-architecture.md`
- Check log files in `logs/stockpilot.log` for errors

---

**Phase 1 Complete! 🎉**

The foundation is solid. Ready to build Phase 2 when you are!
