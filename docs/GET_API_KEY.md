# 🚀 Get Your FREE AI API Key (30 Seconds!)

## Option 1: Groq (RECOMMENDED - BEST & FASTEST) ⭐

**Why Groq?**
- Fastest AI (70+ tokens/second)
- Best model (llama-3.3-70b - 70 billion parameters)
- 30 requests/minute FREE
- No credit card required

**Steps (30 seconds):**

1. **Go to**: https://console.groq.com/

2. **Click "Sign In"** (top right)

3. **Sign in with Google or GitHub** (1 click - no forms!)

4. **Click "API Keys"** (left sidebar)

5. **Click "Create API Key"**

6. **Copy your key** (starts with `gsk_...`)

7. **Done!** ✅

---

## Option 2: Google Gemini (EXCELLENT - ALSO GREAT) 🌟

**Why Google?**
- Google's latest AI model
- 1500 requests/day FREE
- Very fast
- No credit card required

**Steps (1 minute):**

1. **Go to**: https://aistudio.google.com/

2. **Sign in with Google account**

3. **Click "Get API Key"** (top right)

4. **Click "Create API Key"**

5. **Copy your key** (starts with `AIza...`)

6. **Done!** ✅

---

## Option 3: OpenRouter (GOOD - UNLIMITED) ✅

**Why OpenRouter?**
- Unlimited requests FREE
- Good quality
- No credit card required

**Steps (1 minute):**

1. **Go to**: https://openrouter.ai/

2. **Click "Sign Up"**

3. **Sign up with email**

4. **Go to "Keys"** tab

5. **Click "Create Key"**

6. **Copy your key** (starts with `sk-...`)

7. **Done!** ✅

---

## 🔧 Add API Key to StockPilot

Once you have your key, run ONE of these commands:

### Windows (PowerShell):
```powershell
# For Groq (RECOMMENDED)
$env:GROQ_API_KEY="paste-your-key-here"

# OR for Google
$env:GOOGLE_API_KEY="paste-your-key-here"

# OR for OpenRouter
$env:OPENROUTER_API_KEY="paste-your-key-here"
```

### Linux/Mac (Terminal):
```bash
# For Groq (RECOMMENDED)
export GROQ_API_KEY="paste-your-key-here"

# OR for Google
export GOOGLE_API_KEY="paste-your-key-here"

# OR for OpenRouter
export OPENROUTER_API_KEY="paste-your-key-here"
```

---

## ✅ Verify It Works

Run this:
```bash
python test_phase5_ai.py
```

You should see:
```
✅ Groq AI initialized (BEST - 70B model, 30 req/min)
Provider: Groq (llama-3.3-70b)
```

---

## 💬 Start Chatting!

Now just talk to your bot naturally:

- "How's my portfolio?"
- "What are my best trades?"
- "Should I buy AAPL?"
- "Which strategy works best for me?"

---

## 🎯 Quick Comparison

| Provider | Speed | Quality | Limit | Setup Time |
|----------|-------|---------|-------|------------|
| **Groq** | ⚡⚡⚡ Fastest | ⭐⭐⭐⭐⭐ Best | 30/min | 30 sec |
| **Google** | ⚡⚡ Very Fast | ⭐⭐⭐⭐⭐ Excellent | 1500/day | 1 min |
| **OpenRouter** | ⚡ Fast | ⭐⭐⭐⭐ Good | Unlimited | 1 min |

**My Recommendation**: Use Groq! It's the fastest and best quality.

---

## 🐛 Troubleshooting

### "Can't find the API key page"
- Make sure you're signed in
- Look for "API Keys" in the left sidebar (Groq)
- Or "Get API Key" button at top (Google)

### "Key doesn't work"
- Make sure you copied the entire key
- Check for extra spaces at the beginning/end
- Make sure you're using the right environment variable name

### "Still not working"
- Restart your terminal after setting the environment variable
- Or restart the bot
- Or try a different provider

---

## 💡 Pro Tip

You can add multiple API keys for automatic fallback:

```powershell
$env:GROQ_API_KEY="your-groq-key"
$env:GOOGLE_API_KEY="your-google-key"
$env:OPENROUTER_API_KEY="your-openrouter-key"
```

The bot will automatically use the best available!

---

## 🎉 That's It!

Getting an API key takes literally 30 seconds. Just:
1. Go to the website
2. Sign in with Google/GitHub
3. Click "Create API Key"
4. Copy and paste

**You'll be chatting with your AI trading assistant in under a minute!** 🤖📈
