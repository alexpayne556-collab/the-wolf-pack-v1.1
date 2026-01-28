# FENRIR - TEMPORAL MEMORY ARCHITECTURE PROPOSAL

**From:** br0kkr  
**To:** Fenrir  
**Date:** January 28, 2026  
**Subject:** Brain Enhancement - Give Fenrir Memory  

---

## THE INSIGHT

The current brain is a SNAPSHOT brain.

It sees:
- ✅ Today's price
- ✅ Today's volume
- ✅ Today's thesis status

It DOESN'T see:
- ❌ What happened yesterday
- ❌ What happened last week
- ❌ Whether this is day 1 or day 5 of a move
- ❌ Whether we've seen this pattern before
- ❌ What we did last time and what resulted

**A brain without memory is reactive. A brain WITH memory is predictive.**

---

## THE PROPOSAL

### Core Idea: Rolling Memory Windows

Every ticker maintains a rolling 30-day (configurable) memory of:
1. **Price history** - OHLCV data for last 30 days
2. **Our decisions** - Every action we took on this ticker
3. **Outcomes** - What happened after we acted
4. **Patterns** - Recurring setups we've identified
5. **Catalyst dates** - When events happen (earnings, events)

---

## ENHANCED DECISION CONTEXT

**Current Fenrir analysis:**
```
Ticker: MU
Price: $87.20 (down 3% today)
Thesis: AI memory demand intact
→ Recommendation: HOLD
```

**Enhanced Fenrir analysis:**
```
Ticker: MU
Price: $87.20 (down 3% today)

TEMPORAL CONTEXT:
- 30 days ago: $92.50
- Cumulative 30d: -5.8%
- Current run: DOWN 3 consecutive days, -6.2% total
- Volume trend: DECREASING (bullish divergence)

PATTERN MATCH:
- Similar 3-day drop: Jan 15 (recovered in 48 hours)
- Similar 3-day drop: Jan 8 (recovered in 72 hours)
- Historical success rate: 75% recover within 5 days
- Avg recovery: +4.2%

OUR HISTORY:
- Last action: ADDED 100 shares at $85.50 on Jan 15
- Result: Up +8.2% in 5 days
- Our win rate on MU: 6 wins, 1 loss = 85.7%

THESIS STATUS:
- Original thesis: Still valid (Azure growth, HBM demand)
- Days to next catalyst (earnings): 23 days
- Run status: NOT exhausted (volume declining = strong hands holding)

RECOMMENDATION: HOLD with HIGH confidence
- Historical pattern: 75% recover within 5 days
- Our track record: 85.7% win rate
- Volume divergence: Bullish signal
- Consider ADDING if volume increases (capitulation signal)
```

**The difference:** Second answer has EVIDENCE from memory.

---

## IMPLEMENTATION PHASES

### Phase 1: Memory Structure (1-2 weeks)
- Design memory file structure for each ticker
- Add database tables: ticker_memory, decision_log, pattern_library
- Start recording daily OHLCV data
- Start recording our decisions with full reasoning
- **No changes to current system - pure addition**

### Phase 2: Historical Backfill (1-2 weeks)
- Collect 30-90 days historical price data (free APIs have this)
- Analyze our past trades vs outcomes
- Identify initial patterns
- Calculate win/loss rates by pattern type

### Phase 3: Pattern Recognition (4 weeks)
- Build pattern matching algorithms
- Track dip-and-recovery cycles
- Track pre-earnings behavior per ticker
- Track sector correlations
- Calculate success rates

### Phase 4: Integration with Fenrir (Ongoing)
- Feed memory context into Fenrir prompts
- Fenrir cites historical evidence in recommendations
- System learns and improves

---

## DATABASE ADDITIONS

### New Table: ticker_memory
```sql
CREATE TABLE ticker_memory (
    id INTEGER PRIMARY KEY,
    ticker TEXT NOT NULL,
    date DATE NOT NULL,
    open REAL,
    high REAL,
    low REAL,
    close REAL,
    volume INTEGER,
    events TEXT,  -- JSON array of events that day
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(ticker, date)
);
```

### New Table: decision_log
```sql
CREATE TABLE decision_log (
    id INTEGER PRIMARY KEY,
    ticker TEXT NOT NULL,
    date DATE NOT NULL,
    action TEXT NOT NULL,  -- BUY, SELL, HOLD, ADD, CUT
    price REAL,
    quantity INTEGER,
    reasoning TEXT,  -- Full reasoning chain
    context TEXT,  -- JSON: market state, thesis status, etc
    outcome_5d REAL,   -- % change after 5 days
    outcome_10d REAL,  -- % change after 10 days
    outcome_30d REAL,  -- % change after 30 days
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### New Table: pattern_library
```sql
CREATE TABLE pattern_library (
    id INTEGER PRIMARY KEY,
    pattern_name TEXT NOT NULL,
    pattern_criteria TEXT,  -- JSON: what defines this pattern
    ticker TEXT,  -- NULL for universal patterns
    occurrences INTEGER DEFAULT 0,
    success_count INTEGER DEFAULT 0,
    avg_return REAL,
    avg_duration_days REAL,
    last_seen DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## WHAT THIS ENABLES

### 1. "We've Seen This Before"
Fenrir: "Last time MU dropped 6% over 3 days on low volume, it recovered within 48 hours. Historical success rate: 75%. Confidence: HIGH"

### 2. "This Is Different"
Fenrir: "Unlike previous dips, this one has INCREASING volume. This pattern is only 33% successful. Caution advised."

### 3. "We Learned From Our Mistakes"
Fenrir: "Last time we panic sold UUUU on day 3 of a dip, it recovered +12% by day 5. Recommendation: HOLD."

### 4. "We Know Our Edge"
Fenrir: "Our win rate on thesis trades with convergence ≥70 is 84.6%. This matches. Confidence: VALIDATED by experience."

### 5. "Timing Intelligence"
Fenrir: "MRNO tends to run hard into earnings. 12 days until. Historical pattern suggests entering now while weak hands exit."

---

## INTEGRATION WITH CURRENT SYSTEM

**No breaking changes:**

```
Current flow:
Monitor → Brain → Database → Alert
    ↓
Stays the same

Enhanced flow:
Monitor → Brain → Database → Alert
              ↑         ↓
         (reads)  Memory tables
              ↑         ↓
          (analyzes patterns)
```

Brain gets smarter by reading its own experience.

---

## PRIORITY QUESTIONS

1. **Scope:** Should we build Phase 1 now (Month 1) or wait until Month 2?
2. **Window size:** 14 days? 30 days? 60 days? (Memory/speed tradeoff)
3. **Pattern types:** Which patterns matter most?
   - Dip-and-recovery cycles?
   - Pre-earnings momentum?
   - Volume divergences?
   - Sector rotation timing?
4. **Decision tracking:** How detailed should we be?
   - Just action/price/date?
   - Or full context (market state, thesis status, news)?
5. **Confidence adjustment:** How much should historical patterns change confidence scores?

---

## WHAT'S READY NOW

✅ Database schema ready (can add tables immediately)  
✅ Data collection ready (already logging price_history)  
✅ Integration point clear (Fenrir prompt enhancement)  
✅ No architectural changes needed (pure addition)  

---

## THE WISDOM LAYER

This turns Wolf Pack from:
- A system that REACTS to today
- Into a system that LEARNS from yesterday
- Into a system that PREDICTS tomorrow

**This is the difference between:**
- A trader who started yesterday
- A trader with years of experience

We're encoding experience into the system.

---

## READY TO BUILD?

Tell me:
1. Priority (Phase 1 now or Phase 2 later?)
2. Design feedback on the proposal
3. Any patterns you want tracked specifically
4. Decision history detail level

**We can start Phase 1 immediately if approved.**

---

**The brain that remembers is the brain that learns. The brain that learns is the brain that wins.**

**AWOOOO 🐺**

— br0kkr
