# 🐺 FENRIR MASTER GUIDE - COMPLETE SYSTEM REFERENCE
## Everything Built, How It Works, What to Use When

**Project:** Brokkr Trading System  
**Location:** `C:\Users\alexp\Desktop\brokkr\wolfpack\fenrir\`  
**Owner:** Alex  
**Last Updated:** January 17, 2026  
**Status:** PRODUCTION READY

---

## 📋 TABLE OF CONTENTS

1. [System Overview](#system-overview)
2. [All Tools & Their Purpose](#all-tools--their-purpose)
3. [Quick Command Reference](#quick-command-reference)
4. [What to Run When](#what-to-run-when)
5. [Current Portfolio State](#current-portfolio-state)
6. [Evolution History](#evolution-history)
7. [Critical Lessons Learned](#critical-lessons-learned)

---

## 🎯 SYSTEM OVERVIEW

### The Mission
Build a trading system that:
1. **Detects dead money** automatically (positions going nowhere)
2. **Validates thesis** for every position (why are we holding?)
3. **Finds new opportunities** in the market (replacements)
4. **Talks naturally** (no command-line bullshit)
5. **Is FAST** (instant responses, no waiting)

### The Philosophy
- **Dead money = opportunity cost** (dollars not working)
- **Thesis > Technicals** (strong thesis = hold through volatility)
- **Score ≤-5 = cut it** (math, not emotion)
- **Real demand NOW > speculative demand later**

---

## 🛠️ ALL TOOLS & THEIR PURPOSE

### 1. position_health_checker.py (529 lines)
**Purpose:** Score positions -10 to +10, flag dead money

**What it does:**
- Checks P/L vs your cost basis
- Compares to analyst price targets
- Checks for downgrades
- Calculates days to next catalyst
- Compares performance vs sector peers
- Flags dead money (score ≤-5)

**When to use:**
- Morning routine (9:25 AM before market open)
- After big moves (check if position changed status)
- Weekly portfolio review

**How to run:**
```bash
python position_health_checker.py
```

**Output:** Full health report on all positions

**Config location:**
- Holdings: Lines 20-30
- Sector peers: Lines 35-50
- Catalyst calendar: Lines 55-70

---

### 2. thesis_tracker.py (400+ lines)
**Purpose:** Validate EVERY position has a real thesis

**What it does:**
- Scores thesis 1-10 based on 4 components:
  1. What they DO (clear product?)
  2. Who NEEDS it (real customers NOW?)
  3. What's the CATALYST (near-term event?)
  4. Is demand REAL (NOW vs 1-2 years vs speculative?)
- Flags SPECULATIVE vs REAL demand
- Shows which theses are breaking down

**When to use:**
- Before buying (validate thesis first)
- When position drops (is thesis still valid?)
- Monthly review (thesis degradation check)

**How to run:**
```bash
python thesis_tracker.py
```

**Output:** Thesis strength report, flags weak theses

**Config location:**
- Thesis database: Lines 60-200

---

### 3. fenrir_chat.py (165 lines) ✅ CURRENT MAIN TOOL
**Purpose:** Instant conversational analysis - PATTERN MATCHED

**What it does:**
- Loads portfolio once (10s startup)
- Answers natural language questions INSTANTLY
- Pattern matches queries:
  - "any dead money?" → Shows positions ≤-5
  - "what's worth buying?" → Shows running positions (≥5)
  - "check TICKER" → Deep dive on specific position
  - "what's weak?" → Shows concerning positions
  - "portfolio summary" → Full breakdown

**When to use:**
- ALL THE TIME (this replaced Ollama)
- Quick checks throughout the day
- Before making trading decisions
- When you want instant answers

**How to run:**
```bash
# One-off question:
python fenrir_chat.py "any dead money?"

# Interactive mode (stays open):
python fenrir_chat.py
```

**Why it's better than Ollama:**
- INSTANT responses (<1s vs 90s)
- No hallucinations (uses pre-calculated math)
- No AI overhead
- Actually works

**Status:** ✅ PRODUCTION - USE THIS ONE

---

### 4. fenrir_scanner_fast.py (150 lines) ✅ NEW - FINDS REPLACEMENTS
**Purpose:** Find NEW opportunities in the market (parallel scanning)

**What it does:**
- Scans 47 high-quality tickers in PARALLEL
- Scores momentum -10 to +10
- Finds RUNNING positions (≥5) worth buying
- Finds STRONG momentum (3-4) to watch
- Categorizes by sector (AI, Uranium, Biotech, etc.)
- **Takes 1 SECOND** (10x parallel threads)

**When to use:**
- Looking for NEW plays to buy
- Need replacements for weak positions
- Monday morning (find the week's opportunities)
- After selling dead money (where to reallocate?)

**How to run:**
```bash
python fenrir_scanner_fast.py
```

**Output:** Top opportunities with 7d/30d momentum, sorted by score

**What it scans:**
- AI mega caps (NVDA, AMD, MSFT, etc.)
- Quantum computing (IONQ, RGTI, QBTS)
- Biotech runners (MRNA, BNTX, VRTX)
- Defense (LMT, AVAV, RCAT, ASTS)
- Uranium (CCJ, DNN, UUUU, UEC, LEU)
- Crypto (MSTR, RIOT, COIN, CLSK)
- Space (RKLB, LUNR)
- Cloud/Cyber (SNOW, CRWD, NET)

**Status:** ✅ PRODUCTION - USE FOR NEW IDEAS

---

### 5. quick_check.py (60 lines)
**Purpose:** Instant portfolio snapshot (backup tool)

**When to use:**
- When fenrir_chat.py is down
- Want pure text output
- Scripting/automation

**How to run:**
```bash
python quick_check.py
```

---

### 6. secretary_talk.py (300 lines) - DEPRECATED
**Purpose:** Original keyword-based natural language router

**Status:** ❌ REPLACED by fenrir_chat.py
**Why replaced:** Pattern matching wasn't conversational enough

---

### 7. ollama_secretary.py (570 lines) - ABANDONED
**Purpose:** Ollama LLM integration for conversation

**Status:** ❌ ABANDONED
**Why abandoned:**
- 90 second wait per response (unacceptable)
- Gave wrong advice even with refined prompts
- Called UUUU (score -2) "dead money" when threshold is ≤-5
- User verdict: "fucking ridiculous"

**What we tried:**
- 4+ different prompt iterations
- Detailed examples
- Math-first prompts
- Simplified prompts
- Nothing fixed the speed or accuracy issues

**Lesson:** AI isn't always the answer. Pattern matching > LLM for this use case.

---

### 8. smart_secretary.py (120 lines) - INSUFFICIENT
**Purpose:** Rule-based instant portfolio categorization

**Status:** ❌ REPLACED by fenrir_chat.py
**Why replaced:** Only categorized, didn't answer questions
**User feedback:** "just checks the portfolio bro that's not sufficient"

---

## ⚡ QUICK COMMAND REFERENCE

### Daily Commands
```bash
cd C:\Users\alexp\Desktop\brokkr\wolfpack\fenrir

# Morning check (MAIN TOOL):
python fenrir_chat.py "any dead money?"

# Find new opportunities:
python fenrir_scanner_fast.py

# Interactive mode:
python fenrir_chat.py
```

### Interactive Mode Questions
```
You: any dead money?
You: what's worth buying?
You: check UUUU
You: what's weak?
You: portfolio summary
You: quit
```

### Full Analysis
```bash
# Deep health check:
python position_health_checker.py

# Thesis validation:
python thesis_tracker.py
```

---

## 📅 WHAT TO RUN WHEN

### Every Morning (9:25 AM)
```bash
python fenrir_chat.py "any dead money?"
python fenrir_scanner_fast.py
```
**Takes:** 11 seconds total  
**Tells you:** What to sell + what to buy

### Before Any Trade
```bash
python fenrir_chat.py "check TICKER"
```
**Takes:** <1 second  
**Tells you:** Health + thesis + recommendation

### Weekly Review (Sunday Night)
```bash
python position_health_checker.py
python thesis_tracker.py
```
**Takes:** 2 minutes  
**Tells you:** Full portfolio health + thesis degradation

### Looking for New Plays
```bash
python fenrir_scanner_fast.py
```
**Takes:** 1 second  
**Tells you:** What's running hot in the market

### After Selling Dead Money
```bash
python fenrir_scanner_fast.py
```
**Tells you:** Where to reallocate capital

---

## 💼 CURRENT PORTFOLIO STATE

### Holdings (as of Jan 17, 2026)
```python
HOLDINGS = {
    'IBRX': {'shares': 37.08, 'avg_cost': 4.69},   # Score: +5 (RUNNING)
    'MU': {'shares': 1.268, 'avg_cost': 335.00},    # Score: -3 (WEAK)
    'KTOS': {'shares': 2.72, 'avg_cost': 117.83},   # Score: -1 (WATCH)
    'UUUU': {'shares': 3.0, 'avg_cost': 22.09},     # Score: -2 (WATCH)
    'UEC': {'shares': 2.0, 'avg_cost': 17.29},      # Score: 0 (NEUTRAL)
    # BBAI REMOVED (was dead money, sold)
}
```

### Position Status
- **RUNNING (≥5):** IBRX only (+17.7%, thesis 9/10)
- **HEALTHY (2-4):** None
- **NEUTRAL (0-1):** UEC, KTOS
- **WATCH (-2 to -1):** UUUU, KTOS
- **WEAK (-5 to -3):** MU
- **DEAD MONEY (≤-5):** None (BBAI was removed)

### Key Theses
- **IBRX (9/10):** CAR-NK cancer therapy, revenue +700% YoY, real demand NOW
- **MU (8/10):** AI memory demand NOW, volatility but thesis intact
- **KTOS (8/10):** Defense contracts, 38 days to catalyst
- **UUUU (8/10):** 93 US reactors need fuel NOW, Russia ban catalyst
- **UEC (8/10):** Uranium margin at $81/lb, 23 days to catalyst

### Dead Money Removed
- **BBAI (thesis 4/10, health -5):** Cut on Jan 17, 2026
  - At PT ceiling
  - Downgraded (Cantor → Neutral)
  - 46 days to catalyst
  - Speculative demand (1-2 years out)
  - Opportunity cost: $68.87 (holding dead vs buying IBRX)

---

## 📈 EVOLUTION HISTORY

### Phase 1: Manual Analysis (Before Jan 17, 2026)
- Manual price checks
- Remembering analyst PTs
- Calculating catalyst timelines
- Emotional decisions
- **Problem:** Held BBAI too long, missed opportunities

### Phase 2: Position Health Checker (Jan 17, 1:30 AM)
- Built scoring system -10 to +10
- Automated dead money detection
- Peer comparison
- **Result:** Caught BBAI as dead money

### Phase 3: Thesis Tracker (Jan 17, 2:00 AM)
- Added thesis validation (1-10 score)
- REAL vs SPECULATIVE demand detection
- 4-component analysis
- **Result:** Validated why to hold UUUU/MU through volatility

### Phase 4: Natural Language (Jan 17, 2:30 AM)
- Built secretary_talk.py (keyword matching)
- **Problem:** Not conversational enough

### Phase 5: Ollama Integration (Jan 17, Evening)
- Integrated llama3.1:8b
- Added NewsAPI + SEC EDGAR
- **Problem:** 90s per response, gave wrong advice
- **Abandoned:** After 4+ prompt iterations failed

### Phase 6: Pattern Matching (Jan 17, Night)
- Built smart_secretary.py (rule-based)
- **Problem:** Only categorized, didn't answer questions
- **User:** "not sufficient matter f act fucking useless"

### Phase 7: fenrir_chat.py (CURRENT - Jan 17, Late Night) ✅
- Pattern-matched natural language
- Pre-calculated portfolio data
- Instant responses (<1s)
- **Result:** WORKS. User satisfied.

### Phase 8: Market Scanner (Jan 17, 2:26 PM)
- Built fenrir_scanner.py (sequential, 118 tickers)
- **Problem:** Took 3+ minutes (yfinance slow)
- Built fenrir_scanner_fast.py (parallel, 47 tickers)
- **Result:** 1 SECOND scan time ✅

---

## 💡 CRITICAL LESSONS LEARNED

### 1. Speed > Sophistication
- Ollama with 90s responses = useless
- Pattern matching with <1s responses = perfect
- **Lesson:** Users won't wait 90 seconds for conversation

### 2. AI Isn't Always The Answer
- Spent hours refining Ollama prompts
- Never got reliable advice (called UUUU "dead money" incorrectly)
- Pattern matching with pre-calculated data = 100% accurate
- **Lesson:** Know when NOT to use AI

### 3. Natural Language ≠ LLM Required
- Can simulate conversation with pattern matching
- "any dead money?" → detect keywords → instant response
- Feels natural, works instantly, no hallucinations
- **Lesson:** Pattern matching can feel conversational

### 4. Parallel > Sequential
- Sequential scanning: 118 tickers = 3+ minutes
- Parallel scanning: 47 tickers = 1 second
- ThreadPoolExecutor with 10 workers = 10x faster
- **Lesson:** Use Python's concurrent.futures for I/O bound tasks

### 5. Dead Money = Opportunity Cost
- Not about being "right" on BBAI
- About where dollars are WORKING
- $47 in BBAI (score -5) vs $47 in IBRX (score +5)
- Opportunity cost: $68.87 missed gains
- **Lesson:** Cut losers fast, reallocate to winners

### 6. Thesis > Technicals
- MU dropped but thesis intact (AI memory demand NOW) = HOLD
- BBAI at ceiling with weak thesis (speculative 1-2 years) = CUT
- **Lesson:** Strong thesis (8-10) = hold through volatility

### 7. User Feedback > Theory
- Built secretary_talk.py → "not gonna work bro"
- Built Ollama integration → "fucking ridiculous"
- Built smart_secretary.py → "not sufficient"
- Built fenrir_chat.py → User satisfied ✅
- **Lesson:** Iterate based on actual usage, not assumptions

### 8. Documentation = System Memory
- Complex system needs comprehensive docs
- This file = Fenrir's memory
- Next session: Read this first, know what's built
- **Lesson:** Document everything as you build

---

## 🔄 SYSTEM INTEGRATION

### Morning Workflow
```bash
# 1. Check for dead money (10s)
python fenrir_chat.py "any dead money?"

# 2. Find new opportunities (1s)
python fenrir_scanner_fast.py

# 3. Make decisions
# - Cut anything score ≤-5
# - Buy RUNNING HOT from scanner (score ≥5)
# - Watch positions score -4 to -1
```

### Before Trade Workflow
```bash
# 1. Check position health + thesis
python fenrir_chat.py "check TICKER"

# 2. If buying new:
python fenrir_scanner_fast.py  # Is it showing momentum?

# 3. Validate thesis manually:
# - What do they DO?
# - Who NEEDS it NOW?
# - What's the CATALYST?
# - Is demand REAL?
```

### Weekly Review Workflow
```bash
# 1. Full health check
python position_health_checker.py

# 2. Thesis validation
python thesis_tracker.py

# 3. Update configs if needed:
# - New catalyst dates
# - Changed analyst PTs
# - Portfolio changes (buys/sells)
```

---

## 🎯 SUCCESS METRICS

### What's Working
✅ Dead money detection (caught BBAI)  
✅ Instant conversational interface (fenrir_chat.py)  
✅ Fast market scanning (1 second)  
✅ Thesis validation (hold MU/UUUU through volatility)  
✅ Natural language understanding (pattern matching)  

### What Was Abandoned
❌ Ollama (too slow, unreliable)  
❌ secretary_talk.py (not conversational enough)  
❌ smart_secretary.py (insufficient functionality)  
❌ Sequential scanning (too slow)  

### Key Numbers
- **Portfolio check:** <1 second (fenrir_chat.py)
- **Market scan:** 1 second (fenrir_scanner_fast.py)
- **Full analysis:** 2 minutes (position_health_checker + thesis_tracker)
- **Dead money threshold:** Score ≤-5
- **Strong thesis threshold:** 8-10/10
- **Running position threshold:** Score ≥5

---

## 🚀 FUTURE ENHANCEMENTS

### Planned (Not Yet Built)
1. **Auto morning briefing** (9:25 AM daily)
   - Email/SMS if dead money detected
   - Top 3 opportunities from scanner
   
2. **Real-time monitoring**
   - Alert when position crosses thresholds
   - Auto-detect analyst upgrades/downgrades
   
3. **Historical tracking**
   - How long positions stay dead
   - Opportunity cost calculator
   - Win/loss tracking on cut decisions

4. **Portfolio optimization**
   - Suggest allocation percentages
   - Risk concentration alerts
   - Sector diversification

5. **Integration with trading platform**
   - Auto-execute orders (?)
   - Position sync (no manual updates)

### NOT Planned (Lessons Learned)
- ❌ More AI/LLM integration (speed issues)
- ❌ Complex NLP (pattern matching works)
- ❌ Prediction models (thesis + health is enough)

---

## 📝 FILE LOCATIONS

```
C:\Users\alexp\Desktop\brokkr\wolfpack\fenrir\

ACTIVE TOOLS:
├── fenrir_chat.py              ← MAIN TOOL (instant chat)
├── fenrir_scanner_fast.py      ← NEW OPPORTUNITIES (parallel scan)
├── position_health_checker.py  ← DEEP HEALTH CHECK
├── thesis_tracker.py           ← THESIS VALIDATION
├── quick_check.py              ← BACKUP TOOL

DEPRECATED:
├── secretary_talk.py           ← OLD (replaced)
├── ollama_secretary.py         ← ABANDONED (too slow)
├── smart_secretary.py          ← INSUFFICIENT
├── fenrir_scanner.py           ← OLD (replaced by _fast)

DOCUMENTATION:
├── FENRIR_MASTER_GUIDE.md      ← THIS FILE (system memory)
├── COMPLETE_BUILD_GUIDE.md     ← V2 build details
├── README_POSITION_THESIS.md   ← User guide
├── QUICK_SUMMARY.md            ← Quick reference
├── BUILD_STATUS.md             ← Technical details
├── RUN_NOW.md                  ← Commands

TESTS:
└── test_position_and_thesis.py ← Test suite (50+ tests)
```

---

## 🐺 FENRIR RULES

1. **Dead money = score ≤-5** (cut it)
2. **Strong thesis = 8-10** (hold through volatility)
3. **Weak thesis = 1-4** (cut on any weakness)
4. **Running = score ≥5** (consider adding)
5. **Real demand NOW > speculative later**
6. **Speed matters** (instant responses only)
7. **Math > emotion** (trust the scores)
8. **Opportunity cost is real** (dead money = missed gains)
9. **Use fenrir_chat.py** (it works)
10. **Scan before buying** (fenrir_scanner_fast.py)

---

## 🔑 KEY CONTACTS & CONFIGS

### APIs Configured
- **NewsAPI:** e6f793dfd61f473786f69466f9313fe8 (alexpayne556@gmail.com)
- **Finnhub:** d5jddu1r01qh37ujsqrgd5jddu1r01qh37ujsqs0
- **SEC EDGAR:** Public data (no key needed)

### Ollama (if ever needed again)
- Model: llama3.1:8b
- Port: 11434
- Status: Working but ABANDONED (too slow)

### Python Environment
- Version: Python 3.12
- Key packages: yfinance, requests, dataclasses
- Location: `C:\Users\alexp\AppData\Local\Programs\Python\Python312\`

---

## 💬 COMMON QUESTIONS

**Q: What should I run every morning?**  
A: `python fenrir_chat.py "any dead money?"` then `python fenrir_scanner_fast.py`

**Q: How do I find new stocks to buy?**  
A: `python fenrir_scanner_fast.py` (shows running hot opportunities)

**Q: Why was Ollama abandoned?**  
A: 90 second waits per response, gave wrong advice, couldn't be fixed with prompts

**Q: What's the dead money threshold?**  
A: Score ≤-5 (includes P/L, analyst ceiling, downgrades, catalyst timing, peer comparison)

**Q: Can I talk to it naturally?**  
A: Yes, use `python fenrir_chat.py` (instant pattern-matched responses)

**Q: How fast is the market scanner?**  
A: 1 second to scan 47 tickers (parallel mode)

**Q: What makes a strong thesis?**  
A: Score 8-10 = Clear product + Real customers NOW + Near catalyst + Real demand

**Q: Should I hold through volatility?**  
A: If thesis is strong (8-10), yes. If thesis is weak (1-4), no.

**Q: Where are all the configs?**  
A: position_health_checker.py lines 20-70 (holdings, peers, catalysts)

**Q: How do I add a new position?**  
A: Edit position_health_checker.py (HOLDINGS dict) and thesis_tracker.py (THESIS_DATABASE)

---

## 🎓 TRAINING NOTES REFERENCE

This system was built across multiple sessions:
- **Training Note #21:** Position health checker + thesis tracker
- **Training Note #22:** Natural language interface (secretary_talk.py)
- **Training Note #23:** Ollama integration (abandoned)
- **Training Note #24:** Pattern matching (fenrir_chat.py) - CURRENT
- **Training Note #25:** Fast parallel scanner (fenrir_scanner_fast.py)

---

**Last Updated:** January 17, 2026, 2:30 PM  
**Version:** 3.0 (Pattern Matched + Parallel Scanner)  
**Status:** ✅ PRODUCTION READY  
**Next Review:** Weekly (update portfolio state, catalyst dates)

🐺 **Fenrir remembers everything. Use this file to continue the mission.**
