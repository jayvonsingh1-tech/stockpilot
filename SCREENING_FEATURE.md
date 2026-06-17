# Daily Stock Screening Feature

## 🎯 Overview

StockPilot now automatically screens 100+ stocks daily to find the best investment opportunities and recommends them for your watchlist!

## ✨ What It Does

Every morning at **8:00 AM** (before market open), the bot:

1. **Screens 100+ stocks** across US (NASDAQ/NYSE) and UK (LSE) markets
2. **Analyzes each stock** across 4 dimensions:
   - **Technical Analysis** (trend, RSI, MACD, ADX)
   - **Fundamental Analysis** (P/E ratio, profit margins, debt, ROE)
   - **Momentum** (1-month and 3-month performance)
   - **Value** (P/B ratio, dividend yield)
3. **Scores each stock** out of 100
4. **Recommends top 10** stocks scoring 70+ points
5. **Sends detailed report** via Telegram
6. **Generates research report** for the #1 candidate (if score >= 85)

## 📊 Scoring System

Each stock gets scored across 4 categories:

### Technical Score (0-100)
- Trend alignment (EMA20 > EMA50 > SMA200)
- RSI in healthy range (40-60)
- Strong trend strength (ADX > 25)
- Bullish MACD

### Fundamental Score (0-100)
- Low P/E ratio (< 15 = undervalued)
- High profit margins (> 20%)
- Strong revenue growth (> 10%)
- Low debt-to-equity (< 50)
- High ROE (> 20%)

### Momentum Score (0-100)
- 1-month performance (> 5% = good)
- 3-month performance (> 10% = good)

### Value Score (0-100)
- Low P/B ratio (< 1 = undervalued)
- Good dividend yield (> 4%)

**Total Score** = Weighted average:
- Technical: 30%
- Fundamental: 30%
- Momentum: 25%
- Value: 15%

## 📱 Telegram Message Format

You'll receive a message like this:

```
📊 DAILY STOCK SCREENING RESULTS
Monday, 16 June 2026

Found 5 high-quality investment opportunities:

━━━━━━━━━━━━━━━━━━━━━━━━━━━

🟢 #1. AAPL - Apple Inc.
📊 Overall Score: 87/100
🏢 Sector: Technology
💰 Price: $150.00

📈 Scores:
• Technical: 85/100
• Fundamental: 90/100
• Momentum: 88/100
• Value: 75/100

✅ STRONG BUY - Add to watchlist immediately

Reasons: Strong technical setup, Solid fundamentals, Positive momentum

━━━━━━━━━━━━━━━━━━━━━━━━━━━

[... more stocks ...]

💡 RECOMMENDATION:
Add the top 3 stocks to your watchlist for monitoring.

These stocks scored 70+ across technical, fundamental, momentum, and value metrics.
```

## 🔍 Research Reports

For stocks scoring **85+**, you'll automatically receive a detailed research report including:

- **Company Overview** (sector, industry, market cap)
- **Financial Health** (profit margins, debt, cash flow)
- **Valuation** (P/E, P/B, assessment)
- **Growth** (revenue growth, earnings growth)
- **Technical Setup** (current trend, RSI, support/resistance)
- **Risk Factors** (identified concerns)
- **Bot Assessment** (overall recommendation and action)

## 🎯 Recommendations

The bot provides clear recommendations:

| Score | Recommendation | Action |
|-------|---------------|--------|
| 85-100 | **STRONG BUY** | Add to watchlist immediately |
| 75-84 | **BUY** | Strong candidate for watchlist |
| 70-74 | **CONSIDER** | Worth monitoring |
| < 70 | **PASS** | Not recommended |

## 📅 Schedule

- **Daily Screening**: 8:00 AM (Mon-Fri, before market open)
- **Screening Results**: Sent via Telegram
- **Research Report**: Automatically generated for top candidate

## 🔧 Customization

You can adjust the screening in [`src/analysis/screener.py`](src/analysis/screener.py:1):

- **Stock universe**: Add/remove tickers from `us_stocks` and `uk_stocks` lists
- **Minimum score**: Change threshold (default: 70)
- **Max results**: Change `max_results` parameter (default: 10)
- **Scoring weights**: Adjust weights in `_evaluate_stock()` method

## 💡 How to Use

### 1. Review Daily Recommendations
Every morning, check your Telegram for new opportunities

### 2. Add to Watchlist
Add recommended stocks to your watchlist in [`config/watchlist.yaml`](config/watchlist.yaml:1):

```yaml
- ticker: "AAPL"
  name: "Apple Inc."
  sector: "Technology"
  notes: "Recommended by daily screening - 87/100 score"
```

### 3. Monitor for Signals
Once added to watchlist, the bot will:
- Scan every 15 minutes for trading signals
- Alert you when high-confidence setups appear
- Provide Trading 212 instructions

## 🚀 Benefits

✅ **Discover new opportunities** - Don't miss great stocks
✅ **Data-driven decisions** - Based on 4 analysis dimensions
✅ **Save time** - Automated screening of 100+ stocks
✅ **Thorough research** - Detailed reports for top candidates
✅ **Proactive recommendations** - Delivered before market open

## 📈 Example Workflow

1. **8:00 AM** - Receive daily screening results
2. **Review** - Check top 3-5 recommendations
3. **Research** - Read detailed report for #1 candidate
4. **Add to watchlist** - Add promising stocks
5. **Wait for signals** - Bot monitors and alerts on setups
6. **Execute trades** - Follow Trading 212 instructions

## 🔍 Stock Universe

Currently screens:
- **80+ US stocks** (Tech, Finance, Healthcare, Consumer, Industrial, Energy, Retail, Semiconductors)
- **24+ UK stocks** (FTSE 100 major stocks)

Total: **100+ stocks** screened daily

## ⚙️ Technical Details

- **Screening time**: ~5-10 minutes (depending on API rate limits)
- **Data source**: yfinance (free, reliable)
- **Analysis depth**: 6 months of historical data
- **Indicators**: 15+ technical indicators
- **Fundamental metrics**: 10+ financial ratios

## 🎯 Next Steps

This feature is part of **Phase 3** - Research and Fundamentals. Future enhancements:

- News sentiment analysis
- Insider trading tracking
- Sector rotation detection
- Custom screening criteria
- Interactive commands (`/screen`, `/research TICKER`)

---

**The bot now finds opportunities for you, so you never miss a great investment!** 🚀
