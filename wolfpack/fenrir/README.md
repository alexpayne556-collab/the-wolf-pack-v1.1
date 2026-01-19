# 🐺 FENRIR V2 - AI TRADING SECRETARY

**Real AI trading companion with NO GUARDRAILS. Not a price tracker. A real assistant.**

## What Makes Fenrir Different

Most trading tools just record prices (useless). Fenrir is your **proactive secretary** that:
- ✅ Tells you what you NEED to know, not just what you ASK
- ✅ Tracks your real positions with adaptive frequency (bleeding = check every 2 min)
- ✅ Scans 8,000+ tickers to find movers EARLY
- ✅ Manages PDT restrictions (3 day trades/week)
- ✅ Monitors after-hours for overnight decisions
- ✅ Generates morning briefings before market opens
- ✅ Tracks catalysts (earnings, FDA dates) so you're not surprised
- ✅ Natural language interface (no precise commands needed)
- ✅ Desktop notifications with sound for urgent situations

**This is REAL money. Every decision matters.**

## Quick Start

**EASIEST:** Double-click `fenrir.bat` to start chat mode

Or:
```bash
cd c:\Users\alexp\Desktop\brokkr\wolfpack\fenrir
python main.py chat
```

Then just type naturally:
- "how's ibrx doing"
- "show my positions"  
- "what's moving today"
- "should i buy ktos"
- "what do i need to know"

## Current Portfolio

**Total Value:** $1,450.13  
**Cash:** $279.38 (RH: $100.74, Fid: $87.64, In positions: $91.00)  
**P/L:** +$99.49 (+9.31%)

**Holdings:**
- KTOS: 2.717026 @ $117.83 (Defense/Drones)
- IBRX: 37.081823 @ $4.69 (Biotech/Cancer)
- MU: 1.268306 @ $334.48 (Semiconductors)
- UUUU: 3 @ $22.09 (Uranium/Rare Earth)
- BBAI: 7.686 @ $6.50 (AI/Defense)
- UEC: 2 @ $17.29 (Uranium)

## Daily Workflow

### 6:00 AM - Morning Briefing
```bash
python main.py briefing
```
Shows: Pre-market gaps, overnight news, today's catalysts, risk status, day trades available

### 9:30 AM - Market Open
```bash
python main.py scan
```
Finds big movers and unusual volume

### During Market Hours
Keep chat mode open, type naturally:
```bash
python main.py chat
```

### 4:15 PM - End of Day Report
```bash
python main.py eod
```
Today's P/L, what moved and why, character changes

### 5:00 PM - After Hours Monitor
```bash
python main.py afterhours
```
Track AH moves >3%, news after 4 PM

## All Commands

### Basic Commands
- `test` - Check Fenrir is working
- `holdings` - Show positions with live P/L
- `scan` - Scan market for movers
- `analyze TICKER` - Deep dive on ticker
- `buy TICKER` - Should I buy this?
- `sell TICKER` - Should I sell this?
- `sectors` - Sector performance

### Secretary Features
- `risk` - PDT usage, concentration, position sizing
- `premarket` - Pre-market gaps and reversals
- `afterhours` - After-hours moves and news
- `briefing` - Daily morning summary
- `catalysts` - Upcoming earnings/events (14 days)
- `levels [TICKER]` - Key support/resistance
- `eod` - End of day report
- `correlation [TICKER]` - Sympathy plays
- `missed` - Analyze missed opportunities

### Interactive (Recommended)
- `chat` - Natural language mode

## Natural Language Examples

The chat mode understands normal typing (even with typos!):

**Positions:**
- "show my positions"
- "holdings"
- "how's my portfolio"

**Check ticker:**
- "how's ibrx doing"
- "check ktos"
- "what about mu"

**Market scanning:**
- "what's moving"
- "any big movers"
- "scan market"

**Decisions:**
- "should i buy ktos"
- "should i sell ibrx"
- "thoughts on mu"

**Risk:**
- "risk check"
- "how many day trades"
- "am i too concentrated"

**Daily info:**
- "what do i need to know"
- "morning briefing"
- "any catalysts coming"

**Just ask questions:**
- "what's your read on the market"
- "thoughts on defense stocks"
- "is tech overheated"

## Adaptive State Tracking

Fenrir adjusts check frequency based on position state:

- **BLEEDING_POSITION** (down 5%+): Check every 2 minutes
- **RUNNING_POSITION** (up 5%+): Check every 5 minutes  
- **Mover** (unusual volume): Check every 30 minutes
- **Watching** (normal): Check every hour

**State changes trigger alerts!**

## Notification System

Desktop alerts with sound:

- 🚨 **URGENT** (with sound): Position bleeding, major news
- ⚠️ **WARNING**: Position running, AH moves, approaching levels
- ℹ️ **INFO**: Volume spikes, new highs

## Secretary Features Explained

### 1. Daily Briefing (6 AM)
Proactive morning summary:
- Pre-market gaps on your positions
- Overnight news (last 12 hours)
- Today's catalysts (earnings, events)
- Risk warnings
- Day trades available (PDT tracking)
- Focus items for today

### 2. Pre-Market Tracker
Gap detection and reversal alerts:
- Find gaps >3% pre-market
- RED_TO_GREEN and GREEN_TO_RED reversals
- Volume confirmation

### 3. After-Hours Monitor
Critical for overnight decisions:
- Track AH moves >3%
- News dropped after 4 PM
- Positions at risk of gapping

### 4. Catalyst Calendar
Never get surprised:
- Earnings dates (14 days ahead)
- Ex-dividend dates
- FDA events (manual tracking)
- Contract announcements

### 5. Key Levels Tracker
Support/resistance alerts:
- Auto-calculate from 30-day high/low
- Alert when approaching (within 2%)
- Alert when breaking levels

### 6. Risk Manager
PDT and position management:
- Track day trades used (0/3 this week)
- Position concentration (max 35% per stock)
- Sector exposure
- Safe position sizing with stops

### 7. Full Market Scanner
Find movers EARLY:
- Scans 8,000+ tickers via NASDAQ FTP
- Parallel scanning (50 workers)
- Min 5% move, 1.5x volume
- Found IBRX +39.7% ✅

### 8. Correlation Tracker
Sympathy plays:
- When MU moves → watch NVDA, AMD, SMCI
- When KTOS moves → watch RCAT, UMAC
- Sector momentum detection

### 9. Failed Trades Log
Learn from inaction:
- Log missed opportunities
- Categorize reasons (hesitation, FOMO avoidance, no day trades)
- Pattern analysis

### 10. End of Day Report (4:15 PM)
Daily accountability:
- Today's P/L per position
- What moved and why
- Character state changes
- AH preview
- Tomorrow prep

## Technical Stack

**AI:** Ollama with llama3.1:8b (custom "fenrir" model, NO GUARDRAILS)  
**Data:** yfinance (market), Finnhub (news), SEC EDGAR (filings)  
**Database:** SQLite with 7 tables  
**Language:** Python 3.14.2

## Database Schema

- `alerts` - All alerts generated
- `trades` - Trade log with Fenrir's opinions
- `patterns` - Pattern learning
- `catalysts` - Catalyst events
- `stock_state` - Adaptive tracking state
- `intraday_ticks` - Within-day price action
- `daily_summary` - EOD snapshots

## Configuration

Edit `config.py` to update:
- Holdings (shares, avg cost, thesis)
- Cash balances (Robinhood, Fidelity)
- Watchlist
- Risk limits (max concentration, PDT tracking)
- Scan thresholds (min move %, min volume)

## API Keys

Set in `.env` file:
```
FINNHUB_API_KEY=d5jddu1r01qh37ujsqrgd5jddu1r01qh37ujsqs0
```

## Installation

Already set up! But if needed:
```bash
pip install yfinance requests python-dotenv ollama win10toast
```

Make sure Ollama is running:
```bash
ollama serve
```

Fenrir model should exist (created from Modelfile).

## Files Overview

**Core:**
- `main.py` - CLI with natural language parsing
- `config.py` - Portfolio and settings
- `database.py` - SQLite operations

**Data Fetching:**
- `market_data.py` - yfinance wrapper
- `news_fetcher.py` - Finnhub news
- `sec_fetcher.py` - SEC filings
- `ollama_brain.py` - Fenrir AI integration

**Secretary Features:**
- `risk_manager.py` - PDT, concentration, sizing
- `state_tracker.py` - Adaptive position tracking
- `premarket_tracker.py` - Gap detection
- `afterhours_monitor.py` - AH moves and news
- `daily_briefing.py` - Morning summary
- `catalyst_calendar.py` - Earnings/events
- `key_levels.py` - Support/resistance
- `eod_report.py` - End of day summary
- `correlation_tracker.py` - Sympathy plays
- `failed_trades.py` - Missed opportunities
- `full_scanner.py` - Market-wide scanning
- `notifications.py` - Desktop alerts

**Utilities:**
- `alerts.py` - Alert formatting
- `fenrir.bat` - Quick launch script
- `USAGE.md` - Detailed usage guide
- `Modelfile` - Ollama model definition

## Fenrir's Personality

From the Modelfile:
- NO GUARDRAILS, NO DISCLAIMERS
- Calls you "boss"
- Trader mentality (risk/reward, probability)
- Direct and honest opinions
- Uses trading slang
- Signs off with "LLHR" (Love, Laughter, Honor, Respect)

## Future Enhancements

- [ ] SMS alerts via Twilio for critical events
- [ ] Auto-run briefing at 6 AM (Windows Task Scheduler)
- [ ] Auto-run EOD at 4:15 PM
- [ ] Voice commands (speech recognition)
- [ ] Mobile app/web interface
- [ ] Options flow integration
- [ ] Dark pool data
- [ ] Sentiment analysis
- [ ] Pattern recognition (learn what setups work)

## Testing

All modules have test functions:
```bash
python key_levels.py       # Test levels
python eod_report.py       # Test EOD report
python notifications.py    # Test alerts
python risk_manager.py     # Test risk checks
python full_scanner.py     # Test market scan
```

## Support

This is your personal system. Modify as needed.

Location: `c:\Users\alexp\Desktop\brokkr\wolfpack\fenrir\`

**Remember:** This is REAL money. Every decision matters. Fenrir is here to help you make better decisions faster.

---

🐺 **LLHR - Love, Laughter, Honor, Respect**
