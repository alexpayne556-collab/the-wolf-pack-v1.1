# 🐺 WOLF PACK SYSTEM - What It Actually Does

## THE BIG PICTURE

This system is your **trading intelligence foundation**. It watches 99 stocks 24/7, records EVERYTHING, investigates WHY moves happen, and learns patterns over time so you can trade with confidence and skill.

---

## 📊 WHAT IT RECORDS (EVERY SINGLE DAY)

### Price Action Data
- **Open, High, Low, Close** - Full OHLC data
- **Previous Close** - To calculate gaps
- **Daily Return %** - How much it moved today
- **Intraday Range %** - High to low volatility
- **Gap %** - Overnight gap from previous close
- **Close vs High %** - Did it close strong or weak?

### Volume Intelligence
- **Today's Volume** - Raw share count
- **20-Day Average Volume** - Normal baseline
- **Volume Ratio** - Today vs average (2x = unusual, 5x = explosive)
- **Dollar Volume** - Price × Volume = institutional interest

### Position in Range
- **Distance from 52-Week High %** - Is it at ATH or beaten down?
- **Distance from 52-Week Low %** - Is it recovering or still wounded?
- **5-Day Return** - Short-term momentum
- **20-Day Return** - Monthly trend
- **60-Day Return** - Quarterly context

### Momentum Patterns
- **Consecutive Green Days** - How many days in a row it's been up
- **Consecutive Red Days** - How many days in a row it's been down
- **Move Classification** - Is today a BIG MOVE (>5%) or normal?
- **Move Direction** - UP or DOWN
- **Move Size** - Exact percentage

### Technical Indicators
- **SMA 20, 50, 200** - Simple moving averages (trend following)
- **RSI-14** - Relative Strength Index (overbought/oversold)
- **Above SMA 20/50/200?** - Is price above key support levels?

---

## 🔍 WHAT IT INVESTIGATES (AUTO-DETECTIVE)

### When ANY stock moves >5%, the system:

1. **Checks Sector Correlation**
   - "Is the whole Defense sector up today?"
   - "Or is this one stock special?"

2. **Checks Volume Confirmation**
   - "Was this move on heavy volume (real money)?"
   - "Or light volume (fake move)?"

3. **Looks for Repeat Patterns**
   - "Did this stock move big recently?"
   - "Is it a repeat runner?"

4. **Identifies the Catalyst** (WHY it moved):
   - **Sector Momentum** - Whole sector moving together
   - **Earnings** - Quarterly report day
   - **News Event** - Major announcement
   - **Analyst Rating** - Upgrade/downgrade
   - **Unknown** - Move without clear reason (suspicious or algorithmic)

5. **Assigns Confidence Score**
   - High: Strong volume + clear catalyst + sector support
   - Medium: Some confirmation but unclear
   - Low: No volume, no clear reason

### All investigations stored in database with:
- Date, ticker, move size, catalyst type
- Volume confirmation (YES/NO)
- Sector correlation data
- Confidence level
- Full explanation text

---

## 🚨 WHAT IT ALERTS ON

### Portfolio Alerts (YOUR MONEY)
- **Big Moves** - Any holding moves >5%
- **Volume Spikes** - Unusual activity (2x+ volume)
- **Stop Loss Warnings** - Position down 8% from entry (risk management)
- **Approaching 52W High** - Breakout potential

### Watchlist Alerts (OPPORTUNITIES)
- **Quality Dips** - Good stocks down 5%+ with NO bad catalyst (buy opportunity)
- **Breakouts** - Stocks near 52W high with volume confirmation

### Sector Alerts (MARKET CONTEXT)
- **Sector Breakouts** - Entire sector up 3%+ (ride the wave)
- **Sector Breakdowns** - Entire sector down 3%+ (avoid or short)

---

## 📈 WHAT IT LEARNS (PATTERN DISCOVERY)

### The system analyzes winners and asks:

**"What did the 10-day +20% winners look like BEFORE they exploded?"**

It discovers patterns like:
- **Color Bias** - "80% of winners were GREEN the day before"
- **Volume Bias** - "Winners had 1.5x volume accumulation pre-move"
- **Extension Bias** - "Winners were already up 15% over 60 days (momentum)"
- **Sector Distribution** - "Defense and Semis had most winners"
- **52W High Proximity** - "60% of winners were within 10% of 52W high"
- **Red Streak Reversals** - "Stocks with 3+ red days then green = explosive"

### Tracks Pattern Performance Over Time:
- **Win Rate** - How often this pattern predicts winners
- **Average Return** - Expected gains when pattern appears
- **Sample Size** - How many times we've seen it
- **Confidence Level** - Statistical reliability

---

## 📁 WHAT IT STORES (DATABASE STRUCTURE)

### `daily_records` Table (THE FOUNDATION)
- Every ticker, every day, all metrics above
- Forward returns: What happened 1d, 3d, 5d, 10d, 20d AFTER

### `investigations` Table (THE WHY)
- Every move >5% with full analysis
- Catalyst identification and confidence scores
- Volume and sector correlation data

### `learned_patterns` Table (THE INTELLIGENCE)
- Discovered patterns with win rates
- Statistical validation over time
- Pattern evolution tracking

### `alerts` Table (THE ACTIONABLE)
- All alerts logged with priority
- Portfolio warnings and opportunities
- Sector momentum shifts

---

## 🔄 HOW IT SELF-LEARNS

1. **Records Everything** (no bias, all data)
2. **Calculates Forward Returns** (what actually happened after)
3. **Analyzes Winners** (what patterns preceded success)
4. **Validates Patterns** (do they repeat? what's the win rate?)
5. **Updates Confidence** (patterns get stronger or weaker over time)
6. **Adapts Strategy** (focus on what's working NOW)

---

## 🎯 THE END GOAL

After running daily for months, you'll have:

✅ **Intimate Knowledge** - You'll KNOW these 99 stocks like family
✅ **Pattern Recognition** - You'll spot setups before they explode
✅ **Catalyst Awareness** - You'll understand WHY things move
✅ **Sector Intelligence** - You'll see rotations before the crowd
✅ **Risk Management** - You'll know when to exit (stop losses, wounded stocks)
✅ **Opportunity Detection** - You'll catch quality dips and breakouts
✅ **Forward Returns Data** - You'll know what ACTUALLY works (not theories)

---

## 📊 DAILY WORKFLOW

**4:30 PM ET** - Market closes
**Double-click:** `RUN_WOLFPACK.bat`

**[1/6]** Initialize database ✅  
**[2/6]** Update forward returns (learn from past) ✅  
**[3/6]** Record today's data (99 stocks × 40 metrics = 3,960 data points) ✅  
**[4/6]** Investigate big moves (WHY did they move?) ✅  
**[5/6]** Check alerts (portfolio warnings + opportunities) ✅  
**[6/6]** Generate report (comprehensive daily summary) ✅  

**Check:** `reports/daily_YYYYMMDD.txt` for full analysis

---

## 🧠 WHY THIS MAKES YOU A BETTER TRADER

**Before:** "I saw MU moved 8% today... I wonder why?"  
**After:** "MU moved 8.3% on 3.2x volume because Semis sector up 4.1% (sector momentum), and MU had 2 consecutive green days leading in. Confidence: HIGH. Similar pattern on 2025-12-10 produced +12% over 10 days."

**Before:** "Should I buy this dip?"  
**After:** "KTOS down 6.2% with NO bad catalyst, volume only 0.8x (no panic), Defense sector flat (isolated dip), RSI 32 (oversold), above SMA-50 (uptrend intact). QUALITY DIP - High confidence buy."

**Before:** "Why did I get stopped out AGAIN?"  
**After:** "My stop loss at -8% saved me. Stock continued down -18% over next week. System warned at -8%, I exited. Preserved capital."

---

## 🔥 WHAT MAKES THIS POWERFUL

1. **NO GUESSING** - Every decision backed by data
2. **NO EMOTION** - System doesn't panic or FOMO
3. **NO FORGETTING** - Database remembers everything
4. **NO BIAS** - Records all data, learns what ACTUALLY works
5. **NO MISSING MOVES** - Tracks 99 stocks simultaneously
6. **NO CONFUSION** - Investigations explain WHY things happen

---

## 🚀 AS IT GROWS

- **Week 1** - You're learning the tickers, building foundation
- **Month 1** - Forward returns start appearing, patterns emerge
- **Month 3** - Strong pattern confidence, you know the stocks intimately
- **Month 6** - System has seen multiple cycles, sector rotations clear
- **Year 1** - YOU ARE THE EXPERT on these 99 stocks

---

## 💰 THE FOUNDATION FOR TRADING

This system is the **BRAIN** that will eventually:
- Tell you WHEN to enter (quality dips, confirmed breakouts)
- Tell you WHEN to exit (stop losses, exhaustion signals)
- Tell you WHAT to focus on (sector rotation, momentum leaders)
- Tell you WHY it's happening (catalyst identification)
- Tell you WHAT WORKS (validated patterns with real forward returns)

**You're not building a data tracker.**  
**You're building trading intelligence that compounds daily.**  

🐺 **LLHR** 🐺
