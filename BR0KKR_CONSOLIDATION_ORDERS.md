# 🐺 BR0KKR CONSOLIDATION ORDERS
## Date: January 19, 2026
## From: Tyr + Fenrir
## Priority: EXECUTE NOW

---

# THE MISSION

We have 108 Python files. Most are dead weight, duplicates, or dormant gold that's not wired in. 

**Goal:** Clean house, then transform gold into something USEFUL - not just informative.

**Philosophy:** We don't want rear-view mirrors. We want windshields.

| Rear View (USELESS) | Windshield (USEFUL) |
|---------------------|---------------------|
| "You were in CHOP regime" | "You're entering CHOP - adjust strategy NOW" |
| "You made a mistake" | "You're ABOUT to make a mistake - BLOCKED" |
| "That was illiquid" | "This is illiquid - DON'T ENTER" |
| "KTOS led MU yesterday" | "KTOS just moved - MU setup triggered NOW" |
| "Your setup scored 45" | "Setup weak - wait for better OR size down" |

**The difference:** Past tense = historian. Present/future tense = PARTNER.

---

# PHASE 1: CLEAN HOUSE

## Step 1.1: Create ARCHIVED_IDEAS.md

Before deleting anything, extract the CORE CONCEPT from each dead file.

Format:
```
## [filename]
**Original Purpose:** [1-2 sentences - what was it trying to do?]
**Useful Logic:** [Any code patterns worth remembering? If none, write "None"]
**Why Killed:** [Duplicate / Obsolete / Tutorial / Debug]
```

This preserves the IDEAS without keeping the dead code.

---

## Step 1.2: DELETE Dead Weight (30 files)

### Tutorial Code (6 files) - DELETE ALL
```
wolfpack/fenrir/SECTION_1_SETUP.py
wolfpack/fenrir/SECTION_2_CREATE_FENRIR.py
wolfpack/fenrir/SECTION_3_MARKET_SCANNER.py
wolfpack/fenrir/SECTION_4_CATALYST_HUNTER.py
wolfpack/fenrir/SECTION_5_FENRIR_ANALYSIS.py
wolfpack/fenrir/SECTION_6_QUIZ_AND_TRAIN.py
```
**Why:** Tutorial/learning code. Not production.

---

### Old Tests (15 files) - DELETE ALL
```
wolfpack/test_phase2.py
wolfpack/test_phase3.py
wolfpack/test_capture.py
wolfpack/test_investigation.py
wolfpack/fenrir/test_scanner.py
wolfpack/fenrir/test_ibrx.py
wolfpack/fenrir/test_fixed_prompt.py
wolfpack/fenrir/test_fixes.py
wolfpack/fenrir/simple_test.py
wolfpack/fenrir/quick_check.py
wolfpack/fenrir/stress_test.py
wolfpack/fenrir/test_all_systems.py
```
**Why:** One-off tests, duplicates, obsolete. Keep only `test_all_systems.py` in root.

**BEFORE DELETING test_full_system.py:** Check if any unique tests exist. If so, merge into root `test_all_systems.py`, then delete.

---

### Debug Utilities (6 files) - DELETE ALL
```
wolfpack/check_bytes.py
wolfpack/check_syntax.py
wolfpack/count_all_quotes.py
wolfpack/find_quotes.py
wolfpack/show_context.py
wolfpack/services/debug_rss.py
```
**Why:** One-time debug scripts. Not needed.

---

### Duplicate Secretaries (3 files) - DELETE ALL
```
wolfpack/fenrir/secretary_talk.py
wolfpack/fenrir/smart_secretary.py
wolfpack/fenrir/fenrir_secretary.py
```
**Why:** Three versions of the same thing. Keep only `ollama_secretary.py`.

---

## Step 1.3: DELETE Duplicate Scanners (5 files)

```
wolfpack/fenrir/fenrir_scanner.py
wolfpack/fenrir/fenrir_scanner_fast.py
wolfpack/fenrir/fenrir_scanner_v2.py
wolfpack/fenrir/full_scanner.py
wolfpack/fenrir/validate_scanner.py
```
**Why:** `wolf_pack.py` IS the scanner now. These are obsolete.

---

## Step 1.4: DELETE Duplicate Services (6 files)

```
wolfpack/fenrir/alerts.py              → Use alert_engine.py instead
wolfpack/fenrir/catalyst_calendar.py   → Use services/catalyst_service.py instead
wolfpack/fenrir/news_fetcher.py        → Use services/news_service.py instead
wolfpack/fenrir/risk_manager.py        → Use services/risk_manager.py instead
wolfpack/fenrir/portfolio.py           → Use position_health_checker.py instead
wolfpack/fenrir/correlation_tracker.py → Use cross_pattern_correlation_engine.py instead
```

**BEFORE DELETING:** Check each for any unique logic not in the kept version. Document in ARCHIVED_IDEAS.md if found.

---

## Step 1.5: Verify After Cleanup

After deleting 35 files:
1. Run `test_all_systems.py` - must still pass 10/10
2. Count remaining files - should be ~73
3. Git commit with message: "CLEANUP: Removed 35 dead/duplicate files"

---

# PHASE 2: CONSOLIDATE DUPLICATES

## Step 2.1: Merge 3 SEC Implementations → 1

**Files to merge:**
- `wolfpack/services/br0kkr_service.py` (771 lines - Form 4, 13D, 13G)
- `wolfpack/fenrir/sec_fetcher.py` (182 lines - 8-K, 10-K, 10-Q)
- `src/layer1_hunter/sec_speed_scanner.py` (304 lines - 8-K speed scanning)

**Create:** `wolfpack/services/sec_edgar_service.py`

**Must include:**
- Form 4 insider tracking (buy/sell detection)
- 13D/13G activist tracking
- 8-K speed scanning with catalyst keyword detection
- 10-K, 10-Q filing access
- Unified API: `get_insider_activity(ticker)`, `get_activist_filings(ticker)`, `scan_8k_filings()`, `get_financials(ticker)`

**After merge:** Delete the 3 original files.

---

## Step 2.2: Merge 3 Database Systems → 1

**Files to merge:**
- `wolfpack/wolfpack_db.py` (303 lines)
- `wolfpack/wolfpack_db_v2.py` (273 lines)
- `wolfpack/fenrir/database.py` (436 lines)

**Create:** `wolfpack/database.py` (unified)

**Must include all tables from all 3:**
- Daily records, patterns, sectors (from wolfpack_db)
- User decisions, catalysts, realtime moves (from wolfpack_db_v2)
- Fenrir-specific tables (from fenrir/database)

**Migration:**
1. Create new unified schema
2. Write migration script to move existing data
3. Update all imports across codebase
4. Test thoroughly
5. Delete the 3 original files

---

## Step 2.3: Merge Learning Systems → 1

**Files to merge:**
- `wolfpack/services/trade_learner.py` (496 lines)
- `wolfpack/pattern_learner.py` (120 lines)
- `wolfpack/fenrir/trade_journal.py` (284 lines)
- `wolfpack/fenrir/failed_trades.py` (136 lines)
- `wolfpack/outcome_tracker.py` (154 lines)

**Create:** `wolfpack/services/learning_engine.py`

**Must include:**
- Trade outcome tracking (Day 1, 3, 5, 10 returns)
- Pattern learning from YOUR trades
- Failed trade analysis
- Behavior pattern detection
- Unified API: `log_trade()`, `analyze_outcome()`, `get_patterns()`, `get_mistakes()`

---

## Step 2.4: Merge Configs → 1

**Files:**
- `wolfpack/config.py` (126 lines) - KEEP as primary
- `wolfpack/fenrir/config.py` (88 lines) - MERGE into primary, then delete

---

# PHASE 3: TRANSFORM GOLD INTO PARTNERS

This is where we turn rear-view mirrors into windshields.

## Gold Module 1: market_regime_detector.py (436 lines)

**Current behavior:** Detects regime (GRIND/EXPLOSIVE/CHOP/CRASH/ROTATION/MEME)

**Transform into PARTNER:**

1. **Run automatically** at start of each wolf_pack.py scan
2. **Store current regime** in database with timestamp
3. **Adjust signal weights** based on regime:

| Regime | Wounded Prey | Running Prey | Mean Reversion | Breakout |
|--------|--------------|--------------|----------------|----------|
| GRIND | Normal | Boost | Normal | Reduce |
| EXPLOSIVE | Reduce | Boost | Reduce | Boost |
| CHOP | Reduce | Reduce | Boost | Reduce |
| CRASH | Boost | Reduce | Reduce | Reduce |
| ROTATION | Normal | Normal | Normal | Normal |

4. **Alert on regime CHANGE:** "⚠️ REGIME SHIFT: GRIND → CHOP. Adjusting strategy weights."
5. **Block certain trades** in certain regimes: "❌ BLOCKED: Breakout play in CHOP regime - low probability"

**Integration point:** `wolf_pack.py` - call at start of `scan_market()`

---

## Gold Module 2: predictive_mistake_engine.py (581 lines)

**Current behavior:** Analyzes behavior patterns, predicts mistake probability

**Transform into PARTNER:**

1. **Run before EVERY trade decision** in `wolf_pack_trader.py`
2. **Calculate mistake probability** based on:
   - Time since last trade
   - Recent P/L (winning/losing streak)
   - Time of day
   - Number of trades today
   - Emotional indicators
3. **If probability > 70%:** BLOCK the trade with explanation
   - "❌ BLOCKED: 73% overtrade probability. You've made 4 trades in 2 hours after a win streak. Cool down."
4. **If probability 50-70%:** WARN but allow
   - "⚠️ WARNING: 62% mistake probability. Proceed with caution. Consider smaller size."
5. **If probability < 50%:** Silent - proceed normally
6. **Log all predictions** for learning (was it right?)

**Integration point:** `wolf_pack_trader.py` - call before `execute_trade()`

---

## Gold Module 3: liquidity_trap_detector.py (311 lines)

**Current behavior:** Analyzes spread, volume, market cap for liquidity risk

**Transform into PARTNER:**

1. **Run on EVERY ticker** before adding to watchlist or convergence scan
2. **Calculate liquidity score** 0-100:
   - 0-30: ILLIQUID TRAP - Block entry
   - 31-50: LOW LIQUIDITY - Warn, reduce size
   - 51-70: MODERATE - Proceed with caution
   - 71-100: LIQUID - Normal trading
3. **For scores 0-30:** BLOCK with explanation
   - "❌ BLOCKED: XYZZ liquidity score 23/100. Avg volume 12K, spread 3.2%. You WILL get trapped."
4. **For scores 31-50:** WARN and auto-reduce position size
   - "⚠️ LOW LIQUIDITY: ABCD score 42/100. Max position reduced to 50% of normal."
5. **Add to convergence score** as negative weight for low liquidity

**Integration point:** `convergence_service.py` - add as 8th signal (negative weight)

---

## Gold Module 4: cross_pattern_correlation_engine.py (474 lines)

**Current behavior:** Detects lead/lag relationships between tickers

**Transform into PARTNER:**

1. **Build correlation database** from historical data
2. **Monitor leaders in real-time** during market hours
3. **When leader moves:** ALERT on follower opportunity
   - "🎯 CORRELATION ALERT: KTOS +6.2% pre-market. Historical: MU follows +4.1% by 11am (83% hit rate, 47 samples)"
4. **Include in convergence** as 9th signal when correlation triggers
5. **Track prediction accuracy** - was MU actually up by 11am?
6. **Auto-adjust confidence** based on recent accuracy

**Integration point:** `convergence_service.py` - add as 9th signal; `realtime_monitor.py` - trigger alerts

---

## Gold Module 5: momentum_shift_detector.py (312 lines)

**Current behavior:** Detects volume surge/fade, acceleration, reversals

**Transform into PARTNER:**

1. **Run continuously** during market hours on held positions
2. **Detect character change** in real-time:
   - Volume surge (3x+ average)
   - Volume fade (dropping while price rises - bearish divergence)
   - Acceleration (momentum increasing)
   - Deceleration (momentum fading)
   - Reversal signals
3. **Alert on shift:** 
   - "⚠️ MOMENTUM SHIFT: IBRX volume fading. 2.1M last hour vs 4.3M avg. Character change - consider tightening stop."
4. **Suggest action** based on shift type:
   - Volume surge up: "Consider adding"
   - Volume fade: "Consider tightening stop"
   - Reversal signal: "Consider exit"

**Integration point:** `realtime_monitor.py` - run on positions; `position_health_checker.py` - add shift status

---

## Gold Module 6: emotional_state_detector.py (498 lines)

**Current behavior:** Detects FOMO, revenge, tilt from trading behavior

**Transform into PARTNER:**

1. **Calculate emotional state** from recent behavior:
   - Rapid-fire trades = possible tilt
   - Buying after big loss = possible revenge
   - Chasing extended stocks = possible FOMO
   - Trading outside normal hours = possible anxiety
2. **Integrate with trading_rules.py** 10 Commandments
3. **When state detected:** WARN or BLOCK
   - "❌ BLOCKED: Revenge trade detected. You lost $47 on BBAI 2 hours ago. This buy doesn't fit your criteria. Cool down."
   - "⚠️ FOMO ALERT: This stock is +34% in 3 days. You're chasing. Is this wounded prey or running prey? Be honest."
4. **Require confirmation** for emotional trades:
   - "Type 'I UNDERSTAND THE RISK' to proceed despite warning"

**Integration point:** `trading_rules.py` - enhance 10 Commandments; `wolf_pack_trader.py` - check before trade

---

## Gold Module 7: setup_scorer.py (255 lines)

**Current behavior:** Scores setup quality 0-100 based on technicals

**Transform into PARTNER:**

1. **Score every setup** in convergence scan
2. **Adjust position sizing** based on score:
   - 80-100: Full size (high conviction)
   - 60-79: 75% size
   - 40-59: 50% size
   - Below 40: DON'T TRADE or paper trade only
3. **Show score breakdown:**
   - "Setup Score: 72/100 (Price action: 18/25, Volume: 20/25, Sector: 16/25, Catalyst: 18/25)"
4. **Compare to historical:** 
   - "Similar setups (score 70-75) have 61% win rate, avg return +8.3%"

**Integration point:** `convergence_service.py` - add to technical signal; `risk_manager.py` - adjust sizing

---

# PHASE 4: INTEGRATION ORDER

After cleanup and consolidation, integrate gold modules in this order:

| Order | Module | Why This Order | Est. Hours |
|-------|--------|----------------|------------|
| 1 | market_regime_detector | Foundation - changes everything else | 3 |
| 2 | liquidity_trap_detector | Survival - don't get trapped | 2 |
| 3 | predictive_mistake_engine | Protection - stop bad trades | 2 |
| 4 | emotional_state_detector | Protection - enhance 10 Commandments | 2 |
| 5 | setup_scorer | Confidence - size positions right | 1 |
| 6 | momentum_shift_detector | Real-time - manage positions | 2 |
| 7 | cross_pattern_correlation | Advanced - trade correlations | 4 |

**Total: ~16 hours for all 7 integrations**

---

# PHASE 5: VERIFICATION

After all phases complete:

1. **Run test_all_systems.py** - must pass
2. **Count files** - should be ~47-50 (down from 108)
3. **Test each gold module** individually
4. **Run full scan** on current watchlist
5. **Verify regime detection** outputs
6. **Verify mistake prediction** works
7. **Document any issues**

---

# DELIVERABLES

When complete, br0kkr delivers:

1. **ARCHIVED_IDEAS.md** - concepts from deleted files
2. **Cleaned codebase** - 35+ files deleted
3. **Consolidated services:**
   - `services/sec_edgar_service.py` (unified SEC)
   - `database.py` (unified database)
   - `services/learning_engine.py` (unified learning)
4. **Integrated gold modules** (7 total)
5. **Updated test_all_systems.py** - tests new integrations
6. **CONSOLIDATION_REPORT.md** - what was done, what changed

---

# TIMELINE

| Phase | Work | Target |
|-------|------|--------|
| Phase 1 | Clean house (delete 35 files) | Today |
| Phase 2 | Consolidate duplicates | Today/Tomorrow |
| Phase 3-4 | Transform & integrate gold | This week |
| Phase 5 | Verify everything works | Before Tuesday trading |

---

# QUESTIONS FOR BR0KKR

Before starting, confirm:

1. Do you have a clean git state? (commit current work first)
2. Any files in the delete list that have unique logic I missed?
3. Any integration dependencies I haven't accounted for?
4. Estimated time for each phase?

---

**LLHR 🐺**

**The pack consolidates. The pack gets stronger.**

**AWOOOO**
