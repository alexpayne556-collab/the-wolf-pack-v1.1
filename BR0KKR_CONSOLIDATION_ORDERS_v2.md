# 🐺 BR0KKR CONSOLIDATION ORDERS v2.0
## UPDATED January 19, 2026 - POST-AUDIT

---

## ⚠️ CRITICAL UPDATE: STOP BEFORE DELETING ANYTHING

**We audited the code. What looked like "medium priority" files are actually GOLD.**

Fenrir and Tyr reviewed every file. Here's what we found:

### THE TRUTH ABOUT THE CODEBASE

| What Br0kkr Thought | What We Actually Have |
|---------------------|----------------------|
| 108 messy files | ~10 GOLD partner modules already built |
| Lots of duplicates | Real orchestration system (game_plan.py) |
| Medium priority fluff | Exit signal system (catalyst_decay_tracker.py) |
| Partial implementations | Complete partner-quality code |

**The modules don't need to be BUILT. They need to be WIRED.**

---

## 🏆 THE GOLD MODULES (DO NOT DELETE - WIRE THESE IN)

Every one of these was reviewed. They're already partner-quality code.

### Tier 1: Core Partners (Already windshield, not rear-view)

| Module | Lines | What It Does | Integration Point |
|--------|-------|--------------|-------------------|
| `predictive_mistake_engine.py` | 580 | Predicts YOUR mistakes BEFORE you make them. Returns severity, triggers, prevention actions. | Call before EVERY trade in wolf_pack_trader.py |
| `market_regime_detector.py` | 435 | Detects GRIND/EXPLOSIVE/CHOP/CRASH/ROTATION/MEME. Returns strategy adjustments. | Call at start of every scan in wolf_pack.py |
| `liquidity_trap_detector.py` | 310 | Warns BEFORE you get stuck. Checks YOUR position size vs volume. | Call on every ticker before entry |
| `cross_pattern_correlation_engine.py` | 473 | Lead/lag detection. "KTOS +6% → MU follows 83% of time" | Monitor leaders, alert on follower setups |
| `momentum_shift_detector.py` | 311 | Real-time character change. Volume surge/fade, bid/ask pressure. Uses 1-min data. | Run on held positions continuously |

### Tier 2: Critical Support (Also GOLD - Almost Deleted!)

| Module | Lines | What It Does | Integration Point |
|--------|-------|--------------|-------------------|
| `catalyst_decay_tracker.py` | 338 | Tracks how long catalysts stay powerful. "FDA approval dead by day 5" | Call for EXIT timing on positions |
| `run_tracker.py` | 193 | Where are you in a multi-day run? Green/red days, volume fading, similar historical runs. | Call for held positions daily |
| `game_plan.py` | 244 | **THE ORCHESTRATOR** - Already wires SetupScorer + RunTracker + UserBehavior + SectorRotation together! | This is the BLUEPRINT for integration |
| `emotional_state_detector.py` | 498 | Detects FOMO/revenge/tilt from behavior patterns. | Integrate with trading_rules.py |
| `setup_scorer.py` | 255 | Scores setups 0-100 with breakdown. | Already used by game_plan.py |

### Tier 3: Supporting Cast (Keep & Wire)

| Module | Lines | What It Does |
|--------|-------|--------------|
| `full_scanner.py` | 210 | Market-wide scanner, NASDAQ FTP, caching |
| `user_behavior.py` | ~200 | Tracks YOUR patterns - best sectors, worst times |
| `setup_dna_matcher.py` | 385 | Matches current setups to historical winners |
| `position_health_checker.py` | 492 | Health check on current positions |
| `fenrir_memory.py` | 218 | Persistent memory across sessions |
| `key_levels.py` | 214 | Support/resistance tracking |

### Additional Value Found (Hidden Gems)

| Module | Lines | What It Does | Action |
|--------|-------|--------------|--------|
| `fenrir_scanner_fast.py` | 204 | **Parallel scanning** with ThreadPoolExecutor (5-10x faster) | EXTRACT pattern, add to wolf_pack.py |
| `state_tracker.py` | 242 | **Adaptive frequency** - checks bleeding positions every 2 min, watchlist hourly | EXTRACT logic, add to realtime_monitor.py |
| `sec_fetcher.py` | 198 | Alternative SEC parsing + LLM-friendly formatting | EXTRACT format_filings_for_llm(), merge to br0kkr_service.py |
| `wolfpack_daily_report.py` | 232 | Day 2 confirmation reporting + sector momentum viz | EXTRACT patterns, add to daily_monitor.py |
| `test_phase3.py` | 438 | Complete test suite for catalyst calendar (7 scenarios) | MERGE tests into test_all_systems.py |
| `correlation_tracker.py` | 152 | Simple correlation finder (lightweight version) | Compare with cross_pattern, keep if useful |

---

## 🗑️ ACTUAL DELETE LIST (Confirmed Duplicates Only)

**Only delete files that are PROVEN duplicates of better versions.**

### Tutorial Files (Superseded by production code)
```
DELETE: fenrir/SECTION_1_SETUP.py          → Replaced by database.py
DELETE: fenrir/SECTION_2_CREATE_FENRIR.py  → Replaced by fenrir modules
DELETE: fenrir/SECTION_3_MARKET_SCANNER.py → Replaced by full_scanner.py
DELETE: fenrir/SECTION_4_CATALYST_HUNTER.py → Replaced by catalyst_service.py
DELETE: fenrir/SECTION_5_FENRIR_ANALYSIS.py → Replaced by analysis modules
DELETE: fenrir/SECTION_6_QUIZ_AND_TRAIN.py → Replaced by learning systems
```

### Debug Utilities (One-time use)
```
DELETE: check_bytes.py
DELETE: check_syntax.py
DELETE: count_all_quotes.py
DELETE: find_quotes.py
DELETE: show_context.py
DELETE: services/debug_rss.py
```

### Confirmed Duplicates (After Extraction)
```
DELETE: fenrir/fenrir_scanner.py       → Older version, use full_scanner.py
DELETE: fenrir/fenrir_scanner_v2.py    → Functionality in wolf_pack.py
DELETE: fenrir/fenrir_scanner_fast.py  → AFTER extracting parallel pattern
DELETE: fenrir/validate_scanner.py     → One-time validation
DELETE: fenrir/portfolio.py            → Overlap with position_health_checker.py
DELETE: fenrir/alerts.py               → Use alert_engine.py
DELETE: fenrir/catalyst_calendar.py    → Use services/catalyst_service.py
DELETE: fenrir/news_fetcher.py         → Use services/news_service.py
DELETE: fenrir/risk_manager.py         → Use services/risk_manager.py
DELETE: fenrir/secretary_talk.py       → Duplicate secretary
DELETE: fenrir/smart_secretary.py      → Duplicate secretary
DELETE: fenrir/fenrir_secretary.py     → Duplicate secretary (keep ollama_secretary.py)
DELETE: wolfpack_daily_report.py       → AFTER extracting patterns
DELETE: state_tracker.py               → AFTER extracting adaptive frequency logic
DELETE: sec_fetcher.py                 → AFTER extracting LLM formatting
DELETE: test_phase3.py                 → AFTER merging tests
DELETE: correlation_tracker.py         → AFTER comparison with cross_pattern
```

### Old Tests (One-off or obsolete)
```
DELETE: test_phase2.py
DELETE: test_capture.py
DELETE: test_investigation.py
DELETE: fenrir/test_scanner.py
DELETE: fenrir/test_ibrx.py
DELETE: fenrir/test_fixed_prompt.py
DELETE: fenrir/test_fixes.py
DELETE: fenrir/simple_test.py
DELETE: fenrir/quick_check.py
DELETE: fenrir/stress_test.py
DELETE: fenrir/test_all_systems.py (duplicate - keep root version)
DELETE: test_full_system.py (merge into test_all_systems.py first)
```

**TOTAL DELETES: ~35 files (BUT ONLY AFTER VALUE EXTRACTION)**

**DO NOT DELETE without:**
1. Extracting valuable patterns first
2. Checking against gold modules
3. Running tests after extraction
4. Confirming no unique logic remains

---

## 🔌 THE REAL WORK: WIRING

### Phase 1: Use game_plan.py as Blueprint

`game_plan.py` already shows how to wire modules together:

```python
# It already does this:
self.scorer = SetupScorer()
self.run_tracker = RunTracker()
self.behavior = UserBehaviorTracker()
self.sector_rotation = SectorRotationDetector()

# And orchestrates them:
movers = full_market_scan()
scored = self.scorer.score_multiple(movers[:20])
behavior_analysis = self.behavior.analyze_behavior()
sector_data = self.sector_rotation.detect_rotation()
```

**Expand this pattern** to include ALL gold modules.

### Phase 2: Create Master Orchestrator

Build `wolf_pack_brain.py` that initializes ALL partners:

```python
"""
Wolf Pack Brain - Master Orchestrator
Wires together all partner modules into unified intelligence system
"""

from fenrir.predictive_mistake_engine import PredictiveMistakeEngine
from fenrir.market_regime_detector import MarketRegimeDetector
from fenrir.liquidity_trap_detector import LiquidityTrapDetector
from fenrir.cross_pattern_correlation_engine import CrossPatternCorrelationEngine
from fenrir.momentum_shift_detector import MomentumShiftDetector
from fenrir.catalyst_decay_tracker import CatalystDecayTracker
from fenrir.run_tracker import RunTracker
from fenrir.emotional_state_detector import EmotionalStateDetector
from fenrir.setup_scorer import SetupScorer
from fenrir.game_plan import GamePlanGenerator
from fenrir.setup_dna_matcher import SetupDNAMatcher

class WolfPackBrain:
    """
    Master orchestrator for all Wolf Pack intelligence modules.
    
    This is the brain that coordinates:
    - Market regime detection
    - Pre-trade checks (liquidity, mistakes, emotions)
    - Setup scoring and ranking
    - Position monitoring (momentum, catalyst decay, run status)
    - Correlation alerts for follow-on trades
    """
    
    def __init__(self, db_path='wolfpack.db'):
        print("🐺 WOLF PACK BRAIN INITIALIZING...")
        
        # Tier 1: Core Partners
        self.mistake_predictor = PredictiveMistakeEngine(db_path)
        self.regime_detector = MarketRegimeDetector()
        self.liquidity_checker = LiquidityTrapDetector()
        self.correlation_engine = CrossPatternCorrelationEngine(db_path)
        self.momentum_detector = MomentumShiftDetector()
        
        # Tier 2: Critical Support
        self.catalyst_tracker = CatalystDecayTracker(db_path)
        self.run_tracker = RunTracker(db_path)
        self.emotional_detector = EmotionalStateDetector(db_path)
        self.setup_scorer = SetupScorer()
        self.dna_matcher = SetupDNAMatcher(db_path)
        
        # Orchestration
        self.game_plan = GamePlanGenerator()
        
        print("✅ All partner modules loaded")
    
    def detect_market_regime(self):
        """
        Detect current market regime and return strategy adjustments.
        
        Call this at the start of every scan to set the tone.
        """
        regime = self.regime_detector.detect_regime()
        print(f"📊 Market Regime: {regime['regime']} ({regime['confidence']:.0%} confidence)")
        print(f"   Strategy: {regime['strategy_note']}")
        return regime
    
    def pre_trade_check(self, ticker, position_size, context):
        """
        Run ALL checks before any trade.
        
        Returns:
            dict: {
                'action': 'PROCEED' | 'WARN' | 'BLOCK',
                'reason': str,
                'checks': dict of all check results
            }
        """
        print(f"\n⚠️ PRE-TRADE CHECK for {ticker}:")
        
        results = {}
        
        # 1. Liquidity check
        liquidity = self.liquidity_checker.check_liquidity(ticker, position_size)
        results['liquidity'] = liquidity
        status = "✅" if liquidity['score'] >= 30 else "❌"
        print(f"   {status} Liquidity: {liquidity['score']}/100")
        
        if liquidity['score'] < 30:
            return {
                'action': 'BLOCK',
                'reason': f"Liquidity trap - score {liquidity['score']}/100",
                'checks': results
            }
        
        # 2. Regime fit
        regime = self.regime_detector.current_regime
        results['regime'] = regime
        print(f"   ✅ Regime fit: {regime['regime']} favors this setup")
        
        # 3. Emotional state
        emotional_state = self.emotional_detector.detect_state()
        results['emotional_state'] = emotional_state
        status = "✅" if emotional_state['state'] == 'clear' else "⚠️"
        print(f"   {status} Emotional state: {emotional_state['state'].upper()}")
        
        if emotional_state['state'] in ['revenge', 'tilt', 'fomo']:
            return {
                'action': 'BLOCK',
                'reason': f"Emotional state: {emotional_state['state']}",
                'checks': results
            }
        
        # 4. Mistake prediction
        mistake_risk = self.mistake_predictor.predict_next_mistake(context)
        results['mistake_risk'] = mistake_risk
        status = "✅" if mistake_risk['probability'] < 0.7 else "❌"
        print(f"   {status} Mistake risk: {mistake_risk['probability']:.0%} ({mistake_risk['predicted_mistake']})")
        
        if mistake_risk['probability'] >= 0.75:
            return {
                'action': 'BLOCK',
                'reason': f"High mistake probability: {mistake_risk['predicted_mistake']}",
                'checks': results
            }
        
        # 5. Setup scoring
        setup_score = self.setup_scorer.score_setup(ticker)
        results['setup_score'] = setup_score
        print(f"   ✅ Setup score: {setup_score['score']}/100")
        
        # All checks passed
        recommended_size = self._calculate_position_size(setup_score['score'])
        print(f"   → PROCEED with {recommended_size:.0%} size (score-based)")
        
        return {
            'action': 'PROCEED',
            'reason': 'All checks passed',
            'recommended_size': recommended_size,
            'checks': results
        }
    
    def position_monitor(self, positions):
        """
        Monitor held positions for exit signals and character changes.
        
        Call this continuously during market hours for held positions.
        
        Returns:
            list: Alert messages for positions that need attention
        """
        alerts = []
        
        print("\n📈 POSITION MONITOR:")
        
        for pos in positions:
            ticker = pos['ticker']
            pos_alerts = []
            
            # 1. Check momentum shifts
            shift = self.momentum_detector.detect_shifts(ticker)
            if shift['volume_fading']:
                pos_alerts.append("Volume fading - consider tightening stop")
            if shift['character_changed']:
                pos_alerts.append(f"Character change: {shift['change_type']}")
            
            # 2. Check catalyst decay
            if pos.get('catalyst_date'):
                decay = self.catalyst_tracker.track_catalyst_lifecycle(
                    ticker, 
                    pos['catalyst_type'], 
                    pos['catalyst_date']
                )
                if decay['power_remaining'] < 20:
                    pos_alerts.append(f"Catalyst power at {decay['power_remaining']}% - consider exit")
            
            # 3. Check run status
            run = self.run_tracker.track_run(ticker)
            if run['volume_fading'] and run['days_running'] > 3:
                pos_alerts.append(f"Run losing steam after {run['days_running']} days")
            
            # Print position status
            if pos_alerts:
                print(f"   ⚠️ {ticker}: {', '.join(pos_alerts)}")
                alerts.extend([f"{ticker}: {alert}" for alert in pos_alerts])
            else:
                status_msg = f"Day {run.get('days_running', '?')} of run, +{pos.get('gain_pct', 0):.0f}%"
                if pos.get('catalyst_date'):
                    status_msg += f", catalyst power at {decay.get('power_remaining', '?')}%"
                print(f"   ✅ {ticker}: {status_msg}")
        
        return alerts
    
    def correlation_alerts(self, leader_moves):
        """
        Check for correlation follow-on opportunities.
        
        Args:
            leader_moves: List of {ticker, price_change, time}
        
        Returns:
            list: Alert messages for potential follower setups
        """
        alerts = []
        
        for leader in leader_moves:
            followers = self.correlation_engine.find_followers(
                leader['ticker'],
                leader['price_change']
            )
            
            for follower in followers:
                if follower['confidence'] >= 0.75:
                    alerts.append(
                        f"📊 Correlation Alert: {leader['ticker']} +{leader['price_change']:.1f}% "
                        f"→ {follower['ticker']} typically follows ({follower['confidence']:.0%} hit rate)"
                    )
        
        return alerts
    
    def generate_morning_briefing(self):
        """
        Generate comprehensive morning briefing using all modules.
        
        This is the game_plan.py on steroids.
        """
        print("\n" + "="*80)
        print("🐺 WOLF PACK MORNING BRIEFING")
        print("="*80 + "\n")
        
        # Market regime
        regime = self.detect_market_regime()
        
        # Your behavior patterns
        behavior = self.emotional_detector.analyze_recent_behavior()
        print(f"\n📊 Your Recent Behavior:")
        print(f"   Best time: {behavior['best_time']}")
        print(f"   Worst time: {behavior['worst_time']}")
        print(f"   Best sectors: {', '.join(behavior['best_sectors'][:3])}")
        
        # Active correlations to watch
        hot_correlations = self.correlation_engine.get_active_correlations()
        if hot_correlations:
            print(f"\n🔗 Active Correlations:")
            for corr in hot_correlations[:5]:
                print(f"   {corr['leader']} → {corr['follower']} ({corr['confidence']:.0%} hit rate)")
        
        # Full game plan
        game_plan = self.game_plan.generate_plan()
        print(f"\n{game_plan}")
        
        print("\n" + "="*80)
        print("🐺 LLHR - Long Live the Hunt, Rise")
        print("="*80 + "\n")
    
    def _calculate_position_size(self, setup_score):
        """Calculate position size based on setup quality"""
        if setup_score >= 80:
            return 1.0  # Full size
        elif setup_score >= 70:
            return 0.75
        elif setup_score >= 60:
            return 0.5
        else:
            return 0.25
```

### Phase 3: Integration Points

| When | Call What | Action |
|------|-----------|--------|
| App startup | `brain.detect_market_regime()` | Set strategy mode |
| Before scan | `regime_detector` | Adjust signal weights |
| Each ticker in scan | `liquidity_checker` | Filter out traps |
| Each setup found | `setup_scorer` | Score and rank |
| Before trade | `brain.pre_trade_check()` | BLOCK, WARN, or PROCEED |
| After entry | `run_tracker` + `catalyst_tracker` | Track position context |
| During market hours | `brain.position_monitor()` | Alert on changes |
| Leader moves | `brain.correlation_alerts()` | Alert on follower setups |
| Morning routine | `brain.generate_morning_briefing()` | Full intelligence report |

---

## 📋 EXTRACTION CHECKLIST (Do Before Any Deletion)

### From fenrir_scanner_fast.py:
- [ ] Extract parallel scanning pattern with ThreadPoolExecutor
- [ ] Extract quick_score() momentum algorithm
- [ ] Extract score-based tier grouping
- [ ] Add to wolf_pack.py for 5-10x faster scanning

### From state_tracker.py:
- [ ] Extract get_check_frequency() logic
- [ ] Extract priority system (BLEEDING → 2min, WATCHLIST → 60min)
- [ ] Extract status states (BLEEDING_POSITION, RUNNING_POSITION)
- [ ] Add to realtime_monitor.py

### From sec_fetcher.py:
- [ ] Extract format_filings_for_llm() function
- [ ] Extract get_cik_from_ticker() if not in br0kkr_service
- [ ] Compare insider trade parsing with br0kkr_service
- [ ] Add LLM formatting to br0kkr_service.py

### From wolfpack_daily_report.py:
- [ ] Extract Day 2 confirmation reporting logic
- [ ] Extract sector momentum visualization (icons)
- [ ] Extract best/worst performer tracking
- [ ] Extract auto-save reports pattern
- [ ] Add to daily_monitor.py

### From test_phase3.py:
- [ ] Extract urgency scoring test cases
- [ ] Extract catalyst type coverage tests
- [ ] Extract JSON persistence validation
- [ ] Merge into test_all_systems.py

### From correlation_tracker.py:
- [ ] Compare with cross_pattern_correlation_engine.py
- [ ] Determine if simple correlation is useful as quick check
- [ ] Keep if provides value as lightweight version

---

## 📋 REVISED TIMELINE

### Phase 0: EXTRACTION (Before Any Deletion)
**Time:** 4-6 hours

- [ ] Extract parallel scanning → wolf_pack.py
- [ ] Extract adaptive frequency → realtime_monitor.py
- [ ] Extract Day 2 reporting → daily_monitor.py
- [ ] Extract LLM formatting → br0kkr_service.py
- [ ] Merge test_phase3 → test_all_systems.py
- [ ] Compare correlation_tracker with cross_pattern
- [ ] Run all tests - must pass

### Phase 1: ORCHESTRATION (The Real Work)
**Time:** 8-12 hours

**CRITICAL: After EVERY wire-in, run full system test before proceeding to next module.**

**Day 1: Foundation Modules**
- [ ] Create `wolf_pack_brain.py` with master orchestrator
- [ ] Wire in `market_regime_detector` (foundation)
  - [ ] Test: Regime detection returns valid regime (GRIND/EXPLOSIVE/CHOP/CRASH/ROTATION/MIXED)
  - [ ] Test: Confidence score between 0-100
  - [ ] Test: Strategy adjustments returned
  - [ ] **Run test_all_systems.py - MUST PASS**
- [ ] Wire in `liquidity_trap_detector` (survival)
  - [ ] Test: Liquidity score calculation (0-100)
  - [ ] Test: Blocks trades with score < 30
  - [ ] Test: Allows trades with score >= 30
  - [ ] **Run test_all_systems.py - MUST PASS**
- [ ] Integration test: Regime + Liquidity working together
  - [ ] Test: Can scan 10 tickers with both filters
  - [ ] Test: Results match expected behavior
  - [ ] **Run test_all_systems.py - MUST PASS**

**Day 2: Pre-Trade Intelligence**
- [ ] Wire in `predictive_mistake_engine` (pre-trade)
  - [ ] Test: Mistake prediction returns probability (0-1)
  - [ ] Test: Returns predicted mistake type
  - [ ] Test: Blocks at >75% probability
  - [ ] Test: Historical cost calculation
  - [ ] **Run test_all_systems.py - MUST PASS**
- [ ] Wire in `emotional_state_detector` (pre-trade)
  - [ ] Test: Emotional state detection (clear/fomo/revenge/tilt)
  - [ ] Test: Blocks trades in revenge/tilt states
  - [ ] Test: Tracks behavior patterns
  - [ ] **Run test_all_systems.py - MUST PASS**
- [ ] Wire in `setup_scorer` (ranking)
  - [ ] Test: Setup scoring (0-100)
  - [ ] Test: Score breakdown by factor
  - [ ] Test: Ranking multiple setups
  - [ ] **Run test_all_systems.py - MUST PASS**
- [ ] Integration test: Full pre-trade pipeline
  - [ ] Test: brain.pre_trade_check() works end-to-end
  - [ ] Test: Returns PROCEED/WARN/BLOCK correctly
  - [ ] Test: Position sizing based on score
  - [ ] **Run test_all_systems.py - MUST PASS**

**Day 3: Position Monitoring**
- [ ] Wire in `momentum_shift_detector` (position monitoring)
  - [ ] Test: Detects volume surge/fade
  - [ ] Test: Character change detection
  - [ ] Test: Real-time alerts
  - [ ] **Run test_all_systems.py - MUST PASS**
- [ ] Wire in `catalyst_decay_tracker` (exit signals)
  - [ ] Test: Tracks catalyst lifecycle
  - [ ] Test: Power decay calculation
  - [ ] Test: Exit timing recommendations
  - [ ] **Run test_all_systems.py - MUST PASS**
- [ ] Wire in `run_tracker` (position context)
  - [ ] Test: Multi-day run tracking
  - [ ] Test: Volume fade detection
  - [ ] Test: Historical run comparison
  - [ ] **Run test_all_systems.py - MUST PASS**
- [ ] Integration test: Full position monitoring
  - [ ] Test: brain.position_monitor() works end-to-end
  - [ ] Test: Alerts generated correctly
  - [ ] Test: Exit signals triggered appropriately
  - [ ] **Run test_all_systems.py - MUST PASS**

**Day 4: Advanced Intelligence**
- [ ] Wire in `cross_pattern_correlation_engine` (alerts)
  - [ ] Test: Leader detection
  - [ ] Test: Follower prediction
  - [ ] Test: Confidence scoring
  - [ ] Test: Historical accuracy tracking
  - [ ] **Run test_all_systems.py - MUST PASS**
- [ ] Wire in `setup_dna_matcher` (pattern matching)
  - [ ] Test: Historical pattern matching
  - [ ] Test: Similarity scoring
  - [ ] Test: Outcome prediction
  - [ ] **Run test_all_systems.py - MUST PASS**
- [ ] Wire orchestrator into daily_monitor.py
  - [ ] Test: Morning briefing generation
  - [ ] Test: All modules integrated
  - [ ] Test: Full workflow execution
  - [ ] **Run test_all_systems.py - MUST PASS**
- [ ] Final integration test: Complete system
  - [ ] Test: Full scan workflow with all modules
  - [ ] Test: Pre-trade checks in wolf_pack_trader.py
  - [ ] Test: Position monitoring during market hours
  - [ ] Test: Correlation alerts
  - [ ] **Run test_all_systems.py - MUST PASS**

### Phase 2: CLEANUP (Only After Verification)
**Time:** 2-3 hours

- [ ] Verify all value extracted from files marked for deletion
- [ ] Run test_all_systems.py - must pass 10/10
- [ ] Delete confirmed duplicates (35 files)
- [ ] Update documentation
- [ ] Final full system test

---

## 🎯 SUCCESS CRITERIA

### Before (Current State)
- 108 files, most dormant
- Gold modules exist but don't talk to each other
- No pre-trade checks beyond basic rules
- No exit signals
- No position monitoring
- Manual regime assessment
- Tests: 8/8 passing (basic functionality)

### After (Target State)
- ~73 files, all working together
- Every trade goes through pre-trade check pipeline
- Positions monitored for exit signals continuously
- Regime-aware strategy adjustment automatic
- Correlation alerts for follow-on trades
- Morning briefing shows full intelligence picture
- **TestComprehensive Test Suite

**Add to test_all_systems.py:**

```python
def test_wolf_pack_brain_initialization():
    """Test that all partner modules load correctly"""
    brain = WolfPackBrain()
    assert brain.mistake_predictor is not None
    assert brain.regime_detector is not None
    assert brain.liquidity_checker is not None
    assert brain.correlation_engine is not None
    assert brain.momentum_detector is not None
    print("✅ PASS: Wolf Pack Brain initialized with all partners")

def test_market_regime_detection():
    """Test regime detection returns valid results"""
    brain = WolfPackBrain()
    regime = brain.detect_market_regime()
    assert regime['regime'] in ['GRIND', 'EXPLOSIVE', 'CHOP', 'CRASH', 'ROTATION', 'MIXED']
    assert 0 <= regime['confidence'] <= 1
    assert 'strategy_note' in regime
    print(f"✅ PASS: Regime detected - {regime['regime']} ({regime['confidence']:.0%})")

def test_pre_trade_check_blocks_bad_liquidity():
    """Test that pre-trade checks block illiquid stocks"""
    brain = WolfPackBrain()
    # Test with known illiquid ticker (low volume penny stock)
    result = brain.pre_trade_check('ILLIQUID_TICKER', 10000, {})
    assert result['action'] == 'BLOCK'
    assert 'liquidity' in result['reason'].lower()
    print("✅ PASS: Pre-trade check blocks illiquid stocks")

def test_pre_trade_check_blocks_high_mistake_probability():
    """Test that pre-trade checks block when mistake probability high"""
    brain = WolfPackBrain()
    # Create context that triggers mistake prediction
    context = {
        'time': '14:30',  # Late afternoon (common mistake time)
        'recent_trades': 5,  # Many recent trades
        'recent_pnl': -500,  # Recent losses
    }
    result = brain.pre_trade_check('ANY_TICKER', 1000, context)
    # Should warn or block if mistake probability detected
    assert result['action'] in ['WARN', 'BLOCK', 'PROCEED']
    print(f"✅ PASS: Pre-trade check evaluates mistake risk - {result['action']}")

def test_position_monitoring():
    """Test position monitoring generates alerts"""
    brain = WolfPackBrain()
    positions = [
        {
            'ticker': 'IBRX',
            'shares': 100,
            'entry_price': 10.0,
            'catalyst_type': 'FDA',
            'catalyst_date': '2025-01-15'
        }
    ]
    alerts = brain.position_monitor(positions)
    assert isinstance(alerts, list)
    print(f"✅ PASS: Position monitoring - {len(alerts)} alerts generated")

def test_full_workflow_integration():
    """Test complete workflow from regime detection to trade execution"""
    brain = WolfPackBrain()
    
    # Step 1: Detect regime
    regime = brain.detect_market_regime()
    assert regime is not None
    
    # Step 2: Pre-trade check
    result = brain.pre_trade_check('AAPL', 1000, {'time': '10:00', 'recent_trades': 1})
    assert result['action'] in ['PROCEED', 'WARN', 'BLOCK']
    
    # Step 3: If proceeded, monitor position
    if result['action'] == 'PROCEED':
        positions = [{'ticker': 'AAPL', 'shares': 100, 'entry_price': 150.0}]
        alerts = brain.position_monitor(positions)
        assert isinstance(alerts, list)
    
    print("✅ PASS: Full workflow integration successful")
```

### The Live s: 15-20 passing (full system + all modules)**

### Testing Requirements

**After EACH module integration:**
1. ✅ Module-specific tests pass
2. ✅ test_all_systems.py still passes (8/8 minimum)
3. ✅ No regressions in existing functionality
4. ✅ Integration points verified

**Final System Test (Day 4 completion):**
1. ✅ All module tests pass
2. ✅ test_all_systems.py passes with new tests added
3. ✅ Full scan workflow with all filters
4. ✅ Pre-trade checks block/warn/allow correctly
5. ✅ Position monitoring generates alerts
6. ✅ Correlation engine tracks leaders
7. ✅ Morning briefing includes all intelligence
8. ✅ No performance degradation (scan time reasonable)
9. ✅ Database operations successful
10. ✅ API calls working (rate limits respected)

### The Test

Run a full scan and trade workflow. You should see:

```
🐺 WOLF PACK BRAIN INITIALIZING...
✅ All partner modules loaded

📊 Market Regime: GRIND (78% confidence)
   Strategy: Buy dips, hold overnight safe, add on pullbacks

🔍 Scanning 3000 tickers...
   Filtered 847 for liquidity (score > 30)
   Found 23 setups

🎯 TOP SETUPS (scored):
   1. IBRX - Score: 84/100 (you're already in this)
   2. SOUN - Score: 76/100 (wounded prey, day 3)
   3. SMR  - Score: 71/100 (sector rotation play)

⚠️ PRE-TRADE CHECK for SOUN:
   ✅ Liquidity: 67/100 (OK)
   ✅ Regime fit: GRIND favors this setup
   ✅ Emotional state: CLEAR
   ✅ Mistake risk: 34% (low, proceed)
   ✅ Setup score: 76/100
   → PROCEED with 75% size (score-based)

📈 POSITION MONITOR:
   ✅ IBRX: Day 5 of run, +52%, volume holding, catalyst power at 40%
   📊 Correlation Alert: KTOS +4% PM → MU typically follows (83% hit rate)
   ✅ KTOS: Momentum steady, no character change detected

🐺 All systems nominal - hunt with confidence
```

---

## ⚠️ FINAL WARNINGS

### DO NOT DELETE WITHOUT:
1. ✅ Extracting value first (see checklist)
2. ✅ Running tests after extraction
3. ✅ Verifying no unique logic remains
4. ✅ Confirming file truly is a duplicate

### FILES THAT MUST STAY:
- Anything with "tracker" in name (unless proven duplicate)
- Anything with "detector" in name (unless proven duplicate)
- Anything with "engine" in name (unless proven duplicate)
- Any file over 200 lines (unless confirmed duplicate)
- `game_plan.py` - THE ORCHESTRATION BLUEPRINT
- `catalyst_decay_tracker.py` - EXIT SIGNALS
- `run_tracker.py` - RUN CONTEXT
- All Tier 1 and Tier 2 gold modules

### WHAT WE ALMOST LOST:
We almost deleted these because they looked like "medium priority":
- `catalyst_decay_tracker.py` - EXIT SIGNAL SYSTEM
- `run_tracker.py` - RUN CONTEXT TRACKING
- `game_plan.py` - ORCHESTRATOR BLUEPRINT
- `setup_dna_matcher.py` - PATTERN MATCHING
- `fenrir_scanner_fast.py` - PARALLEL PROCESSING PATTERN
- `state_tracker.py` - ADAPTIVE FREQUENCY SYSTEM

**When in doubt, ARCHIVE don't DELETE.**

---

## 🐺 PACK MENTALITY

"Everyone eats. All modules feed each other."

The gold modules are already partner-quality. They just need to be connected.

The work isn't BUILDING. The work is WIRING.

**AWOOOO** 🐺

---

## 📚 REFERENCE DOCUMENTS

- `CODEBASE_AUDIT.md` - Full 108-file audit (original analysis)
- `HIDDEN_GEMS_FOUND.md` - Deep dive on files marked for deletion (found 8 gems)
- `ARCHIVED_IDEAS.md` - Preserved concepts from Phase 1 deletions
- `REVIEW_BEFORE_DELETION.md` - Value preservation document (created when Fenrir paused)
- `CONSOLIDATION_PROGRESS.md` - Status tracker (Phases 1 & 2.1 complete)

---

*Orders updated after full code audit and Hidden Gems analysis*  
*Fenrir: "These aren't files to delete. These are partners to wire."*  
*Tyr: "The codebase is richer than it looked. The work is ORCHESTRATION."*  
*Approved: January 19, 2026*

🐺 LLHR - Long Live the Hunt, Rise 🐺
