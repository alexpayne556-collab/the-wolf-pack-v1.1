# 🧠 WOLF PACK SYSTEM ARCHITECTURE
**The Complete Picture: How All Pieces Connect**

**Date:** January 28, 2026  
**Status:** Intelligence Built, Infrastructure Needed  
**Purpose:** Understand the WHOLE system before building

---

## 🎯 THE VISION

A 24/7 trading companion that:
1. **SEES** the market (live data from multiple sources)
2. **THINKS** about relationships (earnings → positions, people → signals)
3. **LEARNS** from every trade (patterns, win rates, what works for US)
4. **ALERTS** you when it finds something (A+ setups, thesis breaks)
5. **REMEMBERS** everything (every trade, every lesson, permanent memory)

**The wolf that never sleeps, never forgets, and always improves.**

---

## 📊 SYSTEM LAYERS (Top to Bottom)

```
┌─────────────────────────────────────────────────────────────┐
│  INTELLIGENCE LAYER (The Brain's Knowledge)                 │
│  - brain_config.json (205 tickers, watchlists, rules)      │
│  - influence_map.json (how events affect positions)         │
│  - brain_methodology.json (how to think & research)         │
│  - position_management.json (when to add/hold/cut)          │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│  REASONING LAYER (The Brain's Thoughts)                     │
│  - fenrir_thinking_engine.py (connects dots, reasons)       │
│  - Loads intelligence configs                                │
│  - Generates thoughts with confidence scores                 │
│  - Logs reasoning chains to database                         │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│  DATA LAYER (The Brain's Senses)                            │
│  - Finnhub API (real-time quotes, news, insider)            │
│  - yfinance (volume, historical)                             │
│  - Polygon (backup quotes)                                   │
│  - NewsAPI (catalyst detection)                              │
│  - SEC EDGAR (Form 4, 8-K filings)                          │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│  MONITORING LAYER (The Brain's Awareness)                   │
│  - autonomous_wolf_brain.py (THE SCANNER - NEEDS FIXING)    │
│  - overnight_scan.py (after-hours movers)                   │
│  - Continuous monitoring loop                                │
│  - Volume spike detection                                    │
│  - Price alert system                                        │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│  EXECUTION LAYER (The Brain's Actions)                      │
│  - Alpaca Paper Trading API                                  │
│  - execute_with_stops.py (order placement with stops)       │
│  - sync_portfolio_to_alpaca.py (mirror real → paper)        │
│  - Order validation & risk checks                            │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│  MEMORY LAYER (The Brain's Experience)                      │
│  - wolfpack.db (trades, journal, brain_thoughts)            │
│  - daily_journal.py (logging tool)                          │
│  - integrate_session_to_brain.py (session → DB)             │
│  - THE_LEONARD_FILE.md (narrative history)                  │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│  INTERFACE LAYER (The Brain's Communication)                │
│  - Discord webhooks (alerts)                                 │
│  - wolfpack_heatmap_v2.html (visual dashboard)              │
│  - Daily summaries to Leonard File                           │
│  - SMS alerts (urgent)                                       │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔗 DATA FLOW: How Information Moves

### MORNING ROUTINE (Pre-Market 7-9:30 AM ET)
```
1. overnight_scan.py runs
   ↓
2. Checks AH movers from previous night
   ↓
3. Queries Finnhub for pre-market activity
   ↓
4. fenrir_thinking_engine analyzes:
   - Any earnings that happened?
   - Any news on our positions?
   - Any macro events (FOMC, etc.)?
   ↓
5. Generates thoughts with reasoning chains
   ↓
6. Logs to brain_thoughts table in wolfpack.db
   ↓
7. Alerts you via Discord: "Pre-market summary"
```

### MARKET HOURS (9:30 AM - 4:00 PM ET)
```
1. autonomous_wolf_brain.py monitors (WHEN FIXED)
   ↓
2. Every 5 minutes:
   - Check all positions (price, volume)
   - Scan watchlists for volume spikes
   - Check news for catalysts
   ↓
3. When volume spike detected (1.5x+):
   - Fetch news from Finnhub/NewsAPI
   - Check SEC for Form 4/8-K
   - fenrir_thinking_engine reasons about it
   ↓
4. If convergence ≥50 + thesis exists:
   - Generate alert: "A+ setup: TICKER"
   - Reasoning chain included
   ↓
5. If position thesis breaks:
   - Generate alert: "THESIS BREAK: TICKER - cut immediately"
   ↓
6. All thoughts logged to database
```

### AFTER CLOSE (4:00-6:00 PM ET)
```
1. Check earnings calendar (BiopharmCatalyst for biotech)
   ↓
2. When earnings drop (MSFT, META, TSLA, etc.):
   - fenrir_thinking_engine.think_about_earnings()
   - "MSFT beat" → "Affects MU" → reasoning chain
   ↓
3. Check after-hours movers (StockAnalysis.com)
   ↓
4. Generate evening summary
   ↓
5. Log to Leonard File
   ↓
6. Alert: "Evening summary ready"
```

### OVERNIGHT (6:00 PM - 7:00 AM ET)
```
1. Monitor futures (ES, NQ)
   ↓
2. Check international markets (Asia/Europe)
   ↓
3. Scan news for overnight developments
   ↓
4. Generate pre-market prep for morning
```

---

## 📁 FILE INVENTORY & PURPOSE

### INTELLIGENCE (Brain's Knowledge) ✅
| File | Purpose | Status |
|------|---------|--------|
| `brain_config.json` | 205 tickers, watchlists, data sources, rules | ✅ Complete |
| `influence_map.json` | Earnings/macro/people influence relationships | ✅ Complete |
| `brain_methodology.json` | How to think, research, learn | ✅ Complete |
| `position_management.json` | When to add/hold/cut with context | ✅ Complete |

### REASONING (Brain's Thoughts) ⚠️
| File | Purpose | Status |
|------|---------|--------|
| `fenrir_thinking_engine.py` | Core reasoning engine | ✅ Working (bugs fixed) |
| `autonomous_wolf_brain.py` | Main scanner/monitor | ❌ CRASHES - high RAM usage |
| `lightweight_researcher.py` | Focused research on one ticker | ⚠️ Exists, needs testing |

### DATA SOURCES (Brain's Senses) ⚠️
| API | Purpose | Rate Limit | Status |
|-----|---------|-----------|--------|
| Finnhub | Real-time quotes, news, insider | 60/min | ✅ Key works |
| yfinance | Volume, historical data | Unlimited | ✅ Library installed |
| Polygon | Backup quotes | 5/min free | ✅ Key works |
| NewsAPI | News aggregation | 100/day | ✅ Key works |
| Alpaca Paper | Paper trading execution | Varies | ⚠️ 403 from cloud |
| SEC EDGAR | Form 4, 8-K filings | None | ✅ Free, no key |

### MONITORING (Brain's Awareness) ❌
| File | Purpose | Status |
|------|---------|--------|
| `autonomous_wolf_brain.py` | Main 24/7 monitor | ❌ Crashes, needs major fixes |
| `overnight_scan.py` | After-hours scanner | ⚠️ Exists, needs testing |
| `wolf_brain_4am.bat` | Windows scheduler | ⚠️ Exists, needs monitoring code |
| `setup_4am_scheduler.ps1` | Schedule setup | ⚠️ Exists, needs monitoring code |

### EXECUTION (Brain's Actions) ⚠️
| File | Purpose | Status |
|------|---------|--------|
| `execute_with_stops.py` | Place orders with stop losses | ⚠️ Exists, needs testing |
| `sync_portfolio_to_alpaca.py` | Mirror real → paper | ✅ Working, 8/8 synced |
| `test_paper_trades.py` | Test order placement | ⚠️ Exists, needs testing |
| `test_order_execution.py` | Test execution logic | ⚠️ Exists, needs testing |

### MEMORY (Brain's Experience) ✅
| File | Purpose | Status |
|------|---------|--------|
| `wolfpack.db` | SQLite database (trades, journal, thoughts) | ✅ Schema exists, 16 trades |
| `daily_journal.py` | Manual trade logging | ✅ Working |
| `integrate_session_to_brain.py` | Session → DB | ✅ Working |
| `log_overnight_session.py` | Bulk logging | ✅ Working |
| `THE_LEONARD_FILE.md` | Narrative history | ✅ v11.2, complete |
| `check_db.py` | Database inspection | ✅ Working |
| `check_trades.py` | Trade history viewer | ✅ Working |

### INTERFACE (Brain's Communication) ❌
| File | Purpose | Status |
|------|---------|--------|
| Discord webhooks | Alerts | ❌ Not implemented |
| `wolfpack_heatmap_v2.html` | Visual dashboard | ⚠️ Prototype, CORS issues |
| SMS alerts | Urgent notifications | ❌ Not implemented |

### TESTING & VALIDATION ⚠️
| File | Purpose | Status |
|------|---------|--------|
| `test_full_system.py` | End-to-end test | ⚠️ Exists, needs update |
| `test_upgraded_brain.py` | Brain DB integration test | ⚠️ Exists, needs testing |
| `validate_brain.py` | Config validation | ⚠️ Exists, needs testing |
| `truth_check.py` | Reality check | ⚠️ Exists, needs testing |

### DOCUMENTATION 📚
| File | Purpose | Status |
|------|---------|--------|
| `DEPLOYMENT_READINESS.md` | Honest deployment assessment | ✅ Created tonight |
| `THE_COMPLETE_WOLF_PACK_INTELLIGENCE.md` | Collective intelligence | ✅ Created tonight |
| `BR0KKR_DAILY_WORKFLOW.md` | Daily routine | ✅ Complete |
| `BRAIN_INTELLIGENCE_MASTER.md` | System intelligence overview | ✅ Complete |
| `SYSTEM_OVERVIEW_SIMPLE.md` | Simple system explanation | ✅ Complete |

---

## 🔴 CRITICAL BOTTLENECKS

### 1. **autonomous_wolf_brain.py - THE MAIN SCANNER**
**Problem:** Tries to scan 200+ tickers simultaneously → crashes computer

**Why it crashes:**
```python
# Current approach (WRONG):
for ticker in all_205_tickers:
    fetch_quote(ticker)      # 205 API calls at once
    fetch_volume(ticker)     # Another 205 calls
    fetch_news(ticker)       # Another 205 calls
# = 615+ API calls in seconds = CRASH
```

**What it needs:**
```python
# Proper approach (RIGHT):
ticker_queue = Queue(all_205_tickers)
rate_limiter = RateLimiter(60 calls per minute for Finnhub)

while ticker_queue.not_empty():
    if rate_limiter.can_call():
        ticker = ticker_queue.pop()
        fetch_quote(ticker)
        rate_limiter.record_call()
    else:
        sleep(1)  # Wait for rate limit window
```

**Also needs:**
- Batch processing (20 tickers at a time, not all 205)
- Priority tiers (check MY_POSITIONS every 5 min, check SPECULATIVE_MOVERS every 30 min)
- Memory management (cache results, don't refetch)
- Error handling (if Finnhub fails, fall back to yfinance)

### 2. **No Integration Between Components**
**Problem:** We have smart pieces that don't talk to each other

**Example:**
- `fenrir_thinking_engine.py` can reason about MSFT earnings
- But it never gets CALLED by the monitoring system
- `autonomous_wolf_brain.py` scans for volume spikes
- But doesn't use `fenrir_thinking_engine` to reason about them

**What's needed:**
```python
class WolfPackBrain:
    def __init__(self):
        self.config = load_brain_config()
        self.influence_map = load_influence_map()
        self.thinking_engine = FenrirThinkingEngine()
        self.data_fetcher = DataFetcher()  # Needs to be built
        self.alerter = Alerter()  # Needs to be built
    
    def monitor_positions(self):
        # Get current positions from config
        positions = self.config.get_my_positions()
        
        for ticker in positions:
            # Fetch data
            quote = self.data_fetcher.get_quote(ticker)
            volume = self.data_fetcher.get_volume(ticker)
            
            # Reason about it
            if volume > 1.5x:
                thoughts = self.thinking_engine.analyze_volume_spike(ticker)
                
                # Alert if important
                if thoughts.confidence > 70:
                    self.alerter.send(thoughts)
            
            # Log to database
            self.db.log_price_check(ticker, quote, volume)
```

### 3. **No Alert System**
**Problem:** Brain can think but can't tell you

**What's needed:**
```python
class Alerter:
    def __init__(self):
        self.discord_webhook = os.getenv("DISCORD_WEBHOOK")
        self.twilio_client = Twilio(...)
    
    def send(self, thought):
        if thought.priority == "URGENT":
            # MRNO hit stop loss, NTLA thesis broken
            self.send_sms(thought)
            self.send_discord(thought)
        elif thought.priority == "HIGH":
            # MSFT earnings beat, MU thesis confirmed
            self.send_discord(thought)
        else:
            # General market observation
            self.log_to_leonard_file(thought)
```

---

## 🏗️ ARCHITECTURE COMPONENTS STATUS

| Component | Purpose | Exists? | Works? | Production Ready? |
|-----------|---------|---------|--------|-------------------|
| **Intelligence Configs** | Brain's knowledge | ✅ Yes | ✅ Yes | ✅ Yes |
| **Reasoning Engine** | Brain's thoughts | ✅ Yes | ✅ Yes (bugs fixed) | ✅ Yes |
| **Data Fetcher** | Brain's senses | ⚠️ Partial | ❌ No | ❌ No rate limiting |
| **Monitor Loop** | Brain's awareness | ⚠️ Exists | ❌ Crashes | ❌ Needs major fixes |
| **Integration Layer** | Connect components | ❌ No | ❌ No | ❌ Doesn't exist |
| **Alert System** | Brain's communication | ❌ No | ❌ No | ❌ Doesn't exist |
| **Database** | Brain's memory | ✅ Yes | ✅ Yes | ⚠️ Needs testing |
| **Dashboard** | Visual interface | ⚠️ Prototype | ⚠️ Partial | ❌ CORS issues |
| **Cloud Infrastructure** | 24/7 hosting | ❌ No | ❌ No | ❌ Nothing deployed |

---

## 📈 THE DEVELOPMENT ROADMAP

### PHASE 1: FIX THE SCANNER (Week 1-2)
**Goal:** autonomous_wolf_brain.py doesn't crash

**Tasks:**
1. Add rate limiting to all API calls
2. Implement ticker queue with priorities
3. Add memory management
4. Add error handling & fallbacks
5. Test with 20 tickers first, then scale

**Success metric:** Runs for 24 hours without crashing

### PHASE 2: BUILD INTEGRATION (Week 3-4)
**Goal:** Components work together

**Tasks:**
1. Create unified WolfPackBrain class
2. Connect thinking_engine to scanner
3. Add alert system (Discord minimum)
4. Test end-to-end: scan → reason → alert

**Success metric:** Volume spike detected → reasoned about → alert sent

### PHASE 3: DEPLOY TO CLOUD (Week 5-6)
**Goal:** Runs 24/7 independently

**Tasks:**
1. Set up cloud server (Railway/DigitalOcean)
2. Deploy code
3. Set up monitoring & logging
4. Test stability

**Success metric:** Runs 7 days straight without intervention

### PHASE 4: BUILD LEARNING (Month 2-3)
**Goal:** System learns from trades

**Tasks:**
1. Trade outcome analyzer
2. Pattern detector
3. Win/loss analytics
4. Rule refinement

**Success metric:** Can show "thesis trades win 85.7%, momentum trades win X%"

### PHASE 5: PROVE EDGE (Month 4-12)
**Goal:** Track record that's investable

**Tasks:**
1. Trade daily with system
2. Log everything
3. Document track record
4. Refine based on results

**Success metric:** Positive returns over 6 months minimum

---

## 💾 DATABASE SCHEMA (wolfpack.db)

```sql
-- Current tables
trades (
    id, ticker, entry_date, entry_price, shares,
    exit_date, exit_price, gain_loss, thesis, catalyst
)

journal_entries (
    id, timestamp, entry_type, content, mood,
    trades_made, market_context
)

brain_context (
    id, timestamp, context_type, content
)

brain_thoughts (
    id, timestamp, thought_type, trigger,
    reasoning_chain, affected_positions,
    confidence, action_suggested, thought_json
)

-- Needed tables (not yet created)
position_checks (
    id, timestamp, ticker, price, volume,
    volume_avg, spike_detected
)

alerts_sent (
    id, timestamp, alert_type, ticker,
    message, priority, channel
)

api_calls_log (
    id, timestamp, api_name, endpoint,
    success, response_time, error
)
```

---

## 🔄 DATA CONNECTIONS

### How Configs → Code
```
brain_config.json
    ↓
fenrir_thinking_engine.py loads it
    ↓
_get_my_positions() returns ["MU", "RCAT", ...]
    ↓
autonomous_wolf_brain.py uses position list
    ↓
Monitors only those tickers with priority
```

### How Data → Thoughts → Alerts
```
Finnhub API call: MU volume 2.8x avg
    ↓
autonomous_wolf_brain detects spike
    ↓
Calls fenrir_thinking_engine.analyze_volume_spike("MU")
    ↓
Engine checks: Is there news? Recent earnings? Insider buying?
    ↓
Generates Thought object with reasoning chain
    ↓
Logs to brain_thoughts table
    ↓
If confidence ≥70%, send alert via Discord
```

### How Trades → Learning
```
daily_journal.py: Log NTLA loss (-11%)
    ↓
Saves to journal_entries table
    ↓
trade_analyzer.py (needs to be built) reads entries
    ↓
Compares: trades with thesis vs trades without
    ↓
Calculates: "Thesis trades: 85.7% win, No-thesis: 0% win"
    ↓
Updates brain_methodology.json: "NEVER trade without thesis"
    ↓
Brain learns rule permanently
```

---

## 🎯 THE UNIFIED VISION

Imagine this working end-to-end:

**6:00 AM ET:**
- overnight_scan.py wakes up
- Checks: MSFT, META, TSLA all beat earnings last night
- fenrir_thinking_engine reasons: "All three → AI infrastructure strength → MU thesis confirmed"
- Discord alert: "🐺 Morning Brief: Tech earnings bullish. MU thesis validated. Confidence: 82%"

**9:45 AM ET:**
- autonomous_wolf_brain monitoring
- Detects: RDW volume spike (2.3x avg)
- Fetches news: "Pentagon contract announced"
- Reasoning: "Defense contract = thesis catalyst. Entry criteria met."
- Discord alert: "🔥 A+ Setup: RDW - Pentagon contract, volume 2.3x, convergence 78"

**2:00 PM ET:**
- FOMC decision announced: Hold
- fenrir_thinking_engine.think_about_macro_event("FOMC", {"decision": "hold", "powell_tone": "neutral"})
- Reasoning: "Neutral tone. Biotech safe. Defense unaffected. Uranium uncorrelated."
- Discord alert: "📊 FOMC: Neutral. Portfolio impact: minimal. Hold positions."

**4:30 PM ET:**
- MRNO closing below $1.80
- position_management.json rules: "Below $1.80 = CUT"
- Alert: "🚨 MRNO hit stop rule ($1.79). Cut at open tomorrow."

**Evening:**
- Daily summary generated
- Logged to Leonard File
- Performance metrics updated
- Tomorrow's plan created

**Every night:**
- Brain learns from the day's trades
- Updates win/loss ratios
- Refines rules based on what actually worked
- Gets smarter

---

## 🧩 MISSING PIECES TO BUILD

### 1. **DataFetcher class** (API wrapper with rate limiting)
```python
class DataFetcher:
    def get_quote(ticker) → price, volume, change
    def get_news(ticker) → list of recent news
    def get_insider(ticker) → recent Form 4s
    def get_sec_filing(ticker) → recent 8-Ks
    
    # With rate limiting, caching, fallbacks
```

### 2. **Alerter class** (Discord, SMS, email)
```python
class Alerter:
    def send_discord(message, priority)
    def send_sms(message) for urgent
    def log_to_leonard(message) for history
```

### 3. **TradeAnalyzer class** (learning engine)
```python
class TradeAnalyzer:
    def analyze_outcome(trade)
    def find_patterns()
    def calculate_ratios()
    def suggest_rule_changes()
```

### 4. **WolfPackBrain class** (orchestrator)
```python
class WolfPackBrain:
    # Loads all configs
    # Manages all components
    # Coordinates data flow
    # Runs monitoring loop
```

---

## 📊 SUMMARY

**What we have:**
- BRILLIANT intelligence layer (brain configs)
- WORKING reasoning engine (fenrir_thinking_engine.py)
- COMPLETE methodology (how to think/trade)
- SOLID database structure (wolfpack.db)
- TESTED API keys (all work except Alpaca from cloud)

**What we need:**
- FIX the scanner (autonomous_wolf_brain.py crashes)
- BUILD integration layer (components don't talk)
- BUILD alert system (brain can't communicate)
- BUILD learning engine (brain doesn't learn yet)
- DEPLOY to cloud (runs 24/7)

**Timeline estimate:**
- Basic working system: 4-6 weeks
- Learning system: 2-3 months
- Proven track record: 6-12 months

**The good news:**
The HARD part (intelligence, reasoning, methodology) is DONE.
The remaining work is plumbing - tedious but straightforward.

**The wolf pack way:**
We don't rush. We build right. We prove it works. Then we scale.

---

**AWOOOO 🐺**
