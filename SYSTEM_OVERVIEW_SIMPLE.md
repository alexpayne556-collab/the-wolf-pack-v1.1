# 🐺 WOLF PACK SYSTEM - SIMPLE OVERVIEW

**What it is:** A trading intelligence system that hunts "wounded prey" stocks (beaten down stocks ready to bounce).

---

## 🎯 THE CORE CONCEPT

**"Wounded Prey Pattern"** = Stocks that got hammered but might bounce back

**Example (IBRX):**
- Stock at $10 → crash to $3.80 (bad news)
- Wolf Pack spots: unusual volume, positive divergence, oversold
- You buy at $3.80
- Stock recovers to $5.90+ (55% gain in 2 weeks)

---

## 🧠 HOW IT WORKS (7 SIGNALS)

The system looks for 7 things at once:

1. **Volume Spike** - More people buying/selling than usual
2. **Price Pattern** - Reversal candlestick patterns
3. **RSI Divergence** - Price goes down but momentum goes up (hidden strength)
4. **Options Activity** - Big bets being placed
5. **News Sentiment** - Are people talking about it?
6. **Earnings Surprise** - Did they beat expectations?
7. **Pivotal Points** - Livermore's key price levels

When 5+ signals align = **CONVERGENCE** = High probability setup

---

## 📁 KEY FILES (What Does What)

### **SCANNERS** (Find Opportunities)
- `autonomous_brain.py` - Main scanner (runs at 4 AM, finds wounded prey)
- `overnight_scan.py` - Checks for setups overnight
- `build_real_portfolio.py` - Research tool for universe building

### **TRADING** (Execute Trades)
- `terminal_brain.py` - Your main interface (paper trading)
- `execute_with_stops.py` - Places orders with stop losses
- `wolf_pack_trader.py` - Automated trader (when enabled)

### **ANALYSIS** (Learn & Adapt)
- `truth_check.py` - Reviews past trades (what worked? what didn't?)
- `test_paper_trades.py` - Tests trading logic without real money

### **DATA STORAGE**
- `data/wounded_prey_universe.json` - List of potential stocks
- `data/morning_opportunities.json` - Today's top picks
- `data/biotech_moonshots.json` - High-risk biotech plays
- `memory/` - Trade history, learnings, patterns

---

## 🔄 DAILY WORKFLOW

**4:00 AM** - System scans premarket for wounded prey  
**7:00 AM** - You review intel report  
**9:30 AM** - Market opens, you decide which setups to trade  
**4:00 PM** - Market closes, system logs results  
**Evening** - System learns from today's trades

---

## 🛠️ TECH STACK

| Component | Purpose | Status |
|-----------|---------|--------|
| Python | Core language | ✅ Working |
| yfinance | Stock data (free) | ✅ Working |
| Alpaca API | Paper trading | ✅ Ready (needs key refresh) |
| Finnhub | Earnings, fundamentals | ✅ Working |
| NewsAPI | Sentiment analysis | ✅ Working |
| Ollama (optional) | Local AI brain | ⚠️ RAM-intensive (disabled) |

---

## 💾 SYSTEM REQUIREMENTS

### **Current Full System:**
- Python 3.10+
- 8-16GB RAM (with Ollama: 32GB+)
- Windows/Linux/Mac
- Internet connection

### **Lightweight Research System (What We're Building):**
- Python 3.10+
- 4-8GB RAM (no Ollama)
- Just scanners + analysis
- Cloud-ready

---

## 🎓 THE PHILOSOPHY (Market Wizards' Wisdom)

Built on **10 Commandments** from legendary traders:

1. **Cut losses quickly** (Paul Tudor Jones)
2. **Let winners run** (Jesse Livermore)
3. **Trade with the trend** (never fight the market)
4. **Position size with Kelly Criterion** (Ed Thorp)
5. **Wait for high-conviction setups** (quality over quantity)
6. **Manage risk first, profit second** (2% max risk per trade)
7. **Keep detailed records** (learn from every trade)
8. **Respect pivotal points** (Livermore's key levels)
9. **Never trade on hope** (trade the plan, not emotions)
10. **Adapt or die** (markets change, system must evolve)

---

## 📊 PROVEN RESULTS (So Far)

**Trade 1: IBRX**
- Identified: January 9, 2026
- Entry: $3.80
- Peak: $5.90+ (55%+ gain)
- Convergence Score: 93/100 (6/7 signals aligned)
- **Status:** Validated the wounded prey pattern works

**What We Need:** 50+ more trades for statistical significance

---

## 🚀 WHAT'S NEXT (YOUR REQUEST)

You want a **lightweight research-only system** because:
- Current system uses too much RAM (Ollama)
- You can't run it locally on your computer
- You just want the **best research tools**

**Solution:** Strip out trading, keep only:
- ✅ Scanner (finds opportunities)
- ✅ Analysis tools (grades setups)
- ✅ Data export (CSV/JSON for review)
- ✅ No trading execution
- ✅ No memory-heavy AI
- ✅ Can run on low-RAM machine or cloud

---

## 📚 KEY DOCUMENTS (Read These)

1. **QUICK_START.md** - How to run the system
2. **REALISTIC_PITCH.md** - What this system really is (honest assessment)
3. **BRUTAL_TRUTH.md** - Current limitations & challenges
4. **CONSOLIDATION_COMPLETE.md** - Recent cleanup work
5. **ALPACA_SYNC_GUIDE.md** - Paper trading setup

---

## 🆘 SUPPORT

- GitHub Discussions: (planned)
- Read: `HOW_TO_ASK_FOR_HELP_GITHUB.md`
- Discord: (planned)

---

## ⚖️ LICENSE

MIT License - Use freely, modify as needed, share learnings back if possible.

---

**Last Updated:** January 27, 2026  
**System Version:** v5.6
