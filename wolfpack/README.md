# 🐺 WOLF PACK DATA SYSTEM
## Self-Learning Market Intelligence Engine

**Updated:** January 15, 2026

---

## Mission

Build a self-learning system that:
- ✅ Tracks 99 stocks across 11 sectors
- ✅ Records ALL data daily (price, volume, technicals, moves)
- ✅ Auto-investigates big moves to find WHY
- ✅ Alerts on portfolio/watchlist/sector events
- ✅ Learns patterns over time
- ✅ Generates comprehensive daily reports

---

## Quick Start

### 1. Install
```bash
cd c:\Users\alexp\Desktop\brokkr\wolfpack
pip install yfinance pandas numpy
```

### 2. Initialize
```bash
python wolfpack_db.py
```

### 3. Daily Workflow (After 4:30 PM ET)
```bash
# Update forward returns
python wolfpack_updater.py

# Capture today's data
python wolfpack_recorder.py

# Investigate big moves
python move_investigator.py

# Check for alerts
python alert_engine.py

# Generate daily report
python wolfpack_daily_report.py
```

---

## System Components

### 1. Data Collector ([wolfpack_recorder.py](wolfpack_recorder.py))
**Captures daily:**
- Price: open, high, low, close
- Volume: today, 20d avg, ratio, dollar volume
- Returns: 1d, 5d, 20d, 60d
- Technicals: SMA 20/50/200, RSI, position above SMAs
- Context: 52w high/low distance, consecutive green/red days
- Move classification: size, direction, gap detection

**Universe:** 99 stocks across 11 sectors (Holdings, Defense, Space, Nuclear, Semis, AI/Tech, Biotech, Quantum, Crypto, Materials, EVs, Energy)

---

## Files

```
wolfpack/
├── config.py                  # Universe + settings
├── wolfpack_db.py            # Database setup + helpers
├── wolfpack_recorder.py      # Daily data capture
├── wolfpack_updater.py       # Forward return calculator
├── wolfpack_analyzer.py      # Pattern discovery
├── wolfpack_daily_report.py  # Daily summary
├── data/
│   └── wolfpack.db           # SQLite database
└── reports/
    └── daily_YYYYMMDD.txt    # Saved reports
```

---

## Analysis Questions Answered

After 30 days of data:

1. **Color Bias:** Were winners green or red the day before?
2. **Volume Bias:** What was volume ratio before explosion?
3. **Extension Bias:** Were they already extended (60d return)?
4. **Sector Distribution:** Which sectors produce most winners?
5. **52w Positioning:** Were they near highs or wounded prey?
6. **Red Streaks:** Did they have consecutive red days before reversal?

---

## Example Output

### Daily Report:
```
📈 TODAY'S BIG MOVERS (5%+):
Ticker   Sector       Price      Today%     Vol      60d%       Setup?
BKSY     Space        $29.61     +7.1%      0.8x     +50%       NO (extended)
UUUU     Nuclear      $5.21      +7.7%      3.2x     +4%        YES ✅

🔥 DAY 2 CONFIRMATIONS (Yesterday 5%+, Today green):
Ticker   Sector       Yest%      Today%     60d%       Vol      Valid?
QUBT     Quantum      +7.0%      +3.0%      -23%       2.1x     YES ✅

🎯 SECTOR MOMENTUM:
Space:     +2.3% avg today
Nuclear:   +1.8% avg today
Defense:   +1.2% avg today
```

### Pattern Analysis:
```
📊 ANALYSIS 1: COLOR BIAS
Green day before explosion: 23 (54.8%)
Red day before explosion:   19 (45.2%)

📊 ANALYSIS 2: VOLUME BIAS
Average volume ratio: 2.3x
High volume (3x+): 12 winners, avg forward_10d: +31.2%

📊 ANALYSIS 3: EXTENSION BIAS
Compressed (60d <0%):    18 winners, avg forward_10d: +28.4%
Extended (60d >30%):     8 winners, avg forward_10d: +22.1%

🔥 TOP 10 PERFORMERS:
QUBT   | Quantum    | 2026-01-05 | forward_10d: +47.3% | Day before: -2.1% | Vol: 4.2x | 60d: -18.2%
```

---

## Key Principles

✅ **NO FILTERING ON CAPTURE** - Record everything, every day  
✅ **FILTER ON ANALYSIS** - Apply thresholds when querying  
✅ **FORWARD RETURNS = TRUTH** - This is how we know what worked  
✅ **PATTERNS EMERGE FROM DATA** - Don't guess, measure  

---

## Success Criteria

**After 30 days:**
- Can answer: "What did +20% winners look like the day before?"
- Can answer: "What's the Day 2 confirmation rate?"
- Can answer: "Does extension matter?"

**After 60 days:**
- Statistical validation of patterns
- Documented edge
- Repeatable system

---

## 🐺 LLHR

*"Capture everything. Filter nothing. Let truth reveal itself."*

Build complete. Ready for tomorrow.
