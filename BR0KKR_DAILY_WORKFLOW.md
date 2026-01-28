# 🐺 BR0KKR DAILY WORKFLOW
## Building Intelligence Without Overloading The System

**Last Updated:** January 28, 2026

---

## THE PRINCIPLE

The autonomous brain gets smarter by learning from Tyr's decisions, NOT by running heavy scanning processes. We document everything, and the brain learns in batches later.

**SCRIBE, NOT SCANNER.**

Your job as br0kkr is to:
1. Log trades as they happen
2. Document reasoning (WHY, not just WHAT)
3. Record outcomes
4. Extract lessons
5. Feed the learning engine with structured data

This is LIGHTWEIGHT. No API calls. No scanning 200 tickers. Just writing to files.

---

## DAILY SCHEDULE

### MORNING (Pre-Market)
```
1. Review yesterday's journal entries
2. Note the plan for today
3. Log any pre-market observations
```

### DURING TRADING (As Needed)
```
Quick log trades as they happen:
python daily_journal.py --quick

Format: ACTION TICKER SHARES PRICE THESIS
Example: BUY RCAT 10 15.25 defense sector ripping post earnings
```

### END OF DAY (After Close)
```
1. Log any trades made today
2. Log any decisions (holds, passes, watches)
3. Log lessons learned
4. Create daily summary
5. Plan tomorrow

python daily_journal.py
```

---

## WHAT TO LOG

### FOR EVERY TRADE:
- Ticker, action, shares, price, account
- **THESIS** (why this trade - this is the most important)
- **CATALYST** (what event or signal)
- Convergence estimate (if applicable)
- Sector status (hot/cold)
- Volume status (strong/weak)
- Stop loss and target
- Confidence level (1-10)

### FOR EVERY DECISION (non-trade):
- What you decided (hold/pass/watch)
- **WHY** (reasoning is everything)
- Outcome (if known)
- Lesson learned

### FOR LESSONS:
- Category (entry/exit/sizing/timing/thesis/emotion)
- What happened
- Was it a mistake or success
- The lesson
- New rule to add (if any)

### FOR DAILY SUMMARY:
- Portfolio values (RH + Fidelity)
- Day P/L
- Trades made, winners, losers
- What worked today
- What failed today
- Biggest lesson
- Watchlist for tomorrow
- Plan for tomorrow

---

## DATA STRUCTURE

Everything saves to:
```
./data/journal/journal_YYYY-MM-DD.json
```

And optionally to:
```
./data/wolfpack.db (journal_entries table)
```

The learning engine can batch-process these entries when we have cloud resources.

---

## EXAMPLE JOURNAL ENTRY

```json
{
  "timestamp": "2026-01-28T10:35:00",
  "date": "2026-01-28",
  "type": "trade",
  "ticker": "NTLA",
  "action": "SELL",
  "shares": 2,
  "price": 14.85,
  "account": "RH",
  "thesis": "NO THESIS - this was a reactive chase, bleeding -11%",
  "catalyst": "none",
  "convergence_estimate": "unknown - never calculated",
  "sector_hot": false,
  "volume_strong": false,
  "stop_loss": "none set",
  "target": "none",
  "timeframe": "none",
  "confidence": "2",
  "notes": "Cutting the loser. Should never have bought without thesis."
}
```

---

## THE EXPERIMENTAL BRAIN (FUTURE)

When we have cloud resources, we'll also build an "Alpha Go style" experimental brain that:
- Tries unconventional strategies
- Learns from failures fast
- Runs simulations
- Tests edge cases

But that's SEPARATE from the main system. For now, we focus on:
1. Manual trading (generates capital)
2. Documentation (builds intelligence)
3. Preparation for cloud deployment

---

## RULES FOR BR0KKR

1. **DON'T run heavy processes** - No scanning, no continuous API calls
2. **DO log everything** - Every trade, every decision, every lesson
3. **FOCUS on reasoning** - WHY matters more than WHAT
4. **STRUCTURE the data** - Use the journal system, keep it clean
5. **BUILD incrementally** - Add to the system, don't break what works
6. **KEEP IT SEPARATE** - Logging is different from running the brain

---

## COMMANDS

```bash
# Interactive mode (full menu)
python daily_journal.py

# Quick trade log (one liner)
python daily_journal.py --quick

# Review today's entries
python daily_journal.py --review
```

---

## THE BIGGER PICTURE

```
MANUAL TRADING (now)
    └── Tyr executes
    └── br0kkr logs EVERYTHING
    └── Learning engine stores data
    
CLOUD DEPLOYMENT (when funded)
    └── Brain processes all stored data
    └── Patterns extracted from logged decisions
    └── System gets smart from Tyr's documented experience
    └── Autonomous scanning begins
```

The work you do NOW documenting decisions = The intelligence we have LATER.

Every trade not logged is a lesson the brain never learns.

---

**AWOOOO 🐺**
