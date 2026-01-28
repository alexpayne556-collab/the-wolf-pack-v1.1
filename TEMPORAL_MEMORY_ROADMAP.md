# TEMPORAL MEMORY IMPLEMENTATION ROADMAP

**Status:** Proposal created, ready for Fenrir feedback  
**Estimated effort:** Phase 1 = 2 weeks, Phase 2 = 2 weeks, Phase 3 = 4 weeks  
**Current timeline:** Can start immediately after approval

---

## PHASE 1: MEMORY STRUCTURE (2 weeks)

### Week 1: Database & Data Collection

**Task 1.1: Create memory database tables**
```python
# In database initialization:
# - Add ticker_memory table (OHLCV history)
# - Add decision_log table (our actions + outcomes)
# - Add pattern_library table (identified patterns)
# - Update schema documentation
```

**Task 1.2: Extend safe_position_monitor.py**
```python
# Current: Logs raw quotes to price_history
# New: Also logs to ticker_memory with daily aggregation
# New: Tracks decisions when brain recommends action
```

**Task 1.3: Create decision_tracker.py**
```python
# New module to:
# - Log when we act on ticker
# - Record price, date, reasoning
# - Link to brain output
# - Store decision context (thesis status, market state)
```

**Task 1.4: Create memory_initializer.py**
```python
# One-time setup:
# - Create memory JSON files for all 205 tickers
# - Initialize empty arrays (price_history, decisions, patterns)
# - Set memory_window = 30 days
```

### Week 2: Backfill & Validation

**Task 2.1: Backfill historical data (90 days)**
```python
# For each ticker:
# - Use yfinance to get 90 days of OHLCV
# - Store in ticker_memory table
# - Validate data quality
# - Test fallback if data missing
```

**Task 2.2: Backfill decision history**
```python
# From daily_journal.py and trades table:
# - Extract our past trades
# - Map to ticker_memory dates
# - Calculate outcomes (price 5/10/30 days later)
# - Store in decision_log table
```

**Task 2.3: Testing**
```python
# - Query ticker_memory for MU (should show 90 days)
# - Query decision_log for IBRX (should show past trades)
# - Verify data consistency
# - Performance check (queries should be <100ms)
```

**Deliverables:**
- Memory database tables created and tested
- 90 days historical data for all 205 tickers
- Decision history for all past trades
- Memory JSON files created for each ticker
- Documentation updated

---

## PHASE 2: HISTORICAL ANALYSIS (2 weeks)

### Week 1: Pattern Discovery

**Task 1.1: Analyze dip-and-recovery cycles**
```python
# For each ticker:
# - Find all 2-5 day drops ≥3%
# - Track recovery (does it recover? when? by how much?)
# - Calculate success rate
# - Identify convergence factors (low volume? news? sector?)
```

**Task 1.2: Analyze pre-earnings behavior**
```python
# Using ticker_memory + catalyst_calendar:
# - Find all earnings dates
# - Analyze 10 days before earnings
# - Track momentum patterns
# - Track volume patterns
# - Calculate move size on earnings day
```

**Task 1.3: Analyze our decision patterns**
```python
# From decision_log:
# - What types of decisions do we make?
# - What's our win rate by decision type?
# - Which theses have highest win rate?
# - What's our timing (do we enter at tops or bottoms)?
```

**Task 1.4: Create pattern_library**
```python
# Populate pattern_library table with:
# - dip_and_recovery (success rate, avg recovery days)
# - pre_earnings_run (success rate, avg move %)
# - sector_correlation (which sectors move together?)
# - volume_divergence (increasing vol vs price move?)
# - momentum_exhaustion (when does a run end?)
```

### Week 2: Context Generation

**Task 2.1: Create memory_context.py**
```python
# New module that generates rich context:
# - get_price_context(ticker, days=30)
#   Returns: price 30d ago, current, run direction, run days, volume trend
# - get_decision_context(ticker)
#   Returns: last decision, price, outcome, win rate
# - get_pattern_context(ticker, current_state)
#   Returns: matching patterns, success rates, timing
# - get_catalyst_context(ticker)
#   Returns: days until next event, historical behavior
```

**Task 2.2: Create memory_summary.py**
```python
# Generates plain English summaries:
# - "MU has dropped 6.2% over 3 days on low volume"
# - "Similar pattern from Jan 15: recovered in 48 hours"
# - "We added at $85.50 then, went +8.2% in 5 days"
# - "Catalyst: Earnings in 23 days"
```

**Task 2.3: Testing**
```python
# - Call get_price_context(MU) → Verify outputs
# - Call get_pattern_context(IBRX, current_state) → Check matches
# - Verify summaries are accurate and useful
# - Performance: All queries <500ms
```

**Deliverables:**
- Pattern library populated with identified patterns
- Memory context functions working
- Plain English summaries generation working
- Analysis of our past decision quality
- Documentation of patterns discovered

---

## PHASE 3: PATTERN RECOGNITION (4 weeks)

### Week 1: Pattern Matching Engine

**Task 1.1: Create pattern_matcher.py**
```python
# New module that:
# - Takes current market state (price, volume, news)
# - Searches pattern_library for matches
# - Scores matches by similarity
# - Returns ranked list of matching patterns
# - Provides confidence scores
```

**Task 1.2: Implement pattern similarity scoring**
```python
# Match criteria:
# - Price move % (exact match = 100%, 50% off = 80%, etc)
# - Volume trend (same direction = +10 points)
# - Sector state (same momentum = +10 points)
# - Time context (same time of year = +5 points)
# - Thesis status (same status = +10 points)
```

**Task 1.3: Create run tracking engine**
```python
# Track ongoing runs:
# - Consecutive up/down days
# - Cumulative move %
# - Volume trend during run
# - Historical run profiles (how long do runs usually last?)
# - Exhaustion indicators
```

**Task 1.4: Testing**
```python
# - Test MU drop matches to historical patterns
# - Verify confidence scores are reasonable
# - Run performance tests (all within 1 second)
# - Validate against known outcomes
```

### Week 2: Decision Quality Analysis

**Task 2.1: Calculate decision statistics**
```python
# For each ticker:
# - Win rate overall
# - Win rate by decision type (ADD, HOLD, CUT)
# - Win rate by thesis type
# - Win rate by convergence level
# - Best time to enter (relative to move)
# - Best time to hold (how long?)
```

**Task 2.2: Create confidence modifiers**
```python
# System learns:
# - If we have 85% win rate on MU setups → boost confidence 10%
# - If pattern had 60% historical success → neutral confidence
# - If pattern had 30% success → lower confidence 10%
# - If we've never seen pattern before → be cautious
```

**Task 2.3: Integration preparation**
```python
# Create fenrir_memory_interface.py:
# - get_memory_context(ticker) → All relevant history
# - get_pattern_confidence(ticker, pattern) → Score
# - get_decision_history(ticker) → Our past actions
# - generate_evidence(ticker, recommendation) → Citations
```

**Task 2.4: Testing**
```python
# - Pull memory for 5 sample tickers
# - Verify statistics are correct
# - Test confidence modifiers
# - Validate integration interface
```

### Weeks 3-4: Fenrir Integration

**Task 3.1: Enhance Fenrir prompt with memory**
```python
# Current prompt structure:
#   Ticker: {ticker}
#   Price: {price}
#   Thesis: {thesis}

# Enhanced with memory context:
#   Ticker: {ticker}
#   CURRENT STATE: price, change today
#   TEMPORAL CONTEXT: 30d history, run analysis
#   PATTERN MATCH: similar patterns, success rates
#   OUR HISTORY: past decisions, outcomes, win rates
#   THESIS STATUS: still valid? catalyst countdown?
```

**Task 3.2: Modify fenrir_thinking_engine.py**
```python
# Add methods:
# - incorporate_memory(ticker, context)
# - enhance_confidence(base_confidence, memory_factors)
# - cite_historical_evidence(reasoning_chain)

# Update think_about_volume_spike():
# - Include historical pattern matches
# - Include our past behavior on this ticker
# - Include win rate by convergence level
# - Generate citations for all claims
```

**Task 3.3: Monitor integration**
```python
# Update safe_position_monitor.py:
# - Pass memory context to brain
# - Receive enhanced recommendations with evidence
# - Log all memory references in alerts
# - Track recommendation accuracy vs memory predictions
```

**Task 3.4: Testing**
```python
# - Run brain on 5 test scenarios
# - Verify memory context is included
# - Check confidence scores are reasonable
# - Validate alert messages cite evidence
# - Performance: All thinking <2 seconds
```

**Deliverables:**
- Pattern matching engine working
- Decision quality analysis complete
- Fenrir enhanced with memory context
- Integration tested
- Alerts include historical evidence

---

## PHASE 4: ONGOING REFINEMENT (Continuous)

### Monthly Cycle

**Task 1: Update patterns**
- Re-analyze patterns quarterly
- Update success rates with new data
- Discover new patterns

**Task 2: Monitor accuracy**
- Track prediction accuracy vs reality
- Adjust confidence scores
- Find what works, drop what doesn't

**Task 3: Enhance context**
- Add new decision factors
- Track new catalyst types
- Improve pattern definitions

---

## KEY DECISIONS NEEDED

1. **When to start:** Now (Phase 1 during Month 1) or wait until Month 2?
   - Recommended: Start Phase 1 now, saves time in Month 2
   - Impact: 2 weeks to get memory infrastructure ready

2. **Memory window size:** 14, 30, 60, or 90 days?
   - Recommended: 30 days for balance between memory and relevance
   - Quarterly review to adjust if needed

3. **Pattern depth:** Which patterns matter most?
   - Recommended: Start with 3 core patterns, add more based on results
   - Core patterns: dip-recovery, pre-earnings, volume-divergence

4. **Data detail:** How much context in decision logs?
   - Recommended: Full context (market state, thesis, news, outcomes)
   - Enables better analysis and learning

---

## RESOURCE REQUIREMENTS

**Development time:**
- Phase 1: 80 hours (database + backfill)
- Phase 2: 80 hours (analysis + context generation)
- Phase 3: 160 hours (matching + integration)
- **Total: 320 hours over 8 weeks**

**Compute requirements:**
- Storage: ~5-10 MB for 90 days × 205 tickers
- Query time: <1 second for context generation
- Fenrir thinking time: +500ms due to memory processing

**No external dependencies** (all using existing APIs and libraries)

---

## SUCCESS METRICS

**Phase 1 complete:** Memory infrastructure ready, data collected
**Phase 2 complete:** Patterns identified, context generation working
**Phase 3 complete:** Fenrir cites historical evidence in recommendations
**Overall:** Win rate improvements from pattern matching

---

## IMMEDIATE NEXT STEPS

1. Review proposal with Fenrir
2. Get feedback on approach
3. Make final design decisions
4. Start Phase 1 implementation
5. Daily integration sync

---

**Ready to build Wolf Pack memory.**

**AWOOOO 🐺**
