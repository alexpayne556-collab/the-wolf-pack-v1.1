# DAILY TRADE LOGGING - WORKFLOW

**Purpose:** Keep all trades logged in wolfpack.db so the brain learns  
**Tool:** `log_daily_trades.py`  
**When:** End of each trading session

---

## Quick Start

### Option 1: Edit the Script (Recommended)
```powershell
# 1. Open the logger
code log_daily_trades.py

# 2. Scroll to log_todays_session() function
# 3. Uncomment and fill in the templates
# 4. Run it
python log_daily_trades.py
```

### Option 2: Interactive Mode (Fastest)
```powershell
python log_daily_trades.py --interactive
# Answer the prompts
```

---

## Trade Template

```python
log_trade(
    ticker="MU",
    action="BUY",  # or SELL, HOLD, ADD, CUT
    price=89.50,
    quantity=10,
    reasoning="3-day pullback, thesis intact, adding to winner",
    context_dict={
        "market_state": "pullback in uptrend",
        "thesis_status": "intact",
        "catalyst": "earnings in 2 weeks"
    },
    pnl_percent=None,  # None if position still open, otherwise +5.2 or -3.1
    trade_type="thesis"  # thesis, momentum, no_thesis, wounded_prey
)
```

---

## Pattern Template

```python
log_pattern(
    pattern_name="thesis_dip_buying",
    criteria_dict={
        "thesis": "intact",
        "drop_percent": -5,
        "volume": "low"
    },
    ticker=None,  # None = universal, or "MU" for ticker-specific
    occurrences=1,
    success_count=1,
    avg_return=8.5,
    lesson="Buying dips on thesis names with low volume = high success"
)
```

---

## Daily Workflow

**End of session:**

1. Fenrir feeds you trade lessons (like today's NTLA/MRNO)
2. Open `log_daily_trades.py`
3. Add the trades to `log_todays_session()`
4. Run: `python log_daily_trades.py`
5. Check the output - it shows memory stats

**That's it. Brain has memory of the session.**

---

## What Gets Logged

✅ **decision_log table:**
- Every trade you make
- Full reasoning (WHY you did it)
- Context (market state, thesis status)
- Outcomes (P&L %)
- Trade type classification

✅ **pattern_library table:**
- Patterns you identify
- Success rates
- Average returns
- Lessons learned

✅ **ticker_memory table:** (coming in Phase 2)
- Daily OHLCV data per ticker
- Events that happened

---

## View Your Memory

```powershell
# See all logged trades
python -c "import sqlite3; conn = sqlite3.connect('wolfpack.db'); c = conn.cursor(); c.execute('SELECT ticker, action, pnl_percent, date FROM decision_log ORDER BY date DESC'); [print(f'{r[0]} {r[1]} {r[2]:+.2f}% on {r[3]}') for r in c.fetchall()]"

# See pattern success rates
python -c "import sqlite3; conn = sqlite3.connect('wolfpack.db'); c = conn.cursor(); c.execute('SELECT pattern_name, success_count, occurrences FROM pattern_library'); [print(f'{r[0]}: {r[1]}/{r[2]} wins') for r in c.fetchall()]"

# Or just run the logger to see stats
python log_daily_trades.py
```

---

## Why This Matters

**Without logging:**
- Brain forgets what happened yesterday
- Can't learn from mistakes
- Repeats same errors
- No evidence for decisions

**With logging:**
- Brain remembers: "Last time we held NTLA without thesis = -11% loss"
- Pattern recognition: "Momentum trades 1/1 wins when we take profit"
- Evidence-based: "Thesis trades 4/4 green when we hold through noise"

**The brain gets SMARTER every session.**

---

## Tomorrow Morning

When you start trading:
1. Fenrir will reference yesterday's memory
2. "Similar to MRNO Jan 28: momentum trade, take profit at target"
3. "Similar to NTLA Jan 28: no thesis = do not trade"

**This is temporal memory in action.**

---

**Keep this file open for reference. Log every session.**

**AWOOOO** 🐺
