# 🤖 Phase 5 Setup Guide - Conversational AI

**Last Updated**: 2026-06-22  
**Status**: Ready to Deploy  
**Cost**: 100% FREE

---

## 🎯 What You're Setting Up

Phase 5 adds **conversational AI** to StockPilot, allowing you to:
- Ask questions naturally about your portfolio
- Get AI-powered insights and analysis
- Have conversations about trading strategies
- Query market data conversationally

**All using FREE AI APIs!**

---

## 📋 Prerequisites

1. StockPilot already installed and running
2. Python 3.10+ with pip
3. 5 minutes to get a free API key

---

## 🚀 Quick Setup (3 Steps)

### Step 1: Install AI Packages

```bash
pip install groq google-generativeai requests
```

### Step 2: Get a FREE API Key

Choose ONE (or all three for automatic fallback):

#### Option A: Groq (BEST - Recommended) ⭐
- **Speed**: 70+ tokens/second (fastest)
- **Model**: llama-3.3-70b-versatile (70B parameters)
- **Limit**: 30 requests/minute FREE
- **Sign up**: https://console.groq.com/

1. Go to https://console.groq.com/
2. Sign up with Google/GitHub (30 seconds)
3. Click "API Keys" → "Create API Key"
4. Copy your key (starts with `gsk_...`)

#### Option B: Google Gemini (EXCELLENT) 🌟
- **Speed**: Very fast
- **Model**: gemini-2.0-flash-exp (Google's latest)
- **Limit**: 1500 requests/day FREE
- **Sign up**: https://aistudio.google.com/

1. Go to https://aistudio.google.com/
2. Sign in with Google account
3. Click "Get API Key" → "Create API Key"
4. Copy your key

#### Option C: OpenRouter (GOOD) ✅
- **Speed**: Fast
- **Model**: llama-3.1-8b-instruct (8B parameters)
- **Limit**: Unlimited FREE
- **Sign up**: https://openrouter.ai/

1. Go to https://openrouter.ai/
2. Sign up
3. Go to Keys → Create Key
4. Copy your key

### Step 3: Add API Key to Config

#### Method A: Environment Variable (Recommended)

**Windows:**
```powershell
$env:GROQ_API_KEY="your-groq-key-here"
# OR
$env:GOOGLE_API_KEY="your-google-key-here"
# OR
$env:OPENROUTER_API_KEY="your-openrouter-key-here"
```

**Linux/Mac:**
```bash
export GROQ_API_KEY="your-groq-key-here"
# OR
export GOOGLE_API_KEY="your-google-key-here"
# OR
export OPENROUTER_API_KEY="your-openrouter-key-here"
```

#### Method B: Add to config/settings.yaml

```yaml
# Add to config/settings.yaml
telegram:
  bot_token: "your-telegram-token"
  chat_id: "your-chat-id"
  
# Phase 5: Conversational AI (Optional)
ai:
  groq_api_key: "your-groq-key-here"  # BEST
  google_api_key: "your-google-key-here"  # EXCELLENT
  openrouter_api_key: "your-openrouter-key-here"  # GOOD
```

---

## ✅ Verify Setup

Run this test:

```python
from src.notifications.conversation_handler import create_conversation_handler

handler = create_conversation_handler()
print(f"AI Available: {handler.is_available()}")
print(f"Provider: {handler.active_provider}")
```

Expected output:
```
AI Available: True
Provider: Groq (llama-3.3-70b)
```

---

## 💬 How to Use

### In Telegram:

**Before Phase 5:**
```
You: "How's my portfolio?"
Bot: "Send me a ticker symbol (e.g., AAPL) or use /help for commands"
```

**After Phase 5:**
```
You: "How's my portfolio?"
Bot: "Your portfolio is performing well! 📊

Current Status:
• 3 open positions
• Total value: $15,450
• Unrealized P&L: +$1,230 (+8.6%)

Top Performer: AAPL (+15.2%)
Needs Attention: TSLA (-3.1%)

Your all-time win rate is 68% with 45 total trades.
Would you like details on any specific position?"
```

### Example Conversations:

**Portfolio Questions:**
- "How's my portfolio doing?"
- "What are my best trades?"
- "Show me my performance"
- "Which stocks am I holding?"

**Strategy Questions:**
- "Which strategy works best for me?"
- "Why did my last trade lose money?"
- "Should I take more Trend Following signals?"

**Market Questions:**
- "Should I buy AAPL?"
- "What's the price of TSLA?"
- "Tell me about NVDA"

**General Questions:**
- "How can I improve my win rate?"
- "What should I focus on?"
- "Give me trading advice"

---

## 🔄 Automatic Fallback

The bot tries providers in this order:
1. **Groq** (if key provided) - BEST
2. **Google Gemini** (if key provided) - EXCELLENT
3. **OpenRouter** (if key provided) - GOOD
4. **Fallback** (basic responses without AI)

You can provide multiple keys for redundancy!

---

## 📊 API Comparison

| Provider | Model | Speed | Limit | Quality | Setup |
|----------|-------|-------|-------|---------|-------|
| **Groq** | llama-3.3-70b | ⚡⚡⚡ Fastest | 30/min | ⭐⭐⭐⭐⭐ Best | 30 sec |
| **Google** | gemini-2.0-flash | ⚡⚡ Very Fast | 1500/day | ⭐⭐⭐⭐⭐ Excellent | 1 min |
| **OpenRouter** | llama-3.1-8b | ⚡ Fast | Unlimited | ⭐⭐⭐⭐ Good | 2 min |

**Recommendation**: Use Groq for best results!

---

## 🐛 Troubleshooting

### "AI not available" message

**Problem**: No API key configured

**Solution**:
1. Get a free API key (see Step 2 above)
2. Add it as environment variable or in config
3. Restart the bot

### "Groq API error"

**Problem**: Invalid API key or rate limit

**Solution**:
1. Check your API key is correct
2. Wait 1 minute if rate limited
3. Bot will automatically try next provider

### "Import error: No module named 'groq'"

**Problem**: AI packages not installed

**Solution**:
```bash
pip install groq google-generativeai requests
```

---

## 💰 Cost Breakdown

| Component | Cost |
|-----------|------|
| Groq API | **$0.00** (30 req/min free) |
| Google Gemini | **$0.00** (1500 req/day free) |
| OpenRouter | **$0.00** (unlimited free) |
| **Total** | **$0.00** |

**You can run Phase 5 forever without paying anything!**

---

## 🎓 Advanced Configuration

### Multiple API Keys (Recommended)

For maximum reliability, add all three:

```yaml
ai:
  groq_api_key: "gsk_..."  # Primary (fastest)
  google_api_key: "AIza..."  # Backup (excellent)
  openrouter_api_key: "sk-..."  # Fallback (unlimited)
```

The bot will automatically use the best available provider.

### Custom System Prompt

Edit `src/notifications/conversation_handler.py` to customize the AI's personality and behavior.

---

## 📱 Example Session

```
You: Hi!
Bot: Hello! I'm your StockPilot AI assistant. How can I help you today?

You: How's my portfolio?
Bot: Your portfolio is up +8.6% with 3 open positions worth $15,450. 
     Your best performer is AAPL (+15.2%). Want details?

You: Yes, tell me about AAPL
Bot: AAPL is your top performer:
     • Entry: $150.00
     • Current: $172.80 (+15.2%)
     • Unrealized gain: $2,280
     • Days held: 45
     
     The stock is in a strong uptrend. Consider taking partial profits 
     at $180 or holding for long-term growth. Use /research AAPL for 
     detailed analysis.

You: Should I buy more?
Bot: Based on your trading style (68% win rate, prefer Trend Following), 
     AAPL looks good for adding to your position. However, wait for a 
     dip to $165-168 for a better entry. Set a price alert!

You: Thanks!
Bot: You're welcome! Keep up the great trading! 🚀
```

---

## 🚀 Next Steps

1. ✅ Install AI packages
2. ✅ Get free API key (Groq recommended)
3. ✅ Add to config
4. ✅ Restart bot
5. ✅ Start chatting!

---

## 📚 Additional Resources

- **Groq Documentation**: https://console.groq.com/docs
- **Google AI Studio**: https://ai.google.dev/
- **OpenRouter Docs**: https://openrouter.ai/docs

---

## 🎉 You're Done!

Your bot can now have natural conversations about trading!

Try asking:
- "How's my portfolio?"
- "What should I trade today?"
- "Analyze my performance"
- "Should I buy AAPL?"

**Enjoy your FREE AI-powered trading assistant!** 🤖📈
