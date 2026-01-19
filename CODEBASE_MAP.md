# 🐺 Wolf Pack Codebase Map

**Last Updated:** January 19, 2026  
**Version:** 5.6

This document explains what's what in the codebase - where we started, where we are, what failed, what's next.

---

## 🎯 Current Active System (v5.6)

**These are the files you should use:**

| File | Purpose | Status |
|------|---------|--------|
| `wolf_pack.py` | Main convergence engine - runs all 7 signals | ✅ ACTIVE |
| `wolf_pack_trader.py` | Automated trader bot (Alpaca integration) | ✅ ACTIVE (paper trading) |
| `services/convergence_service.py` | Scores signals, weights them | ✅ ACTIVE |
| `services/trade_learner.py` | Self-learning system - learns from wins/losses | ✅ ACTIVE |
| `services/trading_rules.py` | Market Wizards' 10 Commandments enforcer | ✅ ACTIVE |
| `services/risk_manager.py` | Position sizing (Kelly Criterion, 2% max) | ✅ ACTIVE |
| `services/pivotal_point_tracker.py` | Livermore's pattern tracker | ✅ ACTIVE |
| `services/earnings_service.py` | Earnings catalyst scanner | ✅ ACTIVE |
| `services/news_service.py` | News sentiment analyzer | ✅ ACTIVE |
| `pattern_learner.py` | Analyzes what works vs what doesn't | ✅ ACTIVE |
| `daily_monitor.py` | Daily trade monitoring | ✅ ACTIVE |

---

## 📚 Documentation (The Journey)

**These show where we've been:**

| File | What It Documents |
|------|-------------------|
| `THE_LEONARD_FILE.md` | Complete continuation file - everything Fenrir needs |
| `THE_BIG_PICTURE.md` | System architecture overview |
| `WOLF_PACK_ARCHITECTURE.md` | Technical architecture |
| `WOLF_PACK_GUIDE.md` | User guide |
| `HONEST_SYSTEM_AUDIT.md` | Honest assessment of what works/doesn't |
| `REAL_STATUS.md` | Real status (not marketing) |
| `VALIDATION_REPORT.md` | What we validated |

---

## 🧪 Old Experiments (What We Tried)

**These are old modules we tested. Some failed. Some evolved.**

### Scanner Evolution

| File | What It Was | Outcome |
|------|-------------|---------|
| `fenrir/fenrir_scanner.py` | Original scanner (basic) | ⚠️ REPLACED by wolf_pack.py |
| `fenrir/fenrir_scanner_v2.py` | Second iteration | ⚠️ REPLACED by convergence system |
| `fenrir/fenrir_scanner_fast.py` | Speed-optimized version | ⚠️ Merged into wolf_pack.py |
| `src/layer1_hunter/sec_speed_scanner.py` | SEC filing speed scanner | ✅ WORKS but not integrated yet |
| `src/layer1_hunter/wolf_pack_scanner.py` | Early wounded prey detector | ⚠️ Evolved into convergence_service.py |

### Trade Tracking Evolution

| File | What It Was | Outcome |
|------|-------------|---------|
| `wolfpack_db.py` | First database attempt | ⚠️ REPLACED by wolfpack_db_v2.py |
| `wolfpack_db_v2.py` | Second database version | ⚠️ REPLACED by pattern_learner.py |
| `outcome_tracker.py` | Manual outcome tracking | ⚠️ REPLACED by trade_learner.py |
| `decision_logger.py` | Logged decisions | ⚠️ Merged into wolf_pack_trader.py |

### Analysis Tools (Still Useful)

| File | Purpose | Status |
|------|---------|--------|
| `wolfpack_analyzer.py` | Post-trade analysis | ✅ USEFUL for deep dives |
| `move_investigator.py` | Investigates why stocks moved | ✅ USEFUL for research |
| `wolfpack_daily_report.py` | Daily summary generator | ✅ USEFUL |
| `test_investigation.py` | Tests investigation tools | ✅ USEFUL for validation |

---

## 🔬 Test Files (Don't Delete)

**These validate the system:**

| File | What It Tests |
|------|---------------|
| `test_all_systems.py` | Full system integration test |
| `test_phase2.py` | Convergence system test |
| `test_phase3.py` | Brain integration test |
| `test_apis_only.py` | API connectivity test |
| `test_capture.py` | Data capture test |
| `fenrir/test_scanner.py` | Scanner validation |
| `fenrir/validate_scanner.py` | Scanner accuracy test |
| `fenrir/stress_test.py` | Load testing |

---

## 📦 Fenrir Folder (AI Assistant System)

**This is the local Ollama AI system - experimental:**

| File | Purpose | Status |
|------|---------|--------|
| `fenrir/ollama_brain.py` | Ollama integration | ⏳ EXPERIMENTAL |
| `fenrir/fenrir_chat.py` | Chat interface | ⏳ EXPERIMENTAL |
| `fenrir/fenrir_secretary.py` | Secretary/assistant | ⏳ EXPERIMENTAL |
| `fenrir/ollama_secretary.py` | Ollama secretary | ⏳ EXPERIMENTAL |
| `fenrir/natural_language.py` | NLP interface | ⏳ EXPERIMENTAL |

**Status:** These work locally but aren't required for trading. Tyr's experiment with local AI memory.

---

## 🚨 What Failed (Important Lessons)

### Day 1 Confirmation Theory
- **File:** Not saved (intentionally - it failed)
- **Theory:** Stocks that confirm on day 1 tend to continue
- **Test:** 100 stocks, 49.4% win rate
- **Result:** ❌ BUSTED - Coin flip accuracy
- **Lesson:** First-day pops mean nothing without context

### Buy the Pop Theory
- **File:** Not saved
- **Theory:** Buy stocks popping 5%+ on volume
- **Test:** 50 stocks
- **Result:** ❌ BUSTED - Too many traps
- **Lesson:** Need convergence, not just volume

### Overfiltering Problem
- **File:** Early versions of convergence_service.py
- **Issue:** Required ALL 7 signals = too strict
- **Result:** ❌ Missed 60% of valid setups
- **Fix:** Weighted scoring system (convergence 85+, not perfect 100)
- **Lesson:** Perfection kills opportunity

---

## 🚀 What's Next (Roadmap)

### Phase 4: Sector Rotation (In Progress)
- **File:** `services/sector_flow_tracker.py`
- **Status:** 50% complete
- **Goal:** Detect when money flows between sectors
- **Why:** Catch sector momentum early

### Phase 5: Correlation Tracking
- **File:** `fenrir/correlation_tracker.py` (exists, not integrated)
- **Status:** Built but not tested
- **Goal:** Find stocks that move together, catch divergences
- **Why:** When correlation breaks = opportunity

### Phase 6: News Decay Analysis
- **File:** `fenrir/catalyst_decay_tracker.py` (exists, not integrated)
- **Status:** Built but not tested
- **Goal:** Track how long catalyst effects last
- **Why:** Know when to exit momentum plays

### Phase 7: Liquidity Trap Detection
- **File:** `fenrir/liquidity_trap_detector.py` (exists, not integrated)
- **Status:** Built but not tested
- **Goal:** Avoid low-liquidity traps
- **Why:** Can't exit if no buyers

---

## 🗺️ Architecture Evolution

### v1.0 - The Beginning (Dec 2025)
- Basic scanner
- Manual analysis
- No brain

### v2.0 - Convergence System (Early Jan 2026)
- 7 signals
- Weighted scoring
- Still manual execution

### v3.0 - Brain Integration (Mid Jan 2026)
- Added Ollama local AI
- Pattern recognition
- Memory system (Leonard File)

### v4.0 - Livermore's Pattern (Jan 18, 2026)
- Pivotal point tracking
- Automated entries/exits
- Still in testing

### v5.0 - Self-Learning (Jan 18, 2026)
- Trade learner
- Learns from wins/losses
- Adaptive rules

### v5.6 - Market Wizards (Jan 19, 2026) ← YOU ARE HERE
- 10 Commandments enforced
- PTJ's 200-MA rule
- 5:1 R/R minimum
- Self-healing system

### v6.0 - Full Automation (Future)
- Autonomous trading
- Real-time monitoring
- Self-improvement loop

---

## 📝 How to Navigate This Codebase

**If you want to:**

**Understand the system:**
1. Read `THE_LEONARD_FILE.md` (complete context)
2. Read `THE_BIG_PICTURE.md` (architecture)
3. Read `HONEST_SYSTEM_AUDIT.md` (reality check)

**Run the scanner:**
1. `python wolf_pack.py` (main system)
2. Or `RUN_WOLFPACK.bat` (Windows shortcut)

**Trade with it:**
1. Set up API keys (see `SETUP.md`)
2. Configure `config.py`
3. Run `python wolf_pack_trader.py` (paper trading first!)

**Analyze past trades:**
1. `python pattern_learner.py` (what worked/failed)
2. `python wolfpack_analyzer.py` (deep dive)
3. `python move_investigator.py` (why it moved)

**Test a theory:**
1. Use issue templates in `.github/ISSUE_TEMPLATE/`
2. Document methodology
3. Share results (wins AND losses)

---

## 🧭 File Naming Convention

**Pattern we follow:**

- `wolf_pack*.py` = Main system files
- `*_service.py` = Service modules (in `services/`)
- `*_tracker.py` = Tracking/monitoring tools
- `test_*.py` = Test files
- `*_COMPLETE.md` = Progress milestones
- `*.bat` = Windows shortcuts

---

## ❓ Why Keep Old Files?

**Three reasons:**

1. **Learning:** Shows what didn't work (valuable!)
2. **Evolution:** Someone might see value we missed
3. **Transparency:** We build in public, document failures

**Example:**  
`wolfpack_db.py` failed as a database design. But someone might look at it and say "Hey, this approach works for X use case." We don't delete history.

---

## 🐺 The Philosophy

**"The pattern Livermore used 100 years ago is the same pattern we hunt now. The names change. The pattern persists."**

This codebase is a JOURNEY, not a product. We show:
- What worked
- What failed
- What we learned
- Where we're going

If you see an old module and think "This is valuable in a different direction" - SPEAK UP. That's pack mentality.

---

## 📧 Questions?

Email: alexpayne556@gmail.com  
Subject: "Wolf Pack - Codebase Question"

🐺 LLHR
