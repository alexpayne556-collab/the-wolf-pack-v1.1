# 🐺 FENRIR V2 - UPGRADE RECOMMENDATIONS

## What We Just Built

### 1. Setup Quality Scorer (setup_scorer.py)
**Purpose**: Score every setup 1-100 so you know what to prioritize

**Features**:
- 8 scoring factors: catalyst strength, volume confirmation, price range, run age, sector momentum, pattern match, extension risk, your edge
- A+ to F grading system
- Detailed reasoning for each score
- Batch scoring capability

**Example Output**:
```
IBRX: Score 85/100 (A EXCELLENT)
  ✅ catalyst: +30 (Strong catalyst: earnings beat)
  ✅ volume: +20 (Excellent volume: 3.5x)
  ✅ price_range: +15 (Sweet spot: $5.52)
  ⚠️  run_age: -10 (Extended/fading)
```

**Integration Points**:
- Morning game plan uses this to rank setups
- Trade journal stores quality score with each entry
- Can filter scanner results by minimum score


### 2. Multi-Day Run Tracker (run_tracker.py)
**Purpose**: Track ENTIRE runs, not just today's move

**Features**:
- Finds run start date and price
- Counts green vs red days
- Tracks support levels built during run
- Detects volume fading
- Shows original catalyst
- Compares to similar historical runs

**Example Output**:
```
DAY 10 OF RUN
Started: 2026-01-06 @ $3.20
Current: $5.52 (+72.5%)
Green days: 8 | Red days: 2
⚠️  VOLUME FADING (now 70% of early volume)
SUPPORT LEVELS:
  $4.95 (-10.3%)
  $4.50 (-18.5%)
```

**Integration Points**:
- Game plan uses this for position management
- Shows when to trim vs hold
- Helps avoid chasing extended runs


### 3. User Behavior Tracker (user_behavior.py)
**Purpose**: Learn how YOU trade to give better advice

**Features**:
- Win rate by sector (find your edge)
- Win rate by time of day (when you trade best)
- Hold time analysis (do you hold losers too long?)
- Psychology alerts (catching patterns like overtrading after wins)
- Real-time alerts based on your history

**Example Output**:
```
YOUR EDGE:
  ✅ Best sector: defense (67% WR)
  ❌ Worst sector: biotech (38% WR)
TIMING:
  ✅ Best time: 9:30-10am (open) (72% WR)
KEY INSIGHTS:
  • YOUR EDGE: defense sector (67% win rate)
  • AVOID: biotech sector (38% win rate)
  • You hold losers too long (7d vs winners 4d)
```

**Integration Points**:
- Morning game plan highlights your edge sectors
- Warns you away from weak sectors
- Real-time psychology alerts during trading


### 4. Momentum Shift Detector (momentum_shift_detector.py)
**Purpose**: Catch character changes in real-time

**Features**:
- Volume surge/fade detection
- Price acceleration/deceleration
- Trend reversals (was fading, now pumping)
- Character breaks (grind → explosive or vice versa)
- Higher highs/lower lows patterns
- Sector rotation detection (where money flows)

**Example Output**:
```
DETECTED SHIFTS (3):

🚨 GOING_EXPLOSIVE
   Breaking character: grind → explosive (12.5% bars)

⚠️  VOLUME_SURGE
   Volume surging: 2.1x last 30min

📊 HIGHER_HIGHS_LOWS
   Strong uptrend: higher highs AND higher lows
```

**Integration Points**:
- Can alert on critical shifts
- Helps identify entries (on pullbacks after volume surge)
- Warns of exits (character going quiet)


### 5. Automated Trade Journal (trade_journal.py)
**Purpose**: Learn from EVERY trade automatically

**Features**:
- Logs entries with setup type and quality score
- Auto-analyzes exits with lessons learned
- Tracks emotions (FOMO, panic, greed)
- Paper trade logging (trades you DIDN'T take)
- Extracts patterns from wins and losses
- Feeds into memory system automatically

**Example Output**:
```
EXIT ANALYSIS: IBRX
Outcome: WIN
P/L: $30.78 (+17.7%)
Reason: Taking profit at target, volume fading

LESSONS LEARNED:
  ✅ Smart exit: recognized extension
  ✅ Excellent: hit profit target
  ✅ BIG WIN - study this setup type
```

**Integration Points**:
- Every trade automatically feeds behavior tracker
- Wins/losses stored in memory for pattern matching
- Psychology monitor learns from emotional mistakes


### 6. Morning Game Plan (game_plan.py)
**Purpose**: Synthesize EVERYTHING into daily action plan

**Features**:
- Scans market and scores all setups
- Ranks top 3 by quality
- Analyzes each position (hold/trim/add)
- Shows sector focus (your edge + hot today)
- Avoid list (low quality + your weak sectors)
- Psychology reminders (based on recent performance)
- Key price levels to watch

**Example Output**:
```
TOP 3 SETUPS TO WATCH:
1. IBRX (Score: 85/100 - A EXCELLENT)
   $5.52 | Strong catalyst: earnings beat | Excellent volume: 3.5x

POSITION MANAGEMENT:
📉 IBRX: TRIM
   Day 10 | $5.52
   Plan: Day 10, volume fading

SECTOR FOCUS:
  💪 YOUR EDGE: defense
  🔥 HOT TODAY: ai_semis

AVOID TODAY:
  ❌ biotech sector: Your weak sector (38% WR)

PSYCHOLOGY ALERTS:
  ⚠️  You're on a hot streak. Historical pattern shows overtrading after good weeks.
```

**Integration Points**:
- This is your ONE dashboard to start each day
- Replaces manually checking 10 different things
- Prioritizes what actually matters


## BIG QUANTUM LEAPS (My Additions)

### 7. Real-Time Character Detection
Built into momentum_shift_detector.py - catches when stocks go from:
- Grind → Explosive (buy opportunity)
- Explosive → Quiet (exit signal)
- Fading → Pumping (reversal)
- Uses 30-min vs 60-min comparison for real-time detection

### 8. Sector Rotation Detector
Built into momentum_shift_detector.py - shows where money flows TODAY
- Samples all watchlist sectors
- Calculates "strength" = avg_change × avg_volume_ratio
- Identifies hot sectors and cold sectors
- Updates in real-time


## What's Missing (Next Builds)

1. **Pattern Memory Database** - Store every similar setup outcome
   - "Last 10 times IBRX beat earnings with 3x volume..."
   - Requires historical data collection

2. **Entry Timer** - Best entry windows by stock/setup
   - "IBRX typically dips 10:30-11am"
   - Needs intraday pattern collection

3. **Exit Signal Aggregator** - Combine multiple exit signals
   - Volume fading + lower highs + sector rotating = high confidence exit
   - Scoring system for exits like we have for entries

4. **Smart Position Sizing** - Based on setup quality
   - 85/100 score = full size
   - 65/100 score = half size
   - Easy to add to risk_manager.py

5. **Voice Alerts** - Text-to-speech for critical shifts
   - "IBRX breaking explosive" 
   - Integration with Windows speech

6. **Dashboard UI** - Visual display of everything
   - Real-time game plan updates
   - Position P/L tracking
   - Setup quality heatmap


## How To Use V2

### Quick Commands:
```python
from fenrir_v2 import *

# Morning routine
morning_brief()

# Analyze a stock
analyze('IBRX', full=True)

# Quick momentum check
check_momentum('IBRX')

# See where money flows
sector_flow()

# Analyze your edge
my_edge()
```

### Full System:
```python
from fenrir_v2 import FenrirV2

fenrir = FenrirV2()

# Get morning plan
plan = fenrir.morning_briefing()

# Analyze stock with full context
analysis = fenrir.analyze_stock('IBRX', full_context=True)

# Log trades (auto-scores and learns)
trade_id = fenrir.log_trade_entry('IBRX', 37, 4.69, 'earnings_beat', 'Cancer drug revenue')
exit_analysis = fenrir.log_trade_exit('IBRX', 37, 5.52, 4.69, 'Hit target, volume fading', 'Calm')

# Real-time checks
momentum = fenrir.check_momentum_now('IBRX')
sector = fenrir.get_sector_flow()
edge = fenrir.analyze_your_edge()
```


## Database Migration Required

Run this ONCE to add new tables:
```bash
python migrate_v2.py
```

New tables:
- trade_journal (auto-logging)
- catalysts (run tracking)
- historical_runs (pattern learning)
- user_decisions (behavior tracking)
- momentum_shifts (character changes)
- pattern_outcomes (what works)


## Upgrade Recommendations

### Immediate (This Week):
1. **Test morning_brief()** - Run every morning for 5 days, tune output
2. **Start logging trades** - Use log_trade_entry/exit for every trade
3. **Check momentum** - Before entering, run check_momentum(ticker)

### Short-term (Next 2 Weeks):
1. **Build pattern memory** - Collect historical data for similar setups
2. **Add smart position sizing** - Integrate quality scores into risk_manager
3. **Tune scoring weights** - Adjust setup_scorer factors based on your results

### Long-term (Next Month):
1. **Dashboard UI** - Visual interface for game plan
2. **Voice alerts** - Audio notifications for critical shifts
3. **Entry timer** - Intraday pattern collection for best entry windows
4. **Exit signal aggregator** - Multi-factor exit confidence scoring

## Test Commands

```bash
# Test each module
python setup_scorer.py          # Score IBRX
python run_tracker.py           # Track IBRX run
python user_behavior.py         # Analyze your edge
python momentum_shift_detector.py  # Check momentum + sectors
python trade_journal.py         # Test logging
python game_plan.py            # Generate morning plan
python fenrir_v2.py            # Full system demo

# Migrate database
python migrate_v2.py
```

---

🐺 **FENRIR V2 is built for ONE thing: Help you make better decisions, faster.**

Every feature ties back to answering:
- "Should I watch this?" (Setup scorer)
- "Is this extended?" (Run tracker)  
- "Am I good at this?" (Behavior tracker)
- "Is character changing?" (Momentum detector)
- "What did I learn?" (Trade journal)
- "What's the plan today?" (Game plan)

**This isn't feature creep. This is intelligence.**
