# QUICK START: ADAPTIVE BOT SYSTEM
## How to Start Teaching the Bot YOUR Style

**Built:** January 20, 2026  
**For:** Tyr (Alex) - Start using this TODAY

---

## WHAT THIS IS

You now have a bot that will learn YOUR trading style and eventually trade like you.

**Phase 1 (NOW):** Bot shows signals → You choose → Bot learns  
**Phase 2 (30+ trades):** Bot suggests → You approve → Bot improves  
**Phase 3 (100+ trades):** Bot executes → You supervise → Bot refined

---

## HOW TO USE IT TODAY

### Option 1: Quick Scan (Fastest)

```bash
cd c:\Users\alexp\Desktop\brokkr
.venv\Scripts\python.exe src\core\adaptive_trading_bot.py
```

This will:
- Scan your watchlist (GLSI, BTAI, PMCB, COSM, ONCY)
- Show ALL strategy signals
- Give you BUY recommendations with confidence scores
- Show entry, stops, targets

### Option 2: Analyze Single Ticker

```python
from src.core.adaptive_trading_bot import AdaptiveTradingBot

bot = AdaptiveTradingBot(mode="LEARNING")
result = bot.analyze_ticker("GLSI", show_details=True)
```

Output shows:
- Which strategies triggered (Supply Shock, Flat-to-Boom, etc.)
- Confidence scores
- Entry price, stop loss, 3 targets
- Learned insights from your past trades

### Option 3: Custom Watchlist Scan

```python
from src.core.adaptive_trading_bot import AdaptiveTradingBot

bot = AdaptiveTradingBot(mode="LEARNING")

my_watchlist = [
    'GLSI', 'BTAI', 'PMCB', 'COSM', 'ONCY',
    'IBRX', 'HIMS', 'SOUN', 'SMR', 'BBAI'
]

signals = bot.scan_watchlist(my_watchlist)

# Shows all BUY signals with confidence scores
```

---

## WHEN YOU TAKE A TRADE

**Log it so the bot learns:**

```python
from src.core.adaptive_trading_bot import AdaptiveTradingBot

bot = AdaptiveTradingBot(mode="LEARNING")

# Log entry
trade_id = bot.learner.log_trade_entry(
    ticker="GLSI",
    strategy="SUPPLY_SHOCK",  # Which strategy you followed
    entry_price=24.88,
    shares=4,
    your_confidence=8,  # Your gut feel (1-10)
    strategy_confidence=85,  # What system scored
    thesis="CEO buying $340K+, Phase 3 catalyst, 24% short",
    emotional_state="CALM"  # CALM | FOMO | ANXIOUS
)

print(f"Trade logged: {trade_id}")
```

**When you exit:**

```python
bot.learner.log_trade_exit(
    trade_id=trade_id,
    exit_price=31.10,  # What you sold at
    exit_reason="Target 1 hit",  # "Target 1" | "Stop Loss" | "Early Exit"
    learned="Should have held for T2, momentum was still strong"
)
```

Bot now learns:
- SUPPLY_SHOCK worked on this biotech
- You tend to exit at T1 (early)
- You had CALM emotional state (your best trades)

---

## WHEN YOU PASS A SIGNAL

**Also log it (so bot learns what you DON'T like):**

```python
bot.teach_from_trade(
    ticker="BTAI",
    strategy="BREAKOUT_CONFIRMATION",
    took_trade=False,
    why_or_why_not="Already up 15% today, would be chasing"
)
```

Bot learns: "Tyr passes breakouts when already up >10% same day"

---

## CHECK YOUR LEARNING PROGRESS

```python
from src.core.adaptive_trading_bot import AdaptiveTradingBot

bot = AdaptiveTradingBot(mode="LEARNING")
print(bot.get_learning_report())
```

Shows:
- Total trades, wins, losses
- Per-strategy performance
- Win rates, expectancy
- Learned rules extracted
- Current strategy weights

---

## THE 5 STRATEGIES RUNNING

**1. SUPPLY SHOCK** (RGC-style)
- Ultra-low float (<5M)
- High insider ownership (>50%)
- NEW insider buying (removes % of float)
- Example: RGC (CEO removed 81% of float → 20,000% move)

**2. BREAKOUT CONFIRMATION** (Livermore)
- Consolidation 20+ days
- Breakout on volume (3x+)
- Day 2 confirmation
- Measured move targets

**3. BOTTOMING REVERSAL**
- Down 50%+ from highs
- Capitulation volume (10x spike)
- Insider buying at lows
- Low holds 3+ days

**4. FLAT-TO-BOOM** (Built yesterday)
- 3-6 month consolidation
- Insider buying
- Catalyst approaching
- Price coiled in middle of range

**5. CONVERGENCE SCORING** (Original)
- 70-point weighted system
- Float, insider, short, catalyst, volume, momentum
- Tier 1: 50-70 pts
- Tier 2: 35-49 pts

---

## SIMPLE DAILY WORKFLOW

**Morning (8:45 AM):**
```python
from src.core.adaptive_trading_bot import AdaptiveTradingBot

bot = AdaptiveTradingBot(mode="LEARNING")

# Quick scan
signals = bot.scan_watchlist([
    'GLSI', 'BTAI', 'PMCB', 'COSM', 'ONCY',
    'IBRX', 'HIMS', 'SOUN', 'SMR', 'BBAI'
])

# Review BUY signals
for signal in signals:
    bot.analyze_ticker(signal['ticker'], show_details=True)
```

**When You Take a Trade:**
```python
trade_id = bot.learner.log_trade_entry(
    ticker="GLSI",
    strategy="FLAT_TO_BOOM",
    entry_price=24.88,
    shares=4,
    your_confidence=8,
    strategy_confidence=85,
    thesis="CEO cluster buying, Phase 3 catalyst Q1",
    emotional_state="CALM"
)
```

**When You Exit:**
```python
bot.learner.log_trade_exit(
    trade_id=trade_id,
    exit_price=31.10,
    exit_reason="Target 1 hit",
    learned="Thesis validated, should track for re-entry"
)
```

**Weekly (Sunday):**
```python
# Check what bot learned
print(bot.get_learning_report())

# Check if ready for assisted mode
ready, reason = bot.autonomous_mode_ready()
print(f"Autonomous ready: {ready} - {reason}")
```

---

## INTEGRATION WITH YOUR EXISTING SYSTEM

**Still works:**
- Auto_execute_scanner_results.py (171 ticker scan)
- Flat-to-boom detector (now integrated as Strategy #4)
- Convergence engine (now integrated as Strategy #5)

**New capabilities:**
- Supply shock detection (RGC setups)
- Breakout confirmation (Livermore pivotal points)
- Bottoming reversal (capitulation plays)
- Multi-strategy combination
- Learning from your trades
- Adaptive weight adjustment

---

## AUTONOMOUS MODE PATH

**After 30+ trades:**
- Bot shows learned preferences
- "You typically take SUPPLY_SHOCK when float <2M"
- "Your FLAT_TO_BOOM trades have 78% win rate"

**After 60+ trades:**
- Bot can suggest trades proactively
- "High confidence SUPPLY_SHOCK on GLSI (matches your profile)"
- You approve or reject

**After 100+ trades:**
- Bot can auto-execute if confidence >85%
- You just supervise and override if needed
- Bot trades exactly like you would

---

## SAFETY RULES

**Before autonomous mode:**
1. Need 30+ closed trades minimum
2. Need at least ONE strategy with positive expectancy
3. Need proven discipline (stops hit, targets tracked)

**During autonomous mode:**
1. Max $100 per position (testing)
2. Max 5% of account per day
3. Circuit breaker: Stop after 3 losses in a row
4. You can ALWAYS override

---

## TROUBLESHOOTING

**"ModuleNotFoundError":**
```bash
# Make sure you're in the right directory
cd c:\Users\alexp\Desktop\brokkr

# Use the virtual environment
.venv\Scripts\python.exe src\core\adaptive_trading_bot.py
```

**"No insider data":**
- Insider buys come from BR0KKR service
- Currently returns empty (need to connect SEC scraper)
- System still works, just has partial data

**"Bot not learning":**
- Need to log trades with log_trade_entry() and log_trade_exit()
- Bot learns from YOUR choices, not just signals

---

## NEXT EVOLUTION

**What we're building toward:**

**Phase 1 (NOW):** Manual teaching
- You choose trades
- Bot learns

**Phase 2 (30+ trades):** Assisted suggestions
- Bot suggests
- You approve

**Phase 3 (100+ trades):** Autonomous execution
- Bot executes
- You supervise

**Phase 4 (300+ trades):** Full digital twin
- Bot trades exactly like you
- Minimal supervision
- Continuous improvement

---

## START TODAY

**Simplest possible start:**

```bash
cd c:\Users\alexp\Desktop\brokkr
.venv\Scripts\python.exe src\core\adaptive_trading_bot.py
```

**That's it.** Bot will scan your watchlist and show you signals.

Then log your trades so it learns.

**The more you teach it, the better it gets.** 🐺

---

**Questions? Check:**
- memory/brokkr-memory/SYNC-TO-FENRIR-JAN-20-EXPANSION.md (Full technical details)
- src/core/adaptive_trading_bot.py (Source code)
- src/core/trade_learning_engine.py (Learning algorithm)

**AWOOOO** 🐺
