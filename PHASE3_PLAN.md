# 🔍 StockPilot Phase 3 - Complete Plan
## Research, Fundamental Analysis & News Intelligence

---

## 📋 Overview

Phase 3 transforms StockPilot from a technical analysis bot into a comprehensive investment research assistant that provides deep fundamental analysis, real-time news monitoring, earnings tracking, and detailed company research reports.

---

## 🎯 Core Objectives

1. **Fundamental Analysis** - P/E ratios, revenue growth, profitability metrics
2. **News & Sentiment Analysis** - Real-time news monitoring and sentiment scoring
3. **Company Research Reports** - Comprehensive 10-point analysis
4. **Earnings Calendar** - Track and alert on upcoming earnings
5. **Watchlist Intelligence** - Proactive monitoring and alerts
6. **Stock Screening** - Find new opportunities automatically
7. **Sector Analysis** - Industry trends and comparisons
8. **Insider Trading Tracking** - Monitor insider buys/sells
9. **Analyst Ratings** - Track analyst upgrades/downgrades
10. **Economic Calendar** - Major economic events and impact

---

## 🆕 Core Features

### 1. Comprehensive Company Research

**Command:** `/research <ticker>`

#### Example Output:
```
🔍 DEEP RESEARCH REPORT - AAPL
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 COMPANY OVERVIEW
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• Name: Apple Inc.
• Sector: Technology
• Industry: Consumer Electronics
• Market Cap: $2.85T
• Employees: 164,000
• Founded: 1976
• CEO: Tim Cook

💰 CURRENT PRICE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• Price: $185.50
• Day Change: +$2.30 (+1.25%)
• 52-Week Range: $142.50 - $198.23
• Volume: 52.3M (Avg: 48.2M)

📈 FUNDAMENTAL METRICS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• P/E Ratio: 29.5 (Industry: 25.3)
• Forward P/E: 26.8
• PEG Ratio: 2.1
• Price/Sales: 7.2
• Price/Book: 42.5
• Debt/Equity: 1.98
• Current Ratio: 0.98
• Quick Ratio: 0.85

💵 PROFITABILITY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• Revenue (TTM): $383.9B
• Revenue Growth (YoY): +2.1%
• Gross Margin: 44.1%
• Operating Margin: 29.8%
• Net Margin: 25.3%
• ROE: 147.2%
• ROA: 22.4%
• ROIC: 38.5%

💰 EARNINGS & DIVIDENDS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• EPS (TTM): $6.29
• EPS Growth (YoY): +10.2%
• Next Earnings: July 28, 2026 (41 days)
• Dividend Yield: 0.52%
• Dividend/Share: $0.96
• Payout Ratio: 15.3%
• 5-Year Dividend Growth: 7.2%

📊 ANALYST RATINGS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• Strong Buy: 18
• Buy: 12
• Hold: 8
• Sell: 2
• Strong Sell: 0
• Average Target: $205.00 (+10.5%)
• High Target: $240.00 (+29.4%)
• Low Target: $165.00 (-11.0%)

🎯 STOCKPILOT SCORE: 8.2/10
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ STRENGTHS (6)
• Strong brand and ecosystem
• Excellent profit margins (25.3%)
• High return on equity (147%)
• Consistent dividend growth
• Strong balance sheet
• Market leader in premium segment

⚠️ CONCERNS (2)
• High P/E ratio vs industry
• Slowing revenue growth (2.1%)

📰 RECENT NEWS (Last 7 Days)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. ⬆️ Goldman Sachs upgrades to Buy
   Target: $210 → $225
   2 days ago

2. 📱 Apple announces new AI features
   Sentiment: Very Positive
   3 days ago

3. 📊 Q2 earnings beat expectations
   EPS: $1.52 vs $1.48 expected
   5 days ago

🔮 INSIDER ACTIVITY (Last 90 Days)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• Insider Buys: 3 ($2.4M)
• Insider Sells: 12 ($45.2M)
• Net Activity: -$42.8M (Slightly Bearish)

📈 TECHNICAL ANALYSIS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• Trend: Uptrend ✅
• RSI: 58 (Neutral)
• MACD: Bullish crossover
• Support: $180, $175
• Resistance: $190, $198
• 50-Day MA: $178.50 (Above)
• 200-Day MA: $165.20 (Above)

🎯 INVESTMENT RECOMMENDATION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Rating: BUY ⭐⭐⭐⭐
Confidence: 85%

Reasoning:
• Strong fundamentals with excellent margins
• Positive analyst sentiment
• Technical uptrend intact
• Upcoming earnings likely positive
• AI initiatives driving growth

Entry: $183-$187
Target: $205 (6-12 months)
Stop Loss: $175

[📊 View Charts] [📰 More News] [🔔 Set Alert]
```

---

### 2. Real-Time News Monitoring

**Automatic News Alerts:**

```
🚨 BREAKING NEWS - AAPL
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📰 Apple Announces Major AI Partnership

Source: Reuters
Published: 2 minutes ago
Sentiment: Very Positive (0.85)

Summary:
Apple announced a strategic partnership with 
OpenAI to integrate advanced AI features into 
iOS 18. Stock up 3.2% in after-hours trading.

Impact Analysis:
• Positive for long-term growth
• May boost services revenue
• Competitive advantage vs Android

Current Price: $188.50 (+3.2%)
Your Position: 100 shares @ $185
Unrealized P&L: +$350 (+1.9%)

[📰 Read Full Article] [📊 View Chart]
```

**Command:** `/news <ticker>`

```
📰 NEWS FEED - AAPL (Last 24 Hours)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. ⬆️ VERY POSITIVE (0.92)
   "Apple's AI Features Impress Analysts"
   Bloomberg - 2 hours ago
   
2. ➡️ NEUTRAL (0.05)
   "Apple Supplier Reports Strong Demand"
   WSJ - 5 hours ago
   
3. ⬆️ POSITIVE (0.65)
   "iPhone Sales Beat Expectations in China"
   CNBC - 8 hours ago

4. ⬇️ SLIGHTLY NEGATIVE (-0.25)
   "Apple Faces Regulatory Scrutiny in EU"
   FT - 12 hours ago

Overall Sentiment: Positive (0.59)
News Volume: High (24 articles)

[📰 View All News] [🔔 Set News Alert]
```

---

### 3. Earnings Calendar & Tracking

**Command:** `/earnings` or `/earnings <ticker>`

```
📅 EARNINGS CALENDAR
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔴 THIS WEEK
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• TSLA - Tomorrow (June 18)
  Expected EPS: $0.82
  Estimated: $0.78
  Time: After Market Close
  
• NVDA - Friday (June 21)
  Expected EPS: $5.25
  Estimated: $5.10
  Time: After Market Close

🟡 NEXT WEEK
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• AAPL - June 25
• MSFT - June 26
• GOOGL - June 27

🟢 YOUR WATCHLIST (Next 30 Days)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• AAPL - July 28 (41 days)
• MSFT - July 30 (43 days)
• GOOGL - August 1 (45 days)

[🔔 Set Earnings Alerts] [📊 View History]
```

**Automatic Earnings Alerts:**

```
⚠️ EARNINGS ALERT - AAPL
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📅 Earnings Tomorrow (July 28)
⏰ After Market Close (4:00 PM ET)

📊 EXPECTATIONS
• EPS Estimate: $1.48
• Revenue Estimate: $95.2B
• Analyst Consensus: Beat expected

📈 HISTORICAL PERFORMANCE
• Last 4 Quarters: 3 beats, 1 miss
• Avg Post-Earnings Move: +3.2%
• Last Quarter: Beat by $0.04

🎯 TRADING STRATEGY
• Consider closing positions before earnings
• High volatility expected
• Options implied move: ±5%

Your Position: 100 shares @ $185
Current Price: $188.50
Unrealized P&L: +$350

[Close Position] [Hold Through] [Add Alert]
```

---

### 4. Advanced Stock Screening

**Command:** `/screen` or `/screen <criteria>`

```
🔍 STOCK SCREENER
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Select Screening Criteria:

📊 PRE-BUILT SCREENS
[Value Stocks] [Growth Stocks] [Dividend Stocks]
[Momentum Plays] [Breakout Candidates]
[Undervalued Tech] [High ROE Stocks]

⚙️ CUSTOM SCREEN
[Build Custom Screen]

📈 POPULAR SCREENS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. 🚀 High Momentum Stocks
   • Up 20%+ in 3 months
   • RSI < 70
   • Volume > avg
   Results: 23 stocks

2. 💰 Value + Growth Combo
   • P/E < 20
   • Revenue growth > 15%
   • ROE > 15%
   Results: 18 stocks

3. 📈 Breakout Candidates
   • Near 52-week high
   • Volume surge
   • Strong fundamentals
   Results: 12 stocks

[Run Screen] [Save Screen] [Schedule Daily]
```

**Screen Results:**

```
🎯 SCREEN RESULTS: High Momentum Stocks
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Found 23 stocks matching criteria

TOP 10 RESULTS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. NVDA - NVIDIA Corp
   Price: $485.20 (+45% 3M)
   P/E: 68.5 | RSI: 65
   Score: 9.2/10 ⭐⭐⭐⭐⭐
   
2. META - Meta Platforms
   Price: $325.80 (+38% 3M)
   P/E: 24.2 | RSI: 62
   Score: 8.8/10 ⭐⭐⭐⭐

3. AVGO - Broadcom Inc
   Price: $892.50 (+35% 3M)
   P/E: 32.1 | RSI: 58
   Score: 8.5/10 ⭐⭐⭐⭐

[View All 23] [Add to Watchlist] [Get Signals]
[Export Results] [Save Screen]
```

---

### 5. Watchlist Intelligence

**Command:** `/watchlist`

```
📋 INTELLIGENT WATCHLIST
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔴 URGENT ATTENTION (2)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. TSLA - Tesla Inc
   ⚠️ Earnings tomorrow
   ⚠️ Analyst downgrade today
   📉 Down 3.2% today
   Action: Review position
   
2. AAPL - Apple Inc
   🎯 Near buy signal (87% confidence)
   📰 Positive news (AI partnership)
   📈 Breaking resistance at $190
   Action: Consider entry

🟡 MONITORING (5)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

3. MSFT - Microsoft Corp
   ➡️ Consolidating
   📅 Earnings in 5 days
   
4. GOOGL - Alphabet Inc
   ➡️ Range-bound
   📊 Neutral sentiment

5. NVDA - NVIDIA Corp
   ⬆️ Strong uptrend
   💰 High valuation

[View All 15] [Add Stock] [Remove Stock]
[Set Alerts] [Get Research]
```

**Proactive Watchlist Alerts:**

```
🔔 WATCHLIST ALERT - MSFT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Event: Analyst Upgrade
Time: 10 minutes ago

📊 DETAILS
• Goldman Sachs upgrades to Buy
• Price Target: $380 → $420
• Reason: Strong cloud growth

📈 MARKET REACTION
• Price: $385.50 (+2.1%)
• Volume: 2.5x average
• Sentiment: Very Positive

🎯 STOCKPILOT ANALYSIS
• Technical: Bullish breakout
• Fundamental: Strong
• Recommendation: Consider buying

[Research MSFT] [Get Signal] [Dismiss]
```

---

### 6. Sector & Industry Analysis

**Command:** `/sector <sector>` or `/industry <industry>`

```
🏭 SECTOR ANALYSIS - Technology
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 SECTOR OVERVIEW
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• Performance (YTD): +28.5%
• vs S&P 500: +18.2%
• Market Cap: $12.8T
• P/E Ratio: 32.5 (vs 22.1 market avg)
• Sentiment: Bullish

📈 TOP PERFORMERS (Last 30 Days)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. NVDA: +45.2%
2. META: +38.1%
3. AVGO: +35.8%
4. AMD: +32.5%
5. AAPL: +18.2%

📉 WORST PERFORMERS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. INTC: -12.5%
2. CSCO: -8.2%
3. IBM: -5.1%

🔥 TRENDING THEMES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• AI & Machine Learning 🔥🔥🔥
• Cloud Computing ⬆️
• Cybersecurity ⬆️
• Semiconductors 🔥🔥

📰 SECTOR NEWS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• AI spending to reach $200B in 2026
• Chip demand remains strong
• Cloud growth accelerating

🎯 INVESTMENT OUTLOOK
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Rating: Overweight ⭐⭐⭐⭐
Confidence: 82%

Reasoning:
• AI revolution driving growth
• Strong earnings momentum
• Valuation elevated but justified

[View All Tech Stocks] [Compare Sectors]
[Set Sector Alert]
```

---

### 7. Insider Trading Tracking

**Command:** `/insider <ticker>`

```
👔 INSIDER TRADING - AAPL
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 SUMMARY (Last 90 Days)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• Total Transactions: 15
• Insider Buys: 3 ($2.4M)
• Insider Sells: 12 ($45.2M)
• Net Activity: -$42.8M
• Sentiment: Slightly Bearish ⚠️

📈 RECENT TRANSACTIONS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. 🔴 SELL - June 15, 2026
   • Name: Luca Maestri (CFO)
   • Shares: 50,000
   • Value: $9.2M
   • Price: $184.50
   • Type: Scheduled sale
   
2. 🔴 SELL - June 10, 2026
   • Name: Kate Adams (General Counsel)
   • Shares: 25,000
   • Value: $4.6M
   • Price: $183.20
   • Type: Scheduled sale

3. 🟢 BUY - June 5, 2026
   • Name: Board Member
   • Shares: 10,000
   • Value: $1.8M
   • Price: $180.00
   • Type: Open market purchase

📊 ANALYSIS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• Most sales are scheduled (10b5-1 plans)
• Recent buy by board member is positive
• Selling volume is typical for this period
• No unusual patterns detected

Overall Signal: Neutral to Slightly Bearish

[View All Transactions] [Set Alert] [Compare to Peers]
```

---

### 8. Economic Calendar

**Command:** `/economic`

```
📅 ECONOMIC CALENDAR
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔴 THIS WEEK - HIGH IMPACT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 Wednesday, June 19
• FOMC Interest Rate Decision
  Time: 2:00 PM ET
  Expected: 5.25% (No change)
  Impact: Very High 🔥🔥🔥
  
• Fed Press Conference
  Time: 2:30 PM ET
  Watch for: Rate guidance, inflation outlook

📊 Thursday, June 20
• Initial Jobless Claims
  Time: 8:30 AM ET
  Expected: 225K
  Previous: 220K
  Impact: Medium

📊 Friday, June 21
• PMI Manufacturing
  Time: 9:45 AM ET
  Expected: 51.2
  Previous: 50.8
  Impact: Medium

🟡 NEXT WEEK
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• GDP Growth Rate (Q2)
• Consumer Confidence
• Durable Goods Orders

🎯 MARKET IMPACT ANALYSIS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• Fed decision is key event
• Expect volatility Wednesday afternoon
• Tech stocks sensitive to rate outlook
• Consider reducing positions before FOMC

[🔔 Set Reminders] [📊 View History]
```

---

### 9. Comparison Tool

**Command:** `/compare <ticker1> <ticker2> [ticker3]`

```
⚖️ STOCK COMPARISON
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Comparing: AAPL vs MSFT vs GOOGL

📊 VALUATION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                AAPL    MSFT    GOOGL
P/E Ratio       29.5    32.8    24.2
Forward P/E     26.8    28.5    22.1
PEG Ratio       2.1     2.4     1.8
Price/Sales     7.2     11.5    5.8
Price/Book      42.5    12.8    6.2

Winner: GOOGL (Best value) ⭐

💰 PROFITABILITY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                AAPL    MSFT    GOOGL
Net Margin      25.3%   36.7%   23.5%
ROE             147%    42%     28%
ROA             22.4%   18.2%   15.8%
Revenue Growth  2.1%    12.5%   8.2%

Winner: MSFT (Best margins) ⭐

📈 PERFORMANCE (YTD)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                AAPL    MSFT    GOOGL
Return          +18.2%  +22.5%  +15.8%
Volatility      22%     24%     28%
Sharpe Ratio    1.85    1.92    1.45

Winner: MSFT (Best risk-adjusted) ⭐

🎯 ANALYST RATINGS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                AAPL    MSFT    GOOGL
Avg Rating      Buy     Buy     Buy
Target Price    $205    $420    $155
Upside          +10.5%  +9.1%   +12.2%

Winner: GOOGL (Highest upside) ⭐

🏆 OVERALL WINNER
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. MSFT - 3 categories ⭐⭐⭐
2. GOOGL - 2 categories ⭐⭐
3. AAPL - 0 categories

Recommendation: MSFT offers best combination
of growth, profitability, and momentum.

[📊 Detailed Comparison] [Add to Watchlist]
```

---

### 10. Sentiment Analysis

**Command:** `/sentiment <ticker>`

```
😊 SENTIMENT ANALYSIS - AAPL
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 OVERALL SENTIMENT: Positive (0.68)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📰 NEWS SENTIMENT (Last 7 Days)
• Very Positive: 12 articles (0.8-1.0)
• Positive: 18 articles (0.5-0.8)
• Neutral: 8 articles (-0.5-0.5)
• Negative: 3 articles (-0.8--0.5)
• Very Negative: 0 articles (-1.0--0.8)

Average: 0.72 (Positive) ⬆️
Trend: Improving (+0.15 vs last week)

🐦 SOCIAL MEDIA SENTIMENT
• Twitter: 0.65 (Positive)
• Reddit: 0.58 (Positive)
• StockTwits: 0.71 (Positive)

Average: 0.65 (Positive) ⬆️
Volume: High (2.5x normal)

📊 ANALYST SENTIMENT
• Upgrades (30 days): 3
• Downgrades (30 days): 0
• Maintained: 5

Net Sentiment: Very Positive ⬆️⬆️

🎯 SENTIMENT SCORE: 8.2/10
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Interpretation:
• Strong positive sentiment across all sources
• Improving trend
• High social media buzz
• Analyst upgrades support bullish view

Trading Signal: Sentiment supports BUY ✅

[📈 View Trend] [🔔 Set Alert] [📰 Read News]
```

---

## 📁 New Files to Create

### Phase 3 File Structure

```
stockpilot/
├── src/
│   ├── research/
│   │   ├── __init__.py
│   │   ├── fundamental_analyzer.py     # P/E, revenue, margins, etc.
│   │   ├── company_researcher.py       # Comprehensive research reports
│   │   ├── earnings_tracker.py         # Earnings calendar & alerts
│   │   └── comparison_engine.py        # Compare multiple stocks
│   │
│   ├── news/
│   │   ├── __init__.py
│   │   ├── news_fetcher.py             # Fetch from multiple sources
│   │   ├── sentiment_analyzer.py       # Analyze news sentiment
│   │   ├── news_monitor.py             # Real-time monitoring
│   │   └── news_aggregator.py          # Aggregate and rank news
│   │
│   ├── screening/
│   │   ├── __init__.py
│   │   ├── stock_screener.py           # Screen stocks by criteria
│   │   ├── screen_builder.py           # Build custom screens
│   │   └── screen_templates.py         # Pre-built screen templates
│   │
│   ├── watchlist/
│   │   ├── __init__.py
│   │   ├── watchlist_monitor.py        # Monitor watchlist stocks
│   │   ├── alert_manager.py            # Manage alerts
│   │   └── watchlist_intelligence.py   # Proactive insights
│   │
│   ├── sector/
│   │   ├── __init__.py
│   │   ├── sector_analyzer.py          # Sector performance
│   │   ├── industry_analyzer.py        # Industry trends
│   │   └── correlation_analyzer.py     # Sector correlations
│   │
│   ├── insider/
│   │   ├── __init__.py
│   │   ├── insider_tracker.py          # Track insider trades
│   │   └── insider_analyzer.py         # Analyze patterns
│   │
│   └── economic/
│       ├── __init__.py
│       ├── economic_calendar.py        # Economic events
│       └── macro_analyzer.py           # Macro impact analysis
│
└── config/
    └── phase3_settings.yaml            # Phase 3 specific settings
```

---

## ⚙️ Configuration

### config/settings.yaml (Phase 3 additions)

```yaml
# Phase 3 - Research & Analysis

# Fundamental Analysis
fundamental:
  enabled: true
  data_sources:
    - yfinance
    - alpha_vantage
    - financial_modeling_prep
  metrics:
    - pe_ratio
    - forward_pe
    - peg_ratio
    - price_to_sales
    - price_to_book
    - debt_to_equity
    - current_ratio
    - roe
    - roa
    - profit_margin
    - revenue_growth

# News & Sentiment
news:
  enabled: true
  sources:
    - newsapi
    - alpha_vantage_news
    - yahoo_finance
    - benzinga
  sentiment_analysis: true
  real_time_monitoring: true
  alert_on_breaking_news: true
  min_sentiment_threshold: 0.5
  update_interval_minutes: 15

# Earnings Tracking
earnings:
  enabled: true
  track_upcoming: true
  alert_days_before: [7, 3, 1]
  alert_after_release: true
  track_estimates: true
  track_surprises: true

# Stock Screening
screening:
  enabled: true
  pre_built_screens:
    - value_stocks
    - growth_stocks
    - dividend_stocks
    - momentum_plays
    - breakout_candidates
  custom_screens: true
  scheduled_screens: true
  screen_interval: daily

# Watchlist Intelligence
watchlist:
  enabled: true
  proactive_monitoring: true
  alert_on_news: true
  alert_on_price_moves: true
  alert_on_analyst_changes: true
  alert_on_earnings: true
  alert_on_insider_trading: true

# Sector Analysis
sector:
  enabled: true
  track_performance: true
  track_trends: true
  compare_sectors